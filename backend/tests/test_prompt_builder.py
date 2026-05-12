import json
from unittest.mock import AsyncMock, patch

import pytest
from src.pipeline.prompt_builder import PromptBuilder, VideoPrompt


MOCK_LLM_RESPONSE = json.dumps({
    "prompt": (
        "A round-faced orange tabby cat with amber eyes sits at a small wooden desk in a cozy "
        "home office. Morning sunlight streams through the window. The cat types on a tiny laptop "
        "with its paws, occasionally looking up with an exasperated expression. Medium shot, "
        "smooth camera movement. Warm natural lighting, soft shadows, cozy domestic atmosphere. "
        "Photorealistic cute cat, lively expression, high quality video."
    ),
    "title": "猫咪上班日常",
    "scene_type": "daily_life",
    "duration_estimate": 12,
}, ensure_ascii=False)


@pytest.mark.asyncio
async def test_build_returns_video_prompt():
    builder = PromptBuilder()
    with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = MOCK_LLM_RESPONSE

        result = await builder.build(
            "今天天气真好，我们去公园散步吧！",
            character="orange_tabby",
        )
        assert isinstance(result, VideoPrompt)
        assert len(result.prompt) > 0
        assert "orange tabby cat" in result.prompt.lower()
        assert result.title == "猫咪上班日常"
        assert result.duration_estimate == 12
        assert result.scene_type == "daily_life"


@pytest.mark.asyncio
async def test_build_parses_markdown_code_blocks():
    builder = PromptBuilder()
    with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = f"```json\n{MOCK_LLM_RESPONSE}\n```"

        result = await builder.build("test", character="orange_tabby")
        assert len(result.prompt) > 0
        assert result.title == "猫咪上班日常"


@pytest.mark.asyncio
async def test_build_invalid_json_raises():
    builder = PromptBuilder()
    with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "not json at all"

        with pytest.raises(ValueError):
            await builder.build("test", character="orange_tabby")


@pytest.mark.asyncio
async def test_build_all_characters():
    builder = PromptBuilder()
    char_ids = ["orange_tabby", "calico_cat", "black_cat", "ragdoll_cat",
                "british_shorthair", "orange_cat_fat", "panda"]

    for char_id in char_ids:
        with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = json.dumps({
                "prompt": f"A {char_id} looking cute, photorealistic style, high quality",
                "title": f"测试-{char_id}",
                "scene_type": "daily_life",
                "duration_estimate": 10,
            })

            result = await builder.build("测试内容", character=char_id)
            assert isinstance(result, VideoPrompt)
            assert len(result.prompt) > 0
            assert result.character == char_id


@pytest.mark.asyncio
async def test_build_scene_mode_news():
    builder = PromptBuilder()
    with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = json.dumps({
            "prompt": "A black cat anchor in a semi-formal studio, high quality",
            "title": "猫咪新闻播报",
            "scene_type": "social_commentary",
            "duration_estimate": 20,
        })

        result = await builder.build("重大新闻：今天猫粮降价了！", character="black_cat", scene_mode="news")
        assert result.scene_type == "social_commentary"


@pytest.mark.asyncio
async def test_llm_models_have_expected_capabilities():
    from src.pipeline.prompt_builder import LLM_MODELS, supports_input_type

    assert supports_input_type("deepseek-v4-pro[1m]", "text")
    assert supports_input_type("deepseek-v4-pro[1m]", "web_link")
    assert not supports_input_type("deepseek-v4-pro[1m]", "image")
    assert not supports_input_type("deepseek-v4-pro[1m]", "douyin_video")

    assert supports_input_type("gpt-4o", "text")
    assert supports_input_type("gpt-4o", "image")
    assert supports_input_type("claude-opus-4-7", "image")
    assert supports_input_type("claude-sonnet-4-6", "douyin_video")


def test_list_llm_models():
    from src.pipeline.prompt_builder import list_llm_models

    models = list_llm_models()
    assert len(models) >= 4
    for m in models:
        assert "id" in m
        assert "name" in m
        assert "provider" in m
        assert "supported_input_types" in m
        assert "available" in m


def test_character_info():
    from src.pipeline.prompt_builder import CHARACTER_INFO

    assert len(CHARACTER_INFO) == 7
    for char_id in ["orange_tabby", "panda", "orange_cat_fat"]:
        assert char_id in CHARACTER_INFO
        assert "appearance" in CHARACTER_INFO[char_id]
        assert "personality" in CHARACTER_INFO[char_id]
