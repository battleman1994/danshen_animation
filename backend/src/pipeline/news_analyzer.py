"""
新闻严重度分析器 + 动物匹配系统

根据 Issue #1 场景二的需求：
- 分析新闻内容的严肃程度
- 根据严重度自动匹配动物主播形象
- 生成对应的播报风格参数

新闻分级与动物匹配表：
  🟢 娱乐八卦 → 柴犬 🐕   (轻松调侃、活泼)
  🟡 社会民生 → 猫头鹰 🦉 (温和稳重、亲切)
  🟠 财经科技 → 企鹅 🐧   (严谨专业、数据感)
  🔴 重大事件 → 雄狮 🦁   (庄重严肃、权威)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from openai import AsyncOpenAI

from ..config import settings


class NewsSeverity(str, Enum):
    """新闻严重度等级"""
    ENTERTAINMENT = "entertainment"   # 🟢 娱乐八卦
    SOCIAL = "social"                 # 🟡 社会民生
    FINANCE_TECH = "finance_tech"     # 🟠 财经科技
    MAJOR_EVENT = "major_event"       # 🔴 重大事件


@dataclass
class AnimalAnchor:
    """动物主播配置"""
    animal_id: str
    name: str
    emoji: str
    severity: NewsSeverity
    personality: str
    speech_style: str
    voice_id: str
    broadcast_tone: str  # 播报语气描述


# ── 动物主播预设库 ──

ANIMAL_ANCHORS: dict[NewsSeverity, AnimalAnchor] = {
    NewsSeverity.ENTERTAINMENT: AnimalAnchor(
        animal_id="shiba_inu",
        name="柴犬主播",
        emoji="🐕",
        severity=NewsSeverity.ENTERTAINMENT,
        personality="活泼开朗，爱八卦，喜欢调侃，精力充沛",
        speech_style="语速快、音调活泼、带笑腔、偶尔汪汪",
        voice_id="zh-CN-XiaoxiaoNeural",
        broadcast_tone="轻松调侃风：像朋友聊天一样，多用网络热词，可以适当吐槽",
    ),
    NewsSeverity.SOCIAL: AnimalAnchor(
        animal_id="owl",
        name="猫头鹰主播",
        emoji="🦉",
        severity=NewsSeverity.SOCIAL,
        personality="温和智慧，接地气，有同理心，像个知心大叔",
        speech_style="语速适中、语气亲切、娓娓道来",
        voice_id="zh-CN-YunxiNeural",
        broadcast_tone="温和稳重风：像邻家大叔分享身边事，语气亲切自然",
    ),
    NewsSeverity.FINANCE_TECH: AnimalAnchor(
        animal_id="penguin",
        name="企鹅主播",
        emoji="🐧",
        severity=NewsSeverity.FINANCE_TECH,
        personality="严谨专业，数据说话，理性冷静，偶尔冷幽默",
        speech_style="语速适中偏慢、用词精准、带数据分析感",
        voice_id="zh-CN-YunyangNeural",
        broadcast_tone="严谨专业风：精准传达数据，逻辑清晰，关键数字加重语气",
    ),
    NewsSeverity.MAJOR_EVENT: AnimalAnchor(
        animal_id="lion",
        name="雄狮主播",
        emoji="🦁",
        severity=NewsSeverity.MAJOR_EVENT,
        personality="庄重威严，沉稳有力，一诺千金，不怒自威",
        speech_style="语速缓慢庄重、字正腔圆、有仪式感",
        voice_id="zh-CN-YunxiNeural",
        broadcast_tone="庄重严肃风：字字有力，正式规范，体现事件重要性",
    ),
}


@dataclass
class NewsAnalysisResult:
    """新闻分析结果"""
    severity: NewsSeverity
    confidence: float  # 0-1 置信度
    anchor: AnimalAnchor
    summary: str  # 新闻摘要
    keywords: list[str]
    suggested_title: str
    broadcast_script_prompt: str  # 给 LLM 的播报脚本生成提示

    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "severity_label": _severity_label(self.severity),
            "confidence": self.confidence,
            "anchor": {
                "animal_id": self.anchor.animal_id,
                "name": self.anchor.name,
                "emoji": self.anchor.emoji,
                "voice_id": self.anchor.voice_id,
                "broadcast_tone": self.anchor.broadcast_tone,
            },
            "summary": self.summary,
            "keywords": self.keywords,
            "suggested_title": self.suggested_title,
        }


def _severity_label(severity: NewsSeverity) -> str:
    labels = {
        NewsSeverity.ENTERTAINMENT: "🟢 娱乐八卦",
        NewsSeverity.SOCIAL: "🟡 社会民生",
        NewsSeverity.FINANCE_TECH: "🟠 财经科技",
        NewsSeverity.MAJOR_EVENT: "🔴 重大事件",
    }
    return labels.get(severity, "⚪ 未分类")


class NewsAnalyzer:
    """
    新闻严重度分析器

    通过 LLM 分析新闻文本的严肃程度，
    自动匹配最合适的动物主播形象和播报风格。
    """

    SEVERITY_ANALYSIS_PROMPT = """你是一位专业的新闻内容分析专家。请分析以下新闻内容，从以下维度评估：

