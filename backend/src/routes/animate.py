import uuid
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

router = APIRouter(prefix="/animate", tags=["animate"])

logger = logging.getLogger(__name__)

_task_store: dict[str, dict] = {}


class AnimateRequest(BaseModel):
    source: str = Field(
        ..., description="Input content for video generation",
        min_length=1, max_length=5000,
    )
    character: str = Field(
        default="tabby_cat",
        description="Character ID",
        pattern="^(tabby_cat|brown_bear|little_fox|panda|rabbit|shiba_inu|owl|penguin|lion)$",
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
async def create_animation(request: AnimateRequest, background_tasks: BackgroundTasks):
    task_id = f"anim_{uuid.uuid4().hex[:12]}"

    _task_store[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "request": request.model_dump(),
        "result": None,
        "error": None,
    }

    background_tasks.add_task(_process_task, task_id)

    return AnimateResponse(
        task_id=task_id,
        status="queued",
        poll_url=f"/api/v1/tasks/{task_id}",
    )


async def _process_task(task_id: str):
    from ..pipeline import PromptBuilder, get_provider, supports_input_type
    from ..config import settings as cfg

    task = _task_store[task_id]
    req = task["request"]

    try:
        llm_model = req.get("llm_model") or cfg.llm_model
        source_type = req.get("source_type", "text")

        # 检查 LLM 模型是否支持该输入类型
        if not supports_input_type(llm_model, source_type):
            raise ValueError(
                f"LLM 模型 {llm_model} 不支持 {source_type} 类型的输入，请选择多模态模型"
            )

        # Stage 1: Prompt generation — content → AI video prompt
        task["status"] = "generating_prompt"
        task["progress"] = 15
        builder = PromptBuilder(model_id=llm_model)
        video_prompt = await builder.build(
            content=req["source"],
            character=req["character"],
            style=req["style"],
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

    except Exception as e:
        logger.exception("Task %s failed", task_id)
        task["status"] = "failed"
        task["error"] = str(e)
