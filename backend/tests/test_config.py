"""
配置模块测试
"""

from src.config import Settings


class TestSettings:
    def test_default_values(self):
        settings = Settings()
        assert settings.app_name == "danshen_animation"
        assert settings.port == 8000
        assert settings.api_prefix == "/api/v1"

    def test_llm_config(self):
        settings = Settings()
        assert settings.llm_model == "deepseek-v4-pro[1m]"
        assert settings.llm_base_url == "https://api.deepseek.com/anthropic"

    def test_output_dir(self):
        from pathlib import Path
        settings = Settings()
        assert isinstance(settings.output_dir, Path)

    def test_video_gen_provider_default(self):
        settings = Settings()
        assert settings.video_gen_provider == "mock"

    def test_video_api_keys_none_by_default(self):
        settings = Settings()
        assert settings.kling_api_key is None
        assert settings.runway_api_key is None
        assert settings.jimeng_api_key is None
        assert settings.jimeng_secret is None
        assert settings.hailuo_api_key is None
