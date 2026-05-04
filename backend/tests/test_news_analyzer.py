"""
新闻分析器测试

测试新闻严重度分析和动物匹配功能。
"""

import pytest
from src.pipeline.news_analyzer import (
    NewsAnalyzer,
    NewsSeverity,
    NewsAnalysisResult,
    ANIMAL_ANCHORS,
    _severity_label,
)


class TestNewsSeverity:
    """新闻严重度枚举测试"""

    def test_severity_values(self):
        """验证所有严重度等级存在"""
        assert NewsSeverity.ENTERTAINMENT.value == "entertainment"
        assert NewsSeverity.SOCIAL.value == "social"
        assert NewsSeverity.FINANCE_TECH.value == "finance_tech"
        assert NewsSeverity.MAJOR_EVENT.value == "major_event"

    def test_severity_label(self):
        """验证严重度标签"""
        assert "娱乐" in _severity_label(NewsSeverity.ENTERTAINMENT)
        assert "社会" in _severity_label(NewsSeverity.SOCIAL)
        assert "财经" in _severity_label(NewsSeverity.FINANCE_TECH)
        assert "重大" in _severity_label(NewsSeverity.MAJOR_EVENT)


class TestAnimalAnchors:
    """动物主播预设测试"""

    def test_all_severities_have_anchor(self):
        """验证所有严重度等级都有对应主播"""
        for severity in NewsSeverity:
            assert severity in ANIMAL_ANCHORS, f"缺少 {severity} 的主播"

    def test_anchor_has_required_fields(self):
        """验证主播预设包含所有必要字段"""
        for severity, anchor in ANIMAL_ANCHORS.items():
            assert anchor.animal_id, f"{severity} 缺少 animal_id"
            assert anchor.name, f"{severity} 缺少 name"
            assert anchor.emoji, f"{severity} 缺少 emoji"
            assert anchor.voice_id, f"{severity} 缺少 voice_id"
            assert anchor.broadcast_tone, f"{severity} 缺少 broadcast_tone"

    def test_entertainment_anchor_is_shiba_inu(self):
        """娱乐新闻用柴犬"""
        anchor = ANIMAL_ANCHORS[NewsSeverity.ENTERTAINMENT]
        assert anchor.animal_id == "shiba_inu"

    def test_social_anchor_is_owl(self):
        """社会民生用猫头鹰"""
        anchor = ANIMAL_ANCHORS[NewsSeverity.SOCIAL]
        assert anchor.animal_id == "owl"

    def test_finance_anchor_is_penguin(self):
        """财经科技用企鹅"""
        anchor = ANIMAL_ANCHORS[NewsSeverity.FINANCE_TECH]
        assert anchor.animal_id == "penguin"

    def test_major_event_anchor_is_lion(self):
        """重大事件用雄狮"""
        anchor = ANIMAL_ANCHORS[NewsSeverity.MAJOR_EVENT]
        assert anchor.animal_id == "lion"


class TestNewsAnalyzer:
    """NewsAnalyzer 类测试"""

    def test_get_all_anchors(self):
        """验证 get_all_anchors 返回所有主播"""
        all_anchors = NewsAnalyzer.get_all_anchors()
        assert len(all_anchors) == 4
        assert "entertainment" in all_anchors
        assert "social" in all_anchors
        assert "finance_tech" in all_anchors
        assert "major_event" in all_anchors

    def test_fallback_analysis_entertainment(self):
        """测试回退分析：娱乐关键词"""
        analyzer = NewsAnalyzer()
        result = analyzer._fallback_analysis("今天明星八卦真热闹")
        assert result["severity"] == "entertainment"

    def test_fallback_analysis_major(self):
        """测试回退分析：重大事件关键词"""
        analyzer = NewsAnalyzer()
        result = analyzer._fallback_analysis("突发地震预警发布")
        assert result["severity"] == "major_event"

    def test_fallback_analysis_finance(self):
        """测试回退分析：财经关键词"""
        analyzer = NewsAnalyzer()
        result = analyzer._fallback_analysis("AI芯片融资创新高")
        assert result["severity"] == "finance_tech"

    def test_fallback_analysis_default(self):
        """测试回退分析：默认社会"""
        analyzer = NewsAnalyzer()
        result = analyzer._fallback_analysis("明天的天气预报")
        assert result["severity"] == "social"

    def test_heuristic_severity(self):
        """测试启发式严重度判断"""
        analyzer = NewsAnalyzer()
        assert analyzer._heuristic_severity("今天地震了") == NewsSeverity.MAJOR_EVENT
        assert analyzer._heuristic_severity("股市大涨") == NewsSeverity.FINANCE_TECH
        assert analyzer._heuristic_severity("明星离婚八卦") == NewsSeverity.ENTERTAINMENT
        assert analyzer._heuristic_severity("社区活动通知") == NewsSeverity.SOCIAL

    def test_build_broadcast_prompt(self):
        """测试播报提示生成"""
        analyzer = NewsAnalyzer()
        anchor = ANIMAL_ANCHORS[NewsSeverity.SOCIAL]
        prompt = analyzer._build_broadcast_prompt(
            anchor, {"summary": "测试新闻摘要"}
        )
        assert "猫头鹰主播" in prompt
        assert "测试新闻摘要" in prompt
        assert "播报" in prompt or "脚本" in prompt


class TestNewsAnalysisResult:
    """NewsAnalysisResult 数据类测试"""

    def test_to_dict(self):
        """测试 to_dict 序列化"""
        anchor = ANIMAL_ANCHORS[NewsSeverity.ENTERTAINMENT]
        result = NewsAnalysisResult(
            severity=NewsSeverity.ENTERTAINMENT,
            confidence=0.85,
            anchor=anchor,
            summary="娱乐新闻测试",
            keywords=["娱乐", "八卦"],
            suggested_title="娱乐速递",
            broadcast_script_prompt="测试 prompt",
        )
        d = result.to_dict()
        assert d["severity"] == "entertainment"
        assert d["confidence"] == 0.85
        assert d["anchor"]["name"] == "柴犬主播"
        assert "娱乐" in d["severity_label"]
