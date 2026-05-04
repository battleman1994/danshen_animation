"""
Celery Worker — 异步视频生成任务

启动方式:
  celery -A src.worker worker --loglevel=info --concurrency=2
"""

import asyncio

from celery import Celery

from .config import settings

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
    task_time_limit=settings.max_video_duration + 60,
    task_soft_time_limit=settings.max_video_duration + 30,
)


@celery_app.task(bind=True, name="generate_animation")
def generate_animation(self, task_data: dict):
    """
    异步生成动漫视频

    Args:
        task_data: 包含 source, source_type, character 等
    """
    async def _run():
        from .pipeline import (
            ContentExtractor, ScriptAdapter, CharacterGenerator,
            VoiceSynthesizer, VideoComposer,
        )

        task_id = self.request.id
        source = task_data["source"]
        source_type = task_data.get("source_type", "text")
        character = task_data.get("character", "tabby_cat")
        character_count = task_data.get("character_count", 2)
        style = task_data.get("style", "auto")
        resolution = task_data.get("resolution", "1080p")
        subtitle = task_data.get("subtitle", True)

        # 阶段 1：内容提取
        self.update_state(state="EXTRACTING", meta={"progress": 10})
        extractor = ContentExtractor()
        content = await extractor.extract(source, source_type)

        # 阶段 2：脚本改编
        self.update_state(state="ADAPTING", meta={"progress": 30})
        adapter = ScriptAdapter()
        script = await adapter.adapt(content, character, character_count, style)

        # 阶段 3：角色生成
        self.update_state(state="GENERATING_CHARACTERS", meta={"progress": 50})
        char_gen = CharacterGenerator()
        character_images = await char_gen.generate_character_set(character)
        background = await char_gen.generate_background(script.background_mood)

        # 阶段 4：语音合成
        self.update_state(state="SYNTHESIZING_VOICE", meta={"progress": 70})
        voice_synth = VoiceSynthesizer()
        audio_segments = await voice_synth.synthesize_script(script)

        # 阶段 5：视频合成
        self.update_state(state="COMPOSING_VIDEO", meta={"progress": 85})
        composer = VideoComposer()
        video_path = await composer.compose(
            task_id=task_id,
            character_images=character_images,
            background_path=background,
            audio_segments=audio_segments,
            subtitle_lines=[],
            resolution=resolution,
        )

        return {
            "video_url": f"/output/videos/{task_id}.mp4",
            "video_path": str(video_path),
            "duration": sum(s.get("duration", 0) for s in audio_segments),
        }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()
