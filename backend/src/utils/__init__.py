"""
工具函数
"""

import hashlib
import re
from pathlib import Path
from typing import Optional


def hash_source(source: str) -> str:
    """生成来源哈希（用于缓存）"""
    return hashlib.md5(source.encode()).hexdigest()[:12]


def clean_text(text: str) -> str:
    """清洗文本"""
    # 移除多余空白
    text = re.sub(r"\s+", " ", text)
    # 移除控制字符
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()


def ensure_dir(path: Path) -> Path:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_duration(seconds: float) -> str:
    """格式化时长"""
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"
