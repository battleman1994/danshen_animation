import uuid
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/animate", tags=["animate"])

logger = logging.getLogger(__name__)

_task_store: dict[str, dict] = {}


class AnimateRequest(BaseModel):
    source: str = Field(
        ..., description="Input content for video generation",
        min_length=1, max_length=5000,
    )
    source_type: str = Field(default="text", description="Content type: text, web_link, image, douyin_video")
    character: str = Field(
        default="orange_tabby",
        description="Character ID",
        pattern="^(orange_tabby|calico_cat|black_cat|ragdoll_cat|british_shorthair|orange_cat_fat|panda)$",
    )
    style: str = Field(
        default="funny",
        description="Style: funny, serious, cute, news, auto",
        pattern="^(funny|serious|cute|news|auto)$",
    )
    provider: str = Field(default="mock", description="Video generation provider ID")
    llm_model: str = Field(default="", description="LLM model for prompt generation (empty = use default)")
    resolution: str = Field(default="1080p", pattern="^(720p|1080p)$")
    subtitle: bool = Field(default=True)


class AnimateResponse(BaseModel):
    task_id: str
    status: str = "queued"
    poll_url: str


@router.get("/providers")
async def list_providers():
    from ..pipeline.video_gen import list_providers as _list
    from ..config import settings as _settings
    return {"providers": _list(), "active": _settings.video_gen_provider}


@router.get("/llm-models")
async def list_llm_models():
    from ..pipeline.prompt_builder import list_llm_models as _list
    from ..config import settings as _settings
    return {"models": _list(), "active": _settings.llm_model}


@router.post("", response_model=AnimateResponse)
async def create_animation(request: AnimateRequest, background_tasks: BackgroundTasks, req: Request = None):
    task_id = f"anim_{uuid.uuid4().hex[:12]}"

    _task_store[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "request": request.model_dump(),
        "result": None,
        "error": None,
    }

    # 可选：记录到 video_history（如果用户已登录）
    user_id = ""
    try:
        from ..auth import get_current_user
        user = await get_current_user(req)
        user_id = user["id"]
    except Exception:
        pass

    background_tasks.add_task(_process_task, task_id, user_id)

    return AnimateResponse(
        task_id=task_id,
        status="queued",
        poll_url=f"/api/v1/tasks/{task_id}",
    )


async def _process_task(task_id: str, user_id: str = ""):
    from ..pipeline import PromptBuilder, get_provider, supports_input_type
    from ..config import settings as cfg

    task = _task_store[task_id]
    req = task["request"]

    # 写入 video_history 记录
    history_id = ""
    if user_id:
        from ..database import get_db, new_id, now
        history_id = new_id()
        db = await get_db()
        await db.execute(
            """INSERT INTO video_history (id, user_id, task_id, source, source_type,
               character_id, prompt_used, provider, llm_model, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, '', ?, ?, 'queued', ?)""",
            (history_id, user_id, task_id, req["source"], req.get("source_type", "text"),
             req["character"], req.get("provider", "mock"), req.get("llm_model", cfg.llm_model), now()),
        )
        await db.commit()

    try:
        llm_model = req.get("llm_model") or cfg.llm_model
        source_type = req.get("source_type", "text")

        if not supports_input_type(llm_model, source_type):
            raise ValueError(
                f"LLM 模型 {llm_model} 不支持 {source_type} 类型的输入，请选择多模态模型"
            )

        # Stage 0: Content fetching — URL → plain text
        from ..pipeline.content_fetcher import fetch_content
        task["status"] = "extracting"
        task["progress"] = 5
        raw_content = await fetch_content(req["source"], source_type)

        # Stage 1: Prompt generation — content → AI video prompt
        task["status"] = "generating_prompt"
        task["progress"] = 15
        builder = PromptBuilder(model_id=llm_model)
        video_prompt = await builder.build(
            content=raw_content,
            character=req["character"],
            scene_mode=req.get("scene_mode", "auto"),
        )

        # Stage 2: Video generation — submit prompt to third-party API
        task["status"] = "generating_video"
        task["progress"] = 30
        provider = get_provider(req.get("provider", "mock"))

        video_dir = cfg.output_dir / "videos"
        video_dir.mkdir(parents=True, exist_ok=True)
        final_path = video_dir / f"{task_id}.mp4"

        await provider.generate(
            prompt=video_prompt.prompt,
            duration_s=video_prompt.duration_estimate,
            output_path=final_path,
        )

        task["status"] = "completed"
        task["progress"] = 100
        task["result"] = {
            "video_url": f"/output/videos/{task_id}.mp4",
            "video_path": str(final_path),
            "prompt": video_prompt.prompt,
            "title": video_prompt.title,
            "duration_estimate": video_prompt.duration_estimate,
            "llm_model": video_prompt.model_used,
        }

        # 更新 video_history
        if history_id:
            await db.execute(
                """UPDATE video_history SET status = 'completed', prompt_used = ?,
                   video_url = ?, title = ?, duration_estimate = ? WHERE id = ?""",
                (video_prompt.prompt, f"/output/videos/{task_id}.mp4",
                 video_prompt.title, video_prompt.duration_estimate, history_id),
            )
            await db.commit()

    except Exception as e:
        logger.exception("Task %s failed", task_id)
        task["status"] = "failed"
        task["error"] = str(e)

        if history_id:
            await db.execute(
                "UPDATE video_history SET status = 'failed', error = ? WHERE id = ?",
                (str(e), history_id),
            )
            await db.commit()
