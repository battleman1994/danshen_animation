"""
内容提取模块

负责从各种来源提取内容：
- 视频链接 → 下载 + 音频转写
- 图片 → OCR + 视觉理解
- 网页链接 → 抓取 + 摘要
- 纯文本 → 直接使用
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import httpx
from openai import AsyncOpenAI

from ..config import settings


@dataclass
class ExtractedContent:
    """提取后的内容"""
    text: str                       # 主要文本内容
    source_type: str                # douyin_video, image, web_link, text
    source_url: Optional[str] = None
    title: Optional[str] = None
    speakers: Optional[list[dict]] = None  # 对话者信息 [{role, text, emotion}]
    emotion: str = "neutral"        # happy, sad, funny, serious, neutral
    keywords: list[str] = None      # 关键词
    raw_audio_path: Optional[Path] = None
    raw_video_path: Optional[Path] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class ContentExtractor:
    """内容提取器"""

    def __init__(self):
        self.llm = AsyncOpenAI(
            api_key=settings.llm_api_key or "not-needed",
            base_url=settings.llm_base_url,
        )

    async def extract(self, source: str, source_type: str) -> ExtractedContent:
        """根据来源类型提取内容"""
        extractors = {
            "douyin_video": self._from_douyin,
            "bilibili_video": self._from_bilibili,
            "youtube_video": self._from_youtube,
            "image": self._from_image,
            "web_link": self._from_web_link,
            "text": self._from_text,
            "weibo_post": self._from_weibo,
        }
        handler = extractors.get(source_type, self._from_text)
        return await handler(source)

    async def _from_douyin(self, url: str) -> ExtractedContent:
        """从抖音视频提取内容"""
        # 1. 用 yt-dlp 下载视频
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            video_path = tmp / "input.mp4"
            audio_path = tmp / "audio.wav"

            # 下载
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp", "-f", "best", "-o", str(video_path), url,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()

            # 提取音频
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", str(video_path), "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1", str(audio_path), "-y",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()

            # 2. Whisper 转写
            text, speakers = await self._transcribe_with_speakers(audio_path)

            # 3. LLM 分析情绪和关键词
            analysis = await self._analyze_content(text)

            return ExtractedContent(
                text=text,
                source_type="douyin_video",
                source_url=url,
                speakers=speakers,
                emotion=analysis.get("emotion", "neutral"),
                keywords=analysis.get("keywords", []),
                raw_video_path=video_path,
            )

    async def _from_image(self, image_path: str) -> ExtractedContent:
        """从图片提取内容（OCR + 视觉理解）"""
        # TODO: 集成 OCR 和视觉模型
        text = f"[图片内容: {image_path}]"
        return ExtractedContent(
            text=text,
            source_type="image",
        )

    async def _from_web_link(self, url: str) -> ExtractedContent:
        """从网页链接提取内容"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, follow_redirects=True, timeout=30)
            html = resp.text

        # 简化的内容提取（生产环境可用 trafilatura 或 readability）
        title = ""
        text = html[:5000]  # 简化处理

        # LLM 摘要
        analysis = await self._analyze_content(text)

        return ExtractedContent(
            text=text,
            source_type="web_link",
            source_url=url,
            title=title,
            emotion=analysis.get("emotion", "neutral"),
            keywords=analysis.get("keywords", []),
        )

    async def _from_youtube(self, url: str) -> ExtractedContent:
        """从 YouTube 提取"""
        return await self._from_douyin(url)  # 复用相同逻辑

    async def _from_bilibili(self, url: str) -> ExtractedContent:
        """从 B站 提取"""
        return await self._from_douyin(url)

    async def _from_text(self, text: str) -> ExtractedContent:
        """直接使用文字"""
        analysis = await self._analyze_content(text)
        return ExtractedContent(
            text=text,
            source_type="text",
            emotion=analysis.get("emotion", "neutral"),
            keywords=analysis.get("keywords", []),
        )

    async def _from_weibo(self, url: str) -> ExtractedContent:
        """从微博提取"""
        return await self._from_web_link(url)

    async def _transcribe_with_speakers(self, audio_path: Path) -> tuple[str, list[dict]]:
        """Whisper 转写 + 说话人分离"""
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel(
                settings.whisper_model,
                device=settings.whisper_device,
                compute_type="int8",
            )
            segments, info = model.transcribe(str(audio_path), beam_size=5, language="zh")
            text = " ".join(seg.text for seg in segments)
            # TODO: 集成说话人分离 (pyannote-audio)
            return text, []
        except ImportError:
            return "[需要安装 faster-whisper]", []

    async def _analyze_content(self, text: str) -> dict:
        """LLM 分析内容情绪和关键词"""
        if len(text) > 3000:
            text = text[:3000]

        try:
            resp = await self.llm.chat.completions.create(
                model=settings.llm_model,
                messages=[{
                    "role": "system",
                    "content": "分析以下内容，返回 JSON：{emotion: happy|sad|funny|serious|neutral, keywords: [关键词列表], summary: 简短摘要}"
                }, {
                    "role": "user",
                    "content": text
                }],
                temperature=0.3,
                max_tokens=300,
            )
            import json
            result = json.loads(resp.choices[0].message.content)
            return result
        except Exception:
            return {"emotion": "neutral", "keywords": [], "summary": ""}
