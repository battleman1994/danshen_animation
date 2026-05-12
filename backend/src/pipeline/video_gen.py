import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..config import settings

logger = logging.getLogger(__name__)


# ── Provider interface ──

@dataclass
class ProviderMeta:
    id: str
    name: str
    description: str
    config_fields: list[dict] = field(default_factory=list)
    supported_input_types: list[str] = field(default_factory=lambda: ["text", "web_link", "image", "douyin_video"])
    mode: str = "remote"                 # "local" = 用户自配 API key, "remote" = 平台提供
    requires_config: list[str] = field(default_factory=list)  # local 模式需要的配置项


class VideoGenProvider(ABC):
    """Abstract video generation provider."""

    meta: ProviderMeta

    @abstractmethod
    async def generate(self, prompt: str, duration_s: int, output_path: Path) -> Path:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...


# ── Provider implementations ──

class MockProvider(VideoGenProvider):
    meta = ProviderMeta(
        id="mock",
        name="Mock 测试",
        description="本地生成的彩色占位视频，无需 API key",
        supported_input_types=["text", "web_link", "image", "douyin_video"],
        mode="remote",
    )

    async def generate(self, prompt: str, duration_s: int, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        hue = int(hashlib.md5(prompt.encode()).hexdigest()[:2], 16) * 360 // 256
        colors = ["#1a1a2e", "#2d1b2e", "#1e2d1b", "#2e1a1a", "#1b2d2e", "#2e2d1a"]
        color_bg = colors[hue % len(colors)]

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={color_bg}:s=1280x720:d={duration_s}:r=24",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(output_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Mock render failed: {stderr.decode()}")
        return output_path

    async def health_check(self) -> bool:
        return True


class KlingProvider(VideoGenProvider):
    meta = ProviderMeta(
        id="kling",
        name="可灵 Kling",
        description="快手可灵 AI 视频生成，中文场景效果最佳",
        supported_input_types=["text", "web_link", "image"],
        mode="local",
        requires_config=["kling_api_key"],
        config_fields=[
            {"key": "kling_api_key", "label": "API Key", "type": "password"},
            {"key": "kling_model", "label": "模型", "type": "select",
             "options": ["kling-v1", "kling-v1-5", "kling-v2"]},
        ],
    )

    def __init__(self):
        self._api_key = settings.kling_api_key or ""
        self._model = settings.kling_model or "kling-v1"

    async def generate(self, prompt: str, duration_s: int, output_path: Path) -> Path:
        import httpx
        if not self._api_key:
            raise ValueError("Kling API key not configured")

        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
            payload = {
                "model_name": self._model,
                "prompt": prompt,
                "duration": min(duration_s, 10),
                "mode": "std",
                "aspect_ratio": "16:9",
            }
            resp = await client.post(
                "https://api.klingai.com/v1/videos/text2video",
                json=payload, headers=headers,
            )
            resp.raise_for_status()
            task_id = resp.json()["data"]["task_id"]

            for _ in range(40):
                await asyncio.sleep(5)
                poll = await client.get(
                    f"https://api.klingai.com/v1/videos/text2video/{task_id}",
                    headers=headers,
                )
                poll.raise_for_status()
                result = poll.json()
                status = result["data"]["task_status"]
                if status == "succeed":
                    url = result["data"]["task_result"]["videos"][0]["url"]
                    dl = await client.get(url)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(dl.content)
                    return output_path
                elif status == "failed":
                    raise RuntimeError(f"Kling failed: {result}")
            raise TimeoutError("Kling task timed out")

    async def health_check(self) -> bool:
        return bool(self._api_key)


class RunwayProvider(VideoGenProvider):
    meta = ProviderMeta(
        id="runway",
        name="Runway Gen-4",
        description="Runway 最新视频生成模型，质量顶级",
        supported_input_types=["text", "web_link", "image"],
        mode="local",
        requires_config=["runway_api_key"],
        config_fields=[
            {"key": "runway_api_key", "label": "API Key", "type": "password"},
        ],
    )

    def __init__(self):
        self._api_key = settings.runway_api_key or ""

    async def generate(self, prompt: str, duration_s: int, output_path: Path) -> Path:
        import httpx
        if not self._api_key:
            raise ValueError("Runway API key not configured")

        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
            payload = {"prompt": prompt, "duration": min(duration_s, 10), "aspect_ratio": "16:9"}
            resp = await client.post(
                "https://api.runwayml.com/v1/text_to_video",
                json=payload, headers=headers,
            )
            resp.raise_for_status()
            task_id = resp.json()["id"]

            for _ in range(40):
                await asyncio.sleep(5)
                poll = await client.get(
                    f"https://api.runwayml.com/v1/tasks/{task_id}", headers=headers,
                )
                poll.raise_for_status()
                result = poll.json()
                if result["status"] == "SUCCEEDED":
                    url = result["output"][0]
                    dl = await client.get(url)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(dl.content)
                    return output_path
                elif result["status"] == "FAILED":
                    raise RuntimeError(f"Runway failed: {result}")
            raise TimeoutError("Runway task timed out")

    async def health_check(self) -> bool:
        return bool(self._api_key)


