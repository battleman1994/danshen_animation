import asyncio
import logging
import tempfile
from pathlib import Path

from ..config import settings
from .storyboard import Storyboard

logger = logging.getLogger(__name__)


class VideoComposer:
    def __init__(self):
        self.output_dir = settings.output_dir / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def compose_storyboard(
        self,
        task_id: str,
        storyboard: Storyboard,
        scene_images: list[dict],
        audio_segments: list[dict],
        output_path: Path | None = None,
    ) -> Path:
        if output_path is None:
            output_path = self.output_dir / f"{task_id}.mp4"

        # Detect unique characters for multi-character layout
        all_chars = list(dict.fromkeys(s.character for s in storyboard.scenes))
        multi_char = len(all_chars) > 1

        ass_path = self._generate_ass(storyboard)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            scene_clips: list[Path] = []
            for scene in storyboard.scenes:
                aud_info = next(
                    (a for a in audio_segments if a.get("line_index") == scene.index), None
                )
                aud_path = str(aud_info["audio_path"]) if aud_info else None
                duration = scene.duration_s

                if multi_char:
                    # Dual character: find all images for this scene index
                    other_images = [
                        s for s in scene_images
                        if s["scene_index"] == scene.index
                        and s.get("character") != scene.character
                    ]
                    speaking_img = next(
                        (s for s in scene_images
                         if s["scene_index"] == scene.index
                         and s.get("character") == scene.character), None
                    )
                    speaking_path = speaking_img["image_path"] if speaking_img else None
                    other_path = other_images[0]["image_path"] if other_images else None
                    clip = await self._render_dual_scene(
                        speaking_path, other_path, duration, scene, tmp,
                    )
                else:
                    img_info = next(
                        (s for s in scene_images if s["scene_index"] == scene.index), None
                    )
                    img_path = img_info["image_path"] if img_info else None
                    clip = await self._render_ken_burns_scene(
                        img_path, duration, scene, tmp,
                    )

                if aud_path and Path(aud_path).exists():
                    clip = await self._mux_audio(clip, aud_path, duration, tmp, scene.index)

                scene_clips.append(clip)

            concat_path = tmp / "concat.mp4"
            await self._concat_scenes(scene_clips, concat_path)

            await self._burn_subtitles(concat_path, ass_path, output_path)

        return output_path

    async def _render_dual_scene(
        self, speaking_path: str | None, other_path: str | None,
        duration: int, scene, tmp: Path,
    ) -> Path:
        """Render two characters side by side."""
        out = tmp / f"scene_{scene.index:02d}_dual.mp4"
        w, h = 1280, 720

        if speaking_path and Path(speaking_path).exists():
            # Create side-by-side composite with speaking character highlighted
            cmd_inputs = []
            filters = []

            # Speaking character (left, larger/brighter)
            if speaking_path:
                cmd_inputs.extend(["-loop", "1", "-t", str(duration), "-i", speaking_path])
                filters.append(
                    f"[0:v]scale=640:720:force_original_aspect_ratio=decrease,"
                    f"pad=640:720:(ow-iw)/2:(oh-ih)/2:color=#1a1a2e,"
                    f"drawbox=x=0:y=0:w=640:h=720:color=yellow@0.3:t=fill[speaking]"
                )
            else:
                filters.append(
                    f"color=c=#2a2a4e:s=640x720:d={duration}:r=24[speaking]"
                )

            # Other character (right, dimmer)
            if other_path and Path(other_path).exists():
                cmd_inputs.extend(["-loop", "1", "-t", str(duration), "-i", other_path])
                filters.append(
                    f"[1:v]scale=640:720:force_original_aspect_ratio=decrease,"
                    f"pad=640:720:(ow-iw)/2:(oh-ih)/2:color=#1a1a2e,"
                    f"drawbox=x=0:y=0:w=640:h=720:color=black@0.3:t=fill[other]"
                )
            else:
                filters.append(
                    f"color=c=#1a1a2e:s=640x720:d={duration}:r=24[other]"
                )

            filters.append("[speaking][other]hstack=inputs=2,format=yuv420p[v]")
            filter_str = ";".join(filters)

            cmd = [
                "ffmpeg", "-y",
                *cmd_inputs,
                "-filter_complex", filter_str,
                "-map", "[v]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "15",
                "-pix_fmt", "yuv420p", "-r", "24",
                str(out),
            ]
        else:
            filters = (
                f"color=c=#1a1a2e:s={w}x{h}:d={duration}:r=24,format=yuv420p"
            )
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", filters,
                "-c:v", "libx264", "-preset", "medium", "-crf", "15",
                "-pix_fmt", "yuv420p",
                str(out),
            ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Dual scene render failed: {stderr.decode()}")
        return out

    async def _render_ken_burns_scene(
        self, img_path: str | None, duration: int, scene, tmp: Path
    ) -> Path:
        out = tmp / f"scene_{scene.index:02d}_video.mp4"
        w, h = 1280, 720

        if img_path and Path(img_path).exists():
            # Generate 2 alternating frames for simple animation
            anim_list = tmp / f"anim_{scene.index:02d}.txt"
            frame1 = tmp / f"anim_{scene.index:02d}_1.png"
            frame2 = tmp / f"anim_{scene.index:02d}_2.png"
            self._render_animated_frames(img_path, frame1, frame2, scene.emotion)
            anim_list.write_text(f"file '{frame1}'\nduration 0.125\nfile '{frame2}'\nduration 0.125\n")

            filters = (
                f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=#1a1a2e,"
                f"fade=t=in:st=0:d=0.3,fade=t=out:st={duration - 0.3}:d=0.3,"
                f"format=yuv420p"
            )
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", str(anim_list),
                "-vf", filters,
                "-c:v", "libx264", "-preset", "medium", "-crf", "15",
                "-pix_fmt", "yuv420p", "-r", "24",
                str(out),
            ]
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-t", str(duration), "-i", img_path,
                "-vf", filters,
                "-c:v", "libx264", "-preset", "medium", "-crf", "15",
                "-pix_fmt", "yuv420p",
                str(out),
            ]
        else:
            filters = (
                f"color=c=#F5F0EB:s={w}x{h}:d={duration}:r=24,"
                f"fade=t=in:st=0:d=0.3,fade=t=out:st={duration - 0.3}:d=0.3,"
                f"format=yuv420p"
            )
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", filters,
                "-c:v", "libx264", "-preset", "medium", "-crf", "15",
                "-pix_fmt", "yuv420p",
                str(out),
            ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Ken Burns render failed: {stderr.decode()}")
        return out

    async def _mux_audio(
        self, video_path: Path, audio_path: str, duration: int, tmp: Path, scene_idx: int
    ) -> Path:
        out = tmp / f"scene_{scene_idx:02d}_muxed.mp4"

        audio_dur = await self._get_audio_duration(audio_path)
        pad_filters = []

        if audio_dur < duration:
            pad_ms = int((duration - audio_dur) * 1000)
            pad_filters = ["-af", f"apad=pad_dur={pad_ms}ms"]
        elif audio_dur > duration + 0.5:
            pad_filters = [
                "-af", f"afade=t=out:st={duration - 0.5}:d=0.5",
                "-t", str(duration),
            ]

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path), "-i", audio_path,
            *pad_filters,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(out),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Audio mux failed: {stderr.decode()}")
        return out

    def _render_animated_frames(self, img_path: str, out1: Path, out2: Path, emotion: str):
        """Generate 2 slightly different frames for simple flip-book animation."""
        from PIL import Image
        img = Image.open(img_path).convert("RGBA")
        w, h = img.size
        # Frame 1: original
        img.save(out1, "PNG")
        # Frame 2: slight scale + position shift (breathing effect)
        shift = 6 if emotion in ("happy", "surprised", "funny") else 3
        img2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        img2.paste(img.resize((w - shift * 2, h - shift * 2)), (shift, shift))
        img2.save(out2, "PNG")

    async def _concat_scenes(self, clips: list[Path], output: Path):
        concat_file = output.parent / "concat_list.txt"
        lines = [f"file '{str(c)}'" for c in clips]
        concat_file.write_text("\n".join(lines))

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c:v", "libx264", "-preset", "medium", "-crf", "15",
            "-pix_fmt", "yuv420p",
            str(output),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Concat failed: {stderr.decode()}")
        return output

    async def _burn_subtitles(self, video_path: Path, ass_path: Path, output_path: Path):
        escaped = str(ass_path).replace(":", "\\:").replace("\\", "/")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", f"ass={escaped}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            str(output_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            stderr_text = stderr.decode()
            logger.warning("Subtitle burn had issues: %s", stderr_text[:200])
            output_path.unlink(missing_ok=True)
            video_path.rename(output_path)

    CHARACTER_SUBTITLE_COLORS = {
        "tabby_cat": "&H428CFF&",   # orange
        "brown_bear": "&H1469A0&",  # brown
        "little_fox": "&H35B0FF&",  # orange-red
        "panda": "&H6B6B6B&",       # gray
        "rabbit": "&HC0B6FF&",      # pink
        "shiba_inu": "&H60ECD4&",   # gold
        "owl": "&H8B7355&",         # brown-gray
        "penguin": "&H5C5C5C&",     # dark gray
        "lion": "&H20A5DA&",        # gold
    }

    def _generate_ass(self, storyboard: Storyboard) -> Path:
        ass_path = self.output_dir / "subtitles.ass"
        cumulative = 0.0
        dialogues = []

        for scene in storyboard.scenes:
            start = cumulative
            end = cumulative + scene.duration_s
            color = self.CHARACTER_SUBTITLE_COLORS.get(scene.character, "&HFFFFFF&")
            dialogues.append({
                "start": self._seconds_to_ass(start),
                "end": self._seconds_to_ass(end),
                "text": scene.dialogue,
                "color": color,
            })
            cumulative += scene.duration_s

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write("""[Script Info]
Title: danshen_animation
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,PingFang SC,28,&H00FFFFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,20,20,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
            for d in dialogues:
                f.write(
                    f'Dialogue: 0,{d["start"]},{d["end"]},Default,,0,0,0,,'
                    f'{{\\c{d["color"]}\\bord3\\shad2\\fs32}}{d["text"]}\n'
                )

        return ass_path

    def _seconds_to_ass(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    async def _get_audio_duration(self, audio_path: str) -> float:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        try:
            return float(stdout.decode().strip())
        except (ValueError, AttributeError):
            return 1.0

    @staticmethod
    def _seconds_to_srt(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
