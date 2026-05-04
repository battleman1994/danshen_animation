"""
danshen_animation 视频生成流水线

五阶段流水线：
  1. 内容提取 (extractor)
  2. 脚本改编 (adapter)
  3. 角色生成 (character)
  4. 语音合成 (voice)
  5. 视频合成 (composer)

辅助模块：
  - 新闻分析器 (news_analyzer)
  - 对话分析器 (dialogue_analyzer)
"""

from .extractor import ContentExtractor, ExtractedContent
from .adapter import ScriptAdapter, AdaptedScript, ScriptLine
from .character import CharacterGenerator
from .voice import VoiceSynthesizer
from .composer import VideoComposer
from .news_analyzer import NewsAnalyzer, NewsAnalysisResult, AnimalAnchor, NewsSeverity
from .dialogue_analyzer import DialogueAnalyzer, DialogueAnalysis, SpeakerInfo

__all__ = [
    # Pipeline stages
    "ContentExtractor",
    "ScriptAdapter",
    "CharacterGenerator",
    "VoiceSynthesizer",
    "VideoComposer",
    # Data classes
    "ExtractedContent",
    "AdaptedScript",
    "ScriptLine",
    # Analyzers
    "NewsAnalyzer",
    "NewsAnalysisResult",
    "AnimalAnchor",
    "NewsSeverity",
    "DialogueAnalyzer",
    "DialogueAnalysis",
    "SpeakerInfo",
]
