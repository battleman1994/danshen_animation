import asyncio
import logging
from pathlib import Path

from celery import Celery

from .config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "danshen_animation",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.max_video_duration + 120,
    task_soft_time_limit=settings.max_video_duration + 90,
)


@celery_app.task(bind=True, name="generate_animation")
def generate_animation(self, task_data: dict):
    """异步视频生成任务 — 多模态分析 → 提示词 → 第三方 API 生成视频"""

    async def _run():
        from .pipeline import PromptBuilder, get_provider, supports_input_type

        task_id = self.request.id
        text = task_data["source"]
        character = task_data.get("character", "tabby_cat")
        style = task_data.get("style", "funny")
        provider_id = task_data.get("provider", "mock")
        llm_model = task_data.get("llm_model") or settings.llm_model
        source_type = task_data.get("source_type", "text")

        # 检查 LLM 模型是否支持该输入类型
        if not supports_input_type(llm_model, source_type):
            raise ValueError(
                f"LLM 模型 {llm_model} 不支持 {source_type} 类型的输入，请选择多模态模型"
            )

        # Stage 1: Multimodal analysis → video prompt
        self.update_state(state="GENERATING_PROMPT", meta={"progress": 15})
        builder = PromptBuilder(model_id=llm_model)
        video_prompt = await builder.build(
            content=text,
            character=character,
            style=style,
        )

        # Stage 2: Submit prompt to third-party video API
        self.update_state(state="GENERATING_VIDEO", meta={"progress": 30})
        provider = get_provider(provider_id)

        video_dir = settings.output_dir / "videos"
        video_dir.mkdir(parents=True, exist_ok=True)
        final_path = video_dir / f"{task_id}.mp4"

        await provider.generate(
            prompt=video_prompt.prompt,
            duration_s=video_prompt.duration_estimate,
            output_path=final_path,
        )

        return {
            "video_url": f"/output/videos/{task_id}.mp4",
            "video_path": str(final_path),
            "prompt": video_prompt.prompt,
            "title": video_prompt.title,
            "duration_estimate": video_prompt.duration_estimate,
        }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()