1. **话题领域**：政治/经济/科技/娱乐/社会/国际/体育
2. **严肃程度**（1-10分）：1=纯娱乐八卦，10=重大政治/灾难事件
3. **情感基调**：正面/负面/中性
4. **受众影响**：广泛/特定群体/个人

请根据严重程度分类：
- 1-3分 → "entertainment"（娱乐八卦）
- 4-6分 → "social"（社会民生）
- 7-8分 → "finance_tech"（财经科技）
- 9-10分 → "major_event"（重大事件）

返回严格的 JSON 格式（不要加 markdown 代码块标记）：
{
  "severity": "entertainment|social|finance_tech|major_event",
  "score": 整数1-10,
  "confidence": 0.0-1.0,
  "summary": "50字以内的中文摘要",
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "suggested_title": "适合动物播报的标题（15字以内）",
  "domain": "话题领域",
  "sentiment": "positive|negative|neutral"
}"""

    def __init__(self):
        self.llm = AsyncOpenAI(
            api_key=settings.llm_api_key or "not-needed",
            base_url=settings.llm_base_url,
        )

    async def analyze(self, content: str) -> NewsAnalysisResult:
        """
        分析新闻内容并匹配动物主播

        Args:
            content: 新闻文本内容

        Returns:
            NewsAnalysisResult 包含严重度、主播配置、摘要等
        """
        import json

        # 截断过长内容
        text = content[:3000] if len(content) > 3000 else content

        try:
            resp = await self.llm.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": self.SEVERITY_ANALYSIS_PROMPT},
                    {"role": "user", "content": f"请分析以下新闻内容：\n\n{text}"},
                ],
                temperature=0.2,
                max_tokens=500,
            )

            raw_output = resp.choices[0].message.content.strip()
            # 去掉可能的 markdown 代码块标记
            if raw_output.startswith("```"):
                raw_output = raw_output.split("\n", 1)[1]
                if raw_output.endswith("```"):
                    raw_output = raw_output[:-3]
            analysis = json.loads(raw_output)

        except Exception as e:
            # LLM 调用失败时做本地回退分析
            analysis = self._fallback_analysis(text)

        # 映射严重度
        severity_str = analysis.get("severity", "social")
        try:
            severity = NewsSeverity(severity_str)
        except ValueError:
            severity = self._heuristic_severity(text)

        anchor = ANIMAL_ANCHORS[severity]

        # 构建播报脚本提示
        broadcast_prompt = self._build_broadcast_prompt(anchor, analysis)

        return NewsAnalysisResult(
            severity=severity,
            confidence=float(analysis.get("confidence", 0.7)),
            anchor=anchor,
            summary=analysis.get("summary", text[:50]),
            keywords=analysis.get("keywords", []),
            suggested_title=analysis.get("suggested_title", anchor.name),
            broadcast_script_prompt=broadcast_prompt,
        )

    def _fallback_analysis(self, text: str) -> dict:
        """本地关键词匹配回退分析"""
        entertainment_keywords = [
            "八卦", "明星", "综艺", "娱乐", "吃瓜", "恋情", "搞笑",
            "段子", "趣事", "萌宠", "搞笑视频",
        ]
        major_keywords = [
            "地震", "战争", "灾难", "宣布", "主席", "总统", "重大",
            "紧急", "警告", "突发", "国家", "政府",
        ]
        finance_keywords = [
            "股市", "科技", "AI", "融资", "上市", "数据", "芯片",
            "比特币", "行情", "经济", "财报", "基金",
        ]

        text_lower = text.lower()

        if any(kw in text_lower for kw in entertainment_keywords):
            return {"severity": "entertainment", "score": 2, "confidence": 0.6,
                    "summary": text[:50], "keywords": [], "suggested_title": "娱乐速递",
                    "domain": "娱乐", "sentiment": "neutral"}
        elif any(kw in text_lower for kw in major_keywords):
            return {"severity": "major_event", "score": 9, "confidence": 0.6,
                    "summary": text[:50], "keywords": [], "suggested_title": "重大播报",
                    "domain": "重大", "sentiment": "neutral"}
        elif any(kw in text_lower for kw in finance_keywords):
            return {"severity": "finance_tech", "score": 7, "confidence": 0.5,
                    "summary": text[:50], "keywords": [], "suggested_title": "财经速览",
                    "domain": "财经科技", "sentiment": "neutral"}
        else:
            return {"severity": "social", "score": 5, "confidence": 0.4,
                    "summary": text[:50], "keywords": [], "suggested_title": "民生关注",
                    "domain": "社会", "sentiment": "neutral"}

    def _heuristic_severity(self, text: str) -> NewsSeverity:
        """启发式严重度判断（极简规则）"""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["地震", "战争", "灾难", "总统", "宣布"]):
            return NewsSeverity.MAJOR_EVENT
        if any(kw in text_lower for kw in ["股市", "科技", "AI", "芯片", "经济"]):
            return NewsSeverity.FINANCE_TECH
        if any(kw in text_lower for kw in ["明星", "八卦", "综艺", "搞笑"]):
            return NewsSeverity.ENTERTAINMENT
        return NewsSeverity.SOCIAL

    def _build_broadcast_prompt(
        self, anchor: AnimalAnchor, analysis: dict
    ) -> str:
        """构建播报脚本生成的 prompt"""
        return f"""你是{anchor.emoji}{anchor.name}，一只{anchor.personality}的动物新闻主播。

【播报风格要求】
- 语气：{anchor.broadcast_tone}
- 说话特点：{anchor.speech_style}

【今日新闻摘要】
{analysis.get('summary', '')}

【任务】
将以上新闻改编成一段 60-90 秒的动物主播播报脚本：
1. 开场白（活泼/正式取决于新闻类型）
2. 新闻主体（保持事实准确，适当添加动物视角的趣味评论）
3. 结束语
4. 全程用「{anchor.name}」的第一人称播报

请用以下格式输出：
---
【开场】
主播台词...

【新闻播报】
主播台词...

【趣味点评】
主播台词...

【结束】
主播台词...
---"""

    @staticmethod
    def get_all_anchors() -> dict[str, AnimalAnchor]:
        """获取所有动物主播的配置"""
        return {sev.value: anchor for sev, anchor in ANIMAL_ANCHORS.items()}


# 便捷函数
async def analyze_news(content: str) -> NewsAnalysisResult:
    """快速分析新闻的便捷函数"""
    analyzer = NewsAnalyzer()
    return await analyzer.analyze(content)
