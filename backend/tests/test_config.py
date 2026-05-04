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

    def test_character_presets(self):
        settings = Settings()
        assert "tabby_cat" in settings.character_presets
        assert "lion" in settings.character_presets
        assert settings.character_presets["lion"]["emoji"] == "🦁"

    def test_news_animal_mapping(self):
        settings = Settings()
        mapping = settings.news_animal_mapping
        assert "entertainment" in mapping
        assert "social" in mapping
        assert "finance_tech" in mapping
        assert "major_event" in mapping
        assert mapping["entertainment"]["character"] == "shiba_inu"
        assert mapping["major_event"]["character"] == "lion"

    def test_llm_config(self):
        settings = Settings()
        assert settings.llm_provider in ["deepseek", "openai", "anthropic"]

    def test_output_dir(self):
        from pathlib import Path
        settings = Settings()
        assert isinstance(settings.output_dir, Path)
