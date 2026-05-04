"""
视频合成模块

将角色图片 + 配音 + 字幕组合成最终视频：
- FFmpeg 视频合成
- 口型同步（可选）
- 字幕叠加
- 场景转场
"""

import asyncio
import math
from pathlib import Path
from typing import Optional

from ..config import settings


class VideoComposer:
    """视频合成器"""

    def __init__(self):
        self.output_dir = settings.output_dir / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def compose(
        self,
        task_id: str,
        character_images: dict[str, Path],
        background_path: Optional[Path],
        audio_segments: list[dict],
        subtitle_lines: list[dict],
        resolution: str = "1080p",
    ) -> Path:
        """
        合成最终视频

        Args:
            task_id: 任务 ID
            character_images: {emotion: image_path}
            background_path: 背景图路径
            audio_segments: [{line_index, speaker, audio_path, duration}]
            subtitle_lines: [{text, start_time, end_time}]
            resolution: 输出分辨率

        Returns:
            最终视频路径
        """
        output_path = self.output_dir / f"{task_id}.mp4"

        # 1. 准备所有片段
        segments = await self._prepare_segments(
            character_images, background_path, audio_segments
        )

        # 2. 用 FFmpeg 合成
        await self._ffmpeg_compose(segments, subtitle_lines, resolution, output_path)

        return output_path

    async def _prepare_segments(
        self,
        character_images: dict[str, Path],
        background_path: Optional[Path],
        audio_segments: list[dict],
    ) -> list[dict]:
        """准备视频片段"""
        segments = []

        for seg in audio_segments:
            duration = seg.get("duration", 2.0)
            character_img = character_images.get("neutral",
                next(iter(character_images.values())) if character_images else None)

            segments.append({
                "character_image": str(character_img) if character_img else None,
                "background_image": str(background_path) if background_path else None,
                "audio_path": str(seg["audio_path"]),
                "duration": duration,
                "speaker": seg.get("speaker", ""),
            })

        return segments

    async def _ffmpeg_compose(
        self,
        segments: list[dict],
        subtitle_lines: list[dict],
        resolution: str,
        output_path: Path,
    ):
        """FFmpeg 合成"""
        res_map = {"720p": (1280, 720), "1080p": (1920, 1080)}
        width, height = res_map.get(resolution, (1920, 1080))

        # 构建 FFmpeg filter_complex
        filter_parts = []
        concat_inputs = []

        for i, seg in enumerate(segments):
            duration = seg["duration"]
            char_img = seg.get("character_image")

            if char_img and Path(char_img).exists():
                # 角色图 + 背景图叠加
                filter_parts.append(
                    f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                    f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:white,"
                    f"setsar=1[v{i}]"
                )
                concat_inputs.append(f"[v{i}]")
            else:
                # 纯色背景
                color = self._speaker_color(seg.get("speaker", ""))
                filter_parts.append(
                    f"color=c={color}:s={width}x{height}:d={duration}:r=30,"
                    f"setsar=1[v{i}]"
                )
                concat_inputs.append(f"[v{i}]")

        # 拼接所有视频片段
        filter_parts.append(
            f"{''.join(concat_inputs)}concat=n={len(segments)}:v=1:a=0[outv]"
        )

        filter_complex = ";".join(filter_parts)

        # 构建 FFmpeg 命令
        cmd = ["ffmpeg", "-y"]

        # 输入文件
        for seg in segments:
            char_img = seg.get("character_image")
            if char_img and Path(char_img).exists():
                cmd.extend(["-loop", "1", "-t", str(seg["duration"]),
                           "-i", char_img])
            else:
                cmd.extend(["-f", "lavfi",
                           "-i", f"color=c=white:s={width}x{height}:d={seg['duration']}:r=30"])

        # 音频输入
        for seg in segments:
            cmd.extend(["-i", seg["audio_path"]])

        # 滤镜
        cmd.extend(["-filter_complex", filter_complex])
        cmd.extend(["-map", "[outv]"])

        # 混音所有音轨
        audio_inputs = "".join(f"[{len(segments) + i}:a]" for i in range(len(segments)))
        cmd.extend(["-filter_complex", f"{audio_inputs}concat=n={len(segments)}:v=0:a=1[outa]"])
        cmd.extend(["-map", "[outa]"])

        # 编码参数
        cmd.extend([
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(output_path),
        ])

        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")

        # 如果有字幕，叠加字幕
        if subtitle_lines:
            await self._overlay_subtitles(output_path, subtitle_lines)

    async def _overlay_subtitles(self, video_path: Path, subtitle_lines: list[dict]):
        """叠加字幕"""
        # 生成 SRT 字幕文件
        srt_path = video_path.with_suffix(".srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, sub in enumerate(subtitle_lines, 1):
                start = self._seconds_to_srt(sub["start_time"])
                end = self._seconds_to_srt(sub["end_time"])
                f.write(f"{i}\n{start} --> {end}\n{sub['text']}\n\n")

        # 烧录字幕
        output_path = video_path.with_name(f"{video_path.stem}_subtitled.mp4")
        cmd = [
            "ffmpeg", "-y", "-i", str(video_path),
            "-vf", f"subtitles={srt_path}:force_style='FontSize=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=1'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy", str(output_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        # 替换原文件
        output_path.replace(video_path)

    def _speaker_color(self, speaker: str) -> str:
        """根据说话人返回背景色"""
        colors = {
            "狸花猫": "#FFF8DC",
            "棕熊": "#F5DEB3",
            "小狐狸": "#FFE4B5",
            "熊猫": "#F0F0F0",
            "猫头鹰": "#E6E6FA",
        }
        for key, color in colors.items():
            if key in speaker:
                return color
        return "#FFFFFF"

    @staticmethod
    def _seconds_to_srt(seconds: float) -> str:
        """秒数转 SRT 时间格式"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
