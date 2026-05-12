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

    def test_sd_model_default(self):
        settings = Settings()
        assert settings.sd_model == "sd_1.5_base.safetensors"

    def test_lora_model_paths(self):
        settings = Settings()
        assert "tabby_cat" in settings.lora_model_paths
        assert settings.lora_model_paths["tabby_cat"] == "tabby_cat_lora.safetensors"

    def test_lora_weights(self):
        settings = Settings()
        assert "tabby_cat" in settings.lora_weights
        assert 0.0 < settings.lora_weights["tabby_cat"] <= 1.0

    def test_default_seed(self):
        settings = Settings()
        assert settings.default_seed == 42

    def test_ken_burns_default(self):
        settings = Settings()
        assert settings.use_ken_burns is True

    def test_sd_image_dimensions(self):
        settings = Settings()
        assert settings.sd_image_width == 768
        assert settings.sd_image_height == 512
