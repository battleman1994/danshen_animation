import json
from unittest.mock import AsyncMock, patch

import pytest
from src.pipeline.prompt_builder import PromptBuilder, VideoPrompt


MOCK_LLM_RESPONSE = json.dumps({
    "prompt": "A cute orange tabby cat with green eyes, happily waving paw in a sunny park, chibi anime style, soft lighting, the cat speaks cheerfully about the beautiful weather with Chinese subtitles appearing at the bottom, medium shot with gentle camera pan, bright and warm atmosphere, high quality animation",
    "title": "公园散步好天气",
    "duration_estimate": 12,
}, ensure_ascii=False)


@pytest.mark.asyncio
async def test_build_returns_video_prompt():
    builder = PromptBuilder()
    with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = MOCK_LLM_RESPONSE

        result = await builder.build(
            "今天天气真好，我们去公园散步吧！",
            character="tabby_cat",
            style="funny",
        )
        assert isinstance(result, VideoPrompt)
        assert len(result.prompt) > 0
        assert "tabby cat" in result.prompt.lower()
        assert result.title == "公园散步好天气"
        assert result.duration_estimate == 12


@pytest.mark.asyncio
async def test_build_parses_markdown_code_blocks():
    builder = PromptBuilder()
    with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = f"```json\n{MOCK_LLM_RESPONSE}\n```"

        result = await builder.build("test", character="tabby_cat", style="funny")
        assert len(result.prompt) > 0
        assert result.title == "公园散步好天气"


@pytest.mark.asyncio
async def test_build_invalid_json_raises():
    builder = PromptBuilder()
    with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "not json at all"

        with pytest.raises(ValueError):
            await builder.build("test", character="tabby_cat", style="funny")


@pytest.mark.asyncio
async def test_build_different_characters():
    builder = PromptBuilder()

    for char_id in ["tabby_cat", "panda", "lion", "owl"]:
        with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
            prompt_text = f"A {char_id} anime character performing, high quality"
            mock_call.return_value = json.dumps({
                "prompt": prompt_text,
                "title": f"测试-{char_id}",
                "duration_estimate": 10,
            })

            result = await builder.build("测试内容", character=char_id, style="funny")
            assert isinstance(result, VideoPrompt)
            assert len(result.prompt) > 0


@pytest.mark.asyncio
async def test_build_different_styles():
    builder = PromptBuilder()

    for style in ["funny", "serious", "cute", "news"]:
        with patch.object(builder, "_call_llm", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = json.dumps({
                "prompt": f"A video in {style} style, anime, high quality",
                "title": f"测试-{style}",
                "duration_estimate": 10,
            })

            result = await builder.build("测试", character="tabby_cat", style=style)
            assert isinstance(result, VideoPrompt)


@pytest.mark.asyncio
async def test_llm_models_have_expected_capabilities():
    from src.pipeline.prompt_builder import LLM_MODELS, supports_input_type

    # 文本模型只支持 text 和 web_link
    assert supports_input_type("deepseek-v4-pro[1m]", "text")
    assert supports_input_type("deepseek-v4-pro[1m]", "web_link")
    assert not supports_input_type("deepseek-v4-pro[1m]", "image")
    assert not supports_input_type("deepseek-v4-pro[1m]", "douyin_video")

    # 多模态模型支持全部类型
    assert supports_input_type("gpt-4o", "text")
    assert supports_input_type("gpt-4o", "image")
    assert supports_input_type("gpt-4o", "douyin_video")

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
