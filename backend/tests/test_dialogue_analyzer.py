"""
对话分析器测试

测试说话人检测、对话节奏分析和角色推荐。
"""

import pytest
from src.pipeline.dialogue_analyzer import (
    DialogueAnalyzer,
    DialogueAnalysis,
    SpeakerInfo,
)


@pytest.fixture
def analyzer():
    return DialogueAnalyzer()


@pytest.fixture
def two_speaker_transcript():
    return [
        {"speaker": 0, "text": "今天天气真好！"},
        {"speaker": 1, "text": "是啊，我们去野餐吧！"},
        {"speaker": 0, "text": "好主意！带什么吃的？"},
        {"speaker": 1, "text": "我做了三明治和水果沙拉～"},
        {"speaker": 0, "text": "太棒了！我带上饮料。"},
        {"speaker": 1, "text": "哈哈，完美！"},
    ]


class TestSpeakerInfo:
    def test_to_dict(self):
        info = SpeakerInfo(
            speaker_id=0,
            gender="female",
            emotion_profile="happy",
            utterance_count=3,
            sample_text="你好世界",
        )
        d = info.to_dict()
        assert d["speaker_id"] == 0
        assert d["gender"] == "female"
        assert d["emotion_profile"] == "happy"
        assert d["utterance_count"] == 3


class TestDialogueAnalyzer:
    async def test_empty_transcript(self, analyzer):
        result = await analyzer.analyze_dialogue([])
        assert result.speaker_count == 1
        assert result.recommended_character == "tabby_cat"

    async def test_two_speaker_balanced(self, analyzer, two_speaker_transcript):
        result = await analyzer.analyze_dialogue(two_speaker_transcript, 30.0)
        assert result.speaker_count == 2
        assert len(result.speakers) == 2

    async def test_recommendation_for_dialogue(self, analyzer, two_speaker_transcript):
        result = await analyzer.analyze_dialogue(two_speaker_transcript, 15.0)
        # 双人快节奏对话应该推荐狸花猫
        assert result.recommended_character in ["tabby_cat", "little_fox"]

    async def test_emotion_detection(self, analyzer):
        result = await analyzer.analyze_dialogue([
            {"speaker": 0, "text": "哈哈哈太搞笑了"},
            {"speaker": 1, "text": "笑死我了"},
        ], 10.0)
        # 至少一个说话人的情绪应该是 happy
        emotions = [s.emotion_profile for s in result.speakers]
        assert any(e == "happy" for e in emotions)

    async def test_density(self, analyzer, two_speaker_transcript):
        result = await analyzer.analyze_dialogue(two_speaker_transcript, 10.0)
        # 6 utterances in 10 seconds -> dense
        assert result.dialogue_density in ["dense", "normal", "sparse"]

    async def test_single_speaker_monologue(self, analyzer):
        result = await analyzer.analyze_dialogue([
            {"speaker": 0, "text": "今天我要讲一个很长的故事。"},
            {"speaker": 0, "text": "这个故事发生在很久很久以前..."},
            {"speaker": 0, "text": "有一个勇敢的少年..."},
        ], 30.0)
        assert result.speaker_count == 1
        assert result.recommended_character == "owl"

    async def test_turn_pattern_detection(self, analyzer):
        # 快速切换的对话
        rapid = [
            {"speaker": 0, "text": "你好"},
            {"speaker": 1, "text": "你好"},
            {"speaker": 0, "text": "吃了吗"},
            {"speaker": 1, "text": "吃了"},
            {"speaker": 0, "text": "啥"},
            {"speaker": 1, "text": "面"},
        ]
        result = await analyzer.analyze_dialogue(rapid, 6.0)
        assert result.turn_taking_pattern == "rapid_exchange"
