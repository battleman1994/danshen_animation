import json
from unittest.mock import AsyncMock, patch

import pytest
from src.pipeline.adapter import ScriptAdapter
from src.pipeline.storyboard import Storyboard


MOCK_LLM_RESPONSE = json.dumps({
    "scenes": [
        {
            "index": 1, "duration_s": 4,
            "dialogue": "今天天气真好呀喵～",
            "character": "tabby_cat", "emotion": "happy",
            "action": "waving_paw", "background": "sunny_park",
            "camera": "medium_shot",
        },
        {
            "index": 2, "duration_s": 4,
            "dialogue": "我们去公园散步吧！",
            "character": "tabby_cat", "emotion": "happy",
            "action": "pointing", "background": "sunny_park",
            "camera": "wide_shot",
        },
    ],
    "total_duration_s": 8,
    "style": "funny",
}, ensure_ascii=False)


def _make_mock_resp(text: str):
    content = AsyncMock()
    content.text = text
    resp = AsyncMock()
    resp.content = [content]
    return resp


@pytest.mark.asyncio
async def test_adapt_returns_storyboard():
    adapter = ScriptAdapter()
    with patch.object(adapter.llm.messages, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = _make_mock_resp(MOCK_LLM_RESPONSE)

        result = await adapter.adapt("今天天气真好", character="tabby_cat", style="funny")
        assert isinstance(result, Storyboard)
        assert len(result.scenes) == 2
        assert result.scenes[0].character == "tabby_cat"
        assert result.scenes[0].emotion == "happy"
        assert result.total_duration_s == 8
        assert result.style == "funny"


@pytest.mark.asyncio
async def test_adapt_parses_markdown_code_blocks():
    adapter = ScriptAdapter()
    with patch.object(adapter.llm.messages, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = _make_mock_resp(f"```json\n{MOCK_LLM_RESPONSE}\n```")

        result = await adapter.adapt("test", character="tabby_cat", style="funny")
        assert len(result.scenes) == 2


@pytest.mark.asyncio
async def test_adapt_invalid_json_raises():
    adapter = ScriptAdapter()
    with patch.object(adapter.llm.messages, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = _make_mock_resp("not json at all")

        with pytest.raises(ValueError):
            await adapter.adapt("test", character="tabby_cat", style="funny")
