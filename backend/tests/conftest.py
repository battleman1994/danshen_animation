"""
Pytest 配置和共享 fixtures
"""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_output_dir():
    """创建临时输出目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text_content():
    """示例文本内容"""
    return {
        "source": "今天天气真好，我们去公园散步吧！",
        "source_type": "text",
        "character": "tabby_cat",
    }
