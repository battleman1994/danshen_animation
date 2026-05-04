"""
POST /api/v1/animate — 提交视频生成任务

输入热点内容（文字/链接/图片），生成动漫配音视频。
"""

import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/animate", tags=["animate"])

# 内存中的任务存储（生产环境用 Redis）
_task_store: dict[str, dict] = {}
_processing_queue: list[str] = []


class AnimateRequest(BaseModel):
    """视频生成请求"""
    source: str = Field(..., description="输入内容：文字/URL/图片路径", min_length=1, max_length=5000)
    source_type: str = Field(
        default="text",
        description="内容类型：text, douyin_video, bilibili_video, web_link, image, weibo_post",
        pattern="^(text|douyin_video|bilibili_video|youtube_video|web_link|image|weibo_post)$"
    )
    character: str = Field(
        default="tabby_cat",
        description="角色：tabby_cat, brown_bear, little_fox, panda, rabbit, shiba_inu, owl, penguin",
        pattern="^(tabby_cat|brown_bear|little_fox|panda|rabbit|shiba_inu|owl|penguin)$"
    )
    character_count: int = Field(default=2, ge=1, le=5, description="角色数量")
    style: str = Field(default="auto", description="风格：auto, funny, serious, cute, news")
    resolution: str = Field(default="1080p", pattern="^(720p|1080p)$")
    subtitle: bool = Field(default=True, description="是否添加字幕")
    webhook_url: Optional[str] = Field(default=None, description="完成回调 URL")


class AnimateResponse(BaseModel):
    """提交响应"""
    task_id: str
    status: str = "queued"
    estimated_time: int = 120  # 预估秒数
    poll_url: str


@router.post("", response_model=AnimateResponse)
async def create_animation(request: AnimateRequest, background_tasks: BackgroundTasks):
    """提交视频生成任务"""
    task_id = f"anim_{uuid.uuid4().hex[:12]}"

    _task_store[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "request": request.model_dump(),
        "result": None,
        "error": None,
    }

    _processing_queue.append(task_id)

    # 异步处理（简化版，生产环境用 Celery）
    background_tasks.add_task(_process_task, task_id)

    return AnimateResponse(
        task_id=task_id,
        status="queued",
        estimated_time=120,
        poll_url=f"/api/v1/tasks/{task_id}",
    )


async def _process_task(task_id: str):
    """后台处理视频生成任务"""
    from ..pipeline import (
        ContentExtractor, ScriptAdapter, CharacterGenerator,
        VoiceSynthesizer, VideoComposer,
    )
    from ..config import settings as cfg

    task = _task_store[task_id]
    req = task["request"]

    try:
        # 阶段 1：内容提取
        task["status"] = "extracting"
        task["progress"] = 10
        extractor = ContentExtractor()
        content = await extractor.extract(req["source"], req["source_type"])

        # 阶段 2：脚本改编
        task["status"] = "adapting"
        task["progress"] = 30
        adapter = ScriptAdapter()
        style = req["style"] if req["style"] != "auto" else _auto_style(content.emotion)
        script = await adapter.adapt(
            content, character=req["character"],
            character_count=req["character_count"], style=style,
        )

        # 阶段 3：角色生成
        task["status"] = "generating_characters"
        task["progress"] = 50
        char_gen = CharacterGenerator()
        character_images = await char_gen.generate_character_set(req["character"])
        background = await char_gen.generate_background(script.background_mood)

        # 阶段 4：语音合成
        task["status"] = "synthesizing_voice"
        task["progress"] = 70
        voice_synth = VoiceSynthesizer()
        audio_segments = await voice_synth.synthesize_script(script)

        # 阶段 5：视频合成
        task["status"] = "composing_video"
        task["progress"] = 85
        composer = VideoComposer()
        video_path = await composer.compose(
            task_id=task_id,
            character_images=character_images,
            background_path=background,
            audio_segments=audio_segments,
            subtitle_lines=[],
            resolution=req["resolution"],
        )

        task["status"] = "completed"
        task["progress"] = 100
        task["result"] = {
            "video_url": f"/output/videos/{task_id}.mp4",
            "video_path": str(video_path),
            "duration": sum(s.get("duration", 0) for s in audio_segments),
        }

    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)


def _auto_style(emotion: str) -> str:
    """根据情绪自动选择风格"""
    style_map = {
        "funny": "funny", "happy": "funny",
        "serious": "serious", "sad": "serious",
        "neutral": "cute",
    }
    return style_map.get(emotion, "funny")