class JimengProvider(VideoGenProvider):
    meta = ProviderMeta(
        id="jimeng",
        name="即梦 Jimeng",
        description="字节跳动即梦 AI，抖音同款视频生成",
        supported_input_types=["text", "web_link", "image", "douyin_video"],
        mode="local",
        requires_config=["jimeng_api_key", "jimeng_secret"],
        config_fields=[
            {"key": "jimeng_api_key", "label": "API Key", "type": "password"},
            {"key": "jimeng_secret", "label": "Secret", "type": "password"},
        ],
    )

    def __init__(self):
        self._api_key = settings.jimeng_api_key or ""
        self._secret = settings.jimeng_secret or ""

    async def generate(self, prompt: str, duration_s: int, output_path: Path) -> Path:
        import httpx
        if not self._api_key:
            raise ValueError("Jimeng API key not configured")

        async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
            payload = {
                "prompt": prompt,
                "duration": min(duration_s, 10),
                "aspect_ratio": "16:9",
            }
            resp = await client.post(
                "https://api.dreamina.volces.com/v1/video/generate",
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()
            task_id = data.get("task_id") or data.get("id")

            for _ in range(40):
                await asyncio.sleep(5)
                poll = await client.get(
                    f"https://api.dreamina.volces.com/v1/video/status/{task_id}",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                poll.raise_for_status()
                result = poll.json()
                if result.get("status") == "completed":
                    url = result["video_url"]
                    dl = await client.get(url)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(dl.content)
                    return output_path
                elif result.get("status") == "failed":
                    raise RuntimeError(f"Jimeng failed: {result}")
            raise TimeoutError("Jimeng task timed out")

    async def health_check(self) -> bool:
        return bool(self._api_key)


class HailuoProvider(VideoGenProvider):
    meta = ProviderMeta(
        id="hailuo",
        name="海螺 Hailuo",
        description="MiniMax 海螺 AI 视频生成",
        supported_input_types=["text", "web_link"],
        mode="local",
        requires_config=["hailuo_api_key"],
        config_fields=[
            {"key": "hailuo_api_key", "label": "API Key", "type": "password"},
        ],
    )

    def __init__(self):
        self._api_key = settings.hailuo_api_key or ""

    async def generate(self, prompt: str, duration_s: int, output_path: Path) -> Path:
        import httpx
        if not self._api_key:
            raise ValueError("Hailuo API key not configured")

        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
            payload = {"prompt": prompt, "duration": min(duration_s, 10)}
            resp = await client.post(
                "https://api.minimax.chat/v1/video_generation",
                json=payload, headers=headers,
            )
            resp.raise_for_status()
            task_id = resp.json()["task_id"]

            for _ in range(40):
                await asyncio.sleep(5)
                poll = await client.get(
                    f"https://api.minimax.chat/v1/query/video_generation?task_id={task_id}",
                    headers=headers,
                )
                poll.raise_for_status()
                result = poll.json()
                if result["status"] == "Success":
                    url = result["video_url"]
                    dl = await client.get(url)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(dl.content)
                    return output_path
                elif result["status"] == "Failed":
                    raise RuntimeError(f"Hailuo failed: {result}")
            raise TimeoutError("Hailuo task timed out")

    async def health_check(self) -> bool:
        return bool(self._api_key)


# ── Provider Registry ──

_registry: dict[str, type[VideoGenProvider]] = {}
_instances: dict[str, VideoGenProvider] = {}


def register(cls: type[VideoGenProvider]):
    _registry[cls.meta.id] = cls
    return cls


def get_provider(provider_id: str | None = None) -> VideoGenProvider:
    pid = provider_id or settings.video_gen_provider or "mock"
    if pid not in _registry:
        logger.warning("Unknown provider '%s', falling back to mock", pid)
        pid = "mock"

    if pid not in _instances:
        _instances[pid] = _registry[pid]()
    return _instances[pid]


def list_providers() -> list[dict]:
    result = []
    for pid, cls in _registry.items():
        # 本地模式：检查用户是否配置了 API key
        if cls.meta.mode == "local":
            config_ok = all(
                bool(getattr(settings, key, None))
                for key in cls.meta.requires_config
            )
            available = config_ok
        else:
            # 远程模式：平台提供服务，始终可用
            available = True

        result.append({
            "id": pid,
            "name": cls.meta.name,
            "description": cls.meta.description,
            "config_fields": cls.meta.config_fields,
            "supported_input_types": cls.meta.supported_input_types,
            "mode": cls.meta.mode,
            "requires_config": cls.meta.requires_config,
            "available": available,
        })
    return result


# Register built-in providers
for _cls in [MockProvider, KlingProvider, RunwayProvider, JimengProvider, HailuoProvider]:
    register(_cls)
