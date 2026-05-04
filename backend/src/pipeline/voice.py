"""
语音合成模块

将脚本文字转为配音：
- 情绪感知语音合成
- 多角色不同音色
- Edge-TTS / ElevenLabs 双引擎
"""

import asyncio
from pathlib import Path
from typing import Optional

import edge_tts

from ..config import settings
from .adapter import AdaptedScript, ScriptLine


class VoiceSynthesizer:
    """语音合成器"""

    # 中文 TTS 音色预设
    VOICE_PRESETS = {
        "zh-CN-XiaoxiaoNeural": {"gender": "Female", "style": "活泼少女"},
        "zh-CN-YunxiNeural": {"gender": "Male", "style": "沉稳青年"},
        "zh-CN-YunyangNeural": {"gender": "Male", "style": "新闻播音"},
        "zh-CN-XiaoyiNeural": {"gender": "Female", "style": "软萌少女"},
        "zh-CN-YunjianNeural": {"gender": "Male", "style": "阳光少年"},
        "zh-CN-XiaochenNeural": {"gender": "Female", "style": "温柔御姐"},
    }

    def __init__(self):
        self.output_dir = settings.output_dir / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def synthesize_script(
        self,
        script: AdaptedScript,
        output_dir: Optional[Path] = None,
    ) -> list[dict]:
        """
        为整个脚本生成配音

        Returns:
            [{line_index, speaker, audio_path, duration}]
        """
        out_dir = output_dir or self.output_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        tasks = []
        for i, line in enumerate(script.lines):
            voice = self._get_voice_for_character(line.speaker, script.characters)
            audio_path = out_dir / f"line_{i:03d}_{line.speaker}.mp3"
            tasks.append(self._synthesize_line(line, voice, audio_path, i))

        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    def _get_voice_for_character(self, speaker: str, characters: list[dict]) -> str:
        """根据角色获取音色"""
        for char in characters:
            if char["name"] == speaker:
                return char.get("voice", settings.tts_voice)
            # 处理 "狸花猫2号" 这类变体
            if speaker.startswith(char["name"]):
                alt_voices = ["zh-CN-YunxiNeural", "zh-CN-YunjianNeural", "zh-CN-XiaochenNeural"]
                idx = characters.index(char)
                return alt_voices[idx % len(alt_voices)]
        return settings.tts_voice

    async def _synthesize_line(
        self, line: ScriptLine, voice: str, output_path: Path, index: int
    ) -> Optional[dict]:
        """合成单行台词"""
        if output_path.exists():
            # 获取时长
            duration = await self._get_audio_duration(output_path)
            return {"line_index": index, "speaker": line.speaker,
                    "audio_path": output_path, "duration": duration}

        # 根据情绪调整语速和音调
        rate, pitch = self._emotion_to_tts_params(line.emotion)

        try:
            if settings.tts_provider == "edge":
                return await self._edge_tts(line.text, voice, rate, pitch, output_path, index, line.speaker)
            else:
                return await self._openai_tts(line.text, voice, output_path, index, line.speaker)
        except Exception as e:
            print(f"TTS error for line {index}: {e}")
            return None

    def _emotion_to_tts_params(self, emotion: str) -> tuple[str, str]:
        """情绪映射到 TTS 参数"""
        emotion_params = {
            "happy": ("+15%", "+5Hz"),
            "sad": ("-15%", "-10Hz"),
            "funny": ("+10%", "+10Hz"),
            "serious": ("-5%", "-5Hz"),
            "surprised": ("+20%", "+15Hz"),
            "angry": ("+10%", "+20Hz"),
            "neutral": ("+0%", "+0Hz"),
        }
        return emotion_params.get(emotion, ("+0%", "+0Hz"))

    async def _edge_tts(
        self, text: str, voice: str, rate: str, pitch: str,
        output_path: Path, index: int, speaker: str,
    ) -> dict:
        """Edge TTS 合成"""
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )
        await communicate.save(str(output_path))

        duration = await self._get_audio_duration(output_path)
        return {
            "line_index": index,
            "speaker": speaker,
            "audio_path": output_path,
            "duration": duration,
        }

    async def _openai_tts(
        self, text: str, voice: str, output_path: Path, index: int, speaker: str,
    ) -> dict:
        """OpenAI TTS 合成"""
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=settings.llm_api_key or "not-needed",
            base_url=settings.llm_base_url,
        )

        # 映射到 OpenAI 音色
        openai_voices = {"zh-CN-XiaoxiaoNeural": "nova", "zh-CN-YunxiNeural": "onyx"}
        oai_voice = openai_voices.get(voice, "alloy")

        async with client as c:
            resp = await c.audio.speech.create(
                model="tts-1",
                voice=oai_voice,
                input=text,
                speed=1.0,
            )
            resp.stream_to_file(str(output_path))

        duration = await self._get_audio_duration(output_path)
        return {
            "line_index": index,
            "speaker": speaker,
            "audio_path": output_path,
            "duration": duration,
        }

    async def _get_audio_duration(self, audio_path: Path) -> float:
        """获取音频时长"""
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        try:
            return float(stdout.decode().strip())
        except (ValueError, AttributeError):
            return 1.0
