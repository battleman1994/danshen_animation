"""
danshen_animation — AI 动漫视频生成器

配置管理模块。支持从环境变量和 .env 文件加载配置。
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""

    # ── 服务 ──
    app_name: str = "danshen_animation"
    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/api/v1"

    # ── LLM ──
    llm_model: str = "deepseek-v4-pro[1m]"
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.deepseek.com/anthropic"

    # ── 视频生成 API ──
    video_gen_provider: str = "mock"
    kling_api_key: str | None = None
    kling_model: str = "kling-v1"
    runway_api_key: str | None = None
    jimeng_api_key: str | None = None
    jimeng_secret: str | None = None
    hailuo_api_key: str | None = None

    # ── 数据库 ──
    database_url: str = "sqlite:///./data/danshen.db"

    # ── 会话 ──
    session_expire_hours: int = 72

    # ── 输出 ──
    output_dir: Path = Path("./output")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow",
    }


settings = Settings()
