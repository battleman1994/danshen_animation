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
    source_type: str                # douyin_video, image, web_link, text, news
    source_url: Optional[str] = None
    title: Optional[str] = None
    speakers: Optional[list[dict]] = None  # 对话者信息 [{role, text, emotion, start_time, end_time}]
    emotion: str = "neutral"        # happy, sad, funny, serious, neutral
    keywords: list[str] = None      # 关键词
    raw_audio_path: Optional[Path] = None
    raw_video_path: Optional[Path] = None
    news_analysis: Optional[dict] = None  # 新闻分析结果（仅 news 类型）

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
            "news": self._from_news,
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
        """从网页链接提取内容（使用 trafilatura 高质量提取）"""
        title = ""
        text = ""

        # 优先使用 trafilatura 进行高质量内容提取
        try:
            import trafilatura
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                result = trafilatura.extract(
                    downloaded,
                    include_links=False,
                    include_images=False,
                    include_tables=True,
                    output_format="markdown",
                )
                if result:
                    text = result
                    # 尝试提取标题
                    metadata = trafilatura.extract(
                        downloaded,
                        output_format="json",
                        include_links=False,
                    )
                    if metadata:
                        import json as _json
                        try:
                            meta = _json.loads(metadata)
                            title = meta.get("title", "")
                        except Exception:
                            pass
        except ImportError:
            pass

        # 回退到 httpx 直接抓取
        if not text:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        url,
                        follow_redirects=True,
                        timeout=30,
                        headers={
                            "User-Agent": (
                                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/120.0.0.0 Safari/537.36"
                            ),
                        },
                    )
                    html = resp.text
                    # 简单去标签
                    import re
                    text = re.sub(r"<[^>]+>", " ", html)
                    text = re.sub(r"\s+", " ", text).strip()
            except Exception:
                text = f"[无法访问: {url}]"

        # LLM 分析
        analysis = await self._analyze_content(text[:3000])

        return ExtractedContent(
            text=text[:5000],
            source_type="web_link",
            source_url=url,
            title=title or analysis.get("summary", ""),
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

    async def _from_news(self, source: str) -> ExtractedContent:
        """处理新闻内容（URL 或文字）"""
        from .news_analyzer import NewsAnalyzer

        # 如果是 URL，先抓取内容
        if source.startswith("http"):
            async with httpx.AsyncClient() as client:
                resp = await client.get(source, follow_redirects=True, timeout=30)
                html = resp.text
                # 简化内容提取
                text = html[:5000]
        else:
            text = source

        # 新闻分析
        analyzer = NewsAnalyzer()
        analysis = await analyzer.analyze(text, source if source.startswith("http") else None)

        return ExtractedContent(
            text=text,
            source_type="news",
            source_url=source if source.startswith("http") else None,
            title=analysis.title,
            emotion=analysis.emotion,
            keywords=analysis.keywords,
            news_analysis={
                "category": analysis.category,
                "severity": analysis.severity,
                "suggested_character": analysis.suggested_character,
                "broadcast_style": analysis.broadcast_style,
                "summary": analysis.summary,
                "read_time": analysis.read_time,
                "data_points": analysis.data_points,
            },
        )

    async def _transcribe_with_speakers(self, audio_path: Path) -> tuple[str, list[dict]]:
        """Whisper 转写 + 说话人分离（基于时间戳的简单切分）"""
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel(
                settings.whisper_model,
                device=settings.whisper_device,
                compute_type="int8",
            )
            segments, info = model.transcribe(str(audio_path), beam_size=5, language="zh")

            full_text_parts = []
            speaker_segments = []
            current_speaker = 0
            speaker_counter = 0
            last_end = 0.0

            for seg in segments:
                gap = seg.start - last_end
                if gap > 0.5 and last_end > 0:
                    speaker_counter += 1
                    current_speaker = speaker_counter % 2

                speaker_name = "角色A" if current_speaker == 0 else "角色B"
                full_text_parts.append(seg.text)
                speaker_segments.append({
                    "role": speaker_name,
                    "text": seg.text.strip(),
                    "emotion": "neutral",
                    "start_time": seg.start,
                    "end_time": seg.end,
                })
                last_end = seg.end

            full_text = " ".join(full_text_parts)
            return full_text, speaker_segments
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
