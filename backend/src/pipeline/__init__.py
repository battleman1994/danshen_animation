"""
danshen_animation 视频生成流水线

五阶段流水线：
  1. 内容提取 (extractor)
  2. 脚本改编 (adapter)
  3. 角色生成 (character)
  4. 语音合成 (voice)
  5. 视频合成 (composer)
"""

from .extractor import ContentExtractor
from .adapter import ScriptAdapter
from .character import CharacterGenerator
from .voice import VoiceSynthesizer
from .composer import VideoComposer

__all__ = [
    "ContentExtractor",
    "ScriptAdapter",
    "CharacterGenerator",
    "VoiceSynthesizer",
    "VideoComposer",
]
