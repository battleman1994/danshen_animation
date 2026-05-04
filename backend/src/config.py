"""
danshen_animation — AI 动漫视频生成器

配置管理模块。支持从环境变量和 .env 文件加载配置。
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""

    # ── 服务 ──
    app_name: str = "danshen_animation"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/api/v1"

    # ── AI 模型 ──
    llm_provider: str = "deepseek"  # deepseek, openai, anthropic
    llm_model: str = "deepseek-chat"
    llm_api_key: Optional[str] = None
    llm_base_url: str = "https://api.deepseek.com"

    # ── Whisper ──
    whisper_model: str = "base"  # tiny, base, small, medium, large-v3
    whisper_device: str = "cpu"  # cpu, cuda

    # ── TTS ──
    tts_provider: str = "edge"  # edge, elevenlabs, openai
    tts_voice: str = "zh-CN-XiaoxiaoNeural"  # 默认中文女声
    elevenlabs_api_key: Optional[str] = None

    # ── 图片生成 ──
    image_gen_provider: str = "comfyui"  # comfyui, openai, stability
    comfyui_url: str = "http://localhost:8188"

    # ── Redis / Celery ──
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── 存储 ──
    storage_provider: str = "local"  # local, s3
    storage_path: Path = Path("./data")
    s3_bucket: Optional[str] = None
    s3_endpoint: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None

    # ── 输出 ──
    output_dir: Path = Path("./output")
    default_resolution: str = "1080p"
    max_video_duration: int = 300  # 最长 5 分钟
    supported_formats: list[str] = ["mp4", "webm", "gif"]

    # ── 角色预设 ──
    character_presets: dict = {
        "tabby_cat": {"name": "狸花猫", "emoji": "🐱", "style": "活泼灵巧"},
        "brown_bear": {"name": "棕熊", "emoji": "🐻", "style": "稳重憨厚"},
        "little_fox": {"name": "小狐狸", "emoji": "🦊", "style": "机灵俏皮"},
        "panda": {"name": "熊猫", "emoji": "🐼", "style": "呆萌可爱"},
        "rabbit": {"name": "兔子", "emoji": "🐰", "style": "温柔敏捷"},
        "shiba_inu": {"name": "柴犬", "emoji": "🐶", "style": "忠诚阳光"},
        "owl": {"name": "猫头鹰", "emoji": "🦉", "style": "智慧专业"},
        "penguin": {"name": "企鹅", "emoji": "🐧", "style": "憨态可掬"},
        "lion": {"name": "雄狮", "emoji": "🦁", "style": "庄重威严"},
    }

    # ── 新闻分级 → 动物映射 ──
    news_animal_mapping: dict = {
        "entertainment": {"character": "shiba_inu", "name": "柴犬", "emoji": "🐕", "style": "轻松调侃"},
        "social": {"character": "owl", "name": "猫头鹰", "emoji": "🦉", "style": "温和稳重"},
        "finance_tech": {"character": "penguin", "name": "企鹅", "emoji": "🐧", "style": "严谨专业"},
        "major_event": {"character": "lion", "name": "雄狮", "emoji": "🦁", "style": "庄重严肃"},
    }

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow",
    }


settings = Settings()
