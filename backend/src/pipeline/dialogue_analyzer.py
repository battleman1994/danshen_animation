"""
对话分析器

从视频/音频中提取对话信息，分析说话人特征，
为"场景一：抖音对话 → 狸花猫剧场"提供支持。

功能：
- 多说话人检测与分离
- 对话节奏分析
- 人物特征提取（性别、情绪、语速）
- 角色映射建议
"""

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SpeakerInfo:
    """说话人信息"""
    speaker_id: int
    gender: str = "unknown"        # male, female, unknown
    emotion_profile: str = "neutral"  # 主导情绪
    speech_rate: str = "normal"    # fast, normal, slow
    utterance_count: int = 0       # 发言次数
    sample_text: str = ""          # 发言样例

    def to_dict(self) -> dict:
        return {
            "speaker_id": self.speaker_id,
            "gender": self.gender,
            "emotion_profile": self.emotion_profile,
            "speech_rate": self.speech_rate,
            "utterance_count": self.utterance_count,
            "sample_text": self.sample_text[:100],
        }


@dataclass
class DialogueAnalysis:
    """对话分析结果"""
    speaker_count: int
    speakers: list[SpeakerInfo]
    total_duration: float = 0.0
    dialogue_density: str = "normal"  # sparse, normal, dense
    turn_taking_pattern: str = "balanced"  # balanced, one_dominant, rapid_exchange
    recommended_character: str = "tabby_cat"
    character_count: int = 2
    background_mood: str = "bright"

    def to_dict(self) -> dict:
        return {
            "speaker_count": self.speaker_count,
            "speakers": [s.to_dict() for s in self.speakers],
            "total_duration": self.total_duration,
            "dialogue_density": self.dialogue_density,
            "turn_taking_pattern": self.turn_taking_pattern,
            "recommended_character": self.recommended_character,
            "character_count": self.character_count,
            "background_mood": self.background_mood,
        }


class DialogueAnalyzer:
    """
    对话分析器

    分析视频中的对话特征，为角色替换提供参数：
    - 检测说话人数目
    - 分析对话节奏
    - 推荐匹配的动漫角色
    """

    # 基于对话特征的角色匹配规则
    CHARACTER_MATCH_RULES = [
        {
            "conditions": {"speaker_count": 2, "pattern": "rapid_exchange"},
            "recommend": "tabby_cat",
            "count": 2,
            "mood": "bright",
            "reason": "两只狸花猫适合快节奏搞笑对话",
        },
        {
            "conditions": {"speaker_count": 2, "pattern": "balanced"},
            "recommend": "little_fox",
            "count": 2,
            "mood": "bright",
            "reason": "小狐狸适合机灵俏皮的对话",
        },
        {
            "conditions": {"speaker_count": 1},
            "recommend": "owl",
            "count": 1,
            "mood": "calm",
            "reason": "单人独白用猫头鹰讲故事",
        },
        {
            "conditions": {"speaker_count": 3, "speaker_count_gte": 3},
            "recommend": "panda",
            "count": 3,
            "mood": "bright",
            "reason": "多人讨论用熊猫群像",
        },
    ]

    async def analyze_dialogue(
        self,
        transcript_lines: list[dict],
        total_duration: float = 0.0,
    ) -> DialogueAnalysis:
        """
        分析对话脚本

        Args:
            transcript_lines: Whisper 转写结果，每行含 speaker/text
            total_duration: 视频总时长（秒）

        Returns:
            DialogueAnalysis 对话分析结果
        """
        if not transcript_lines:
            return self._empty_analysis()

        # 1. 统计说话人
        speaker_map: dict[int, list[dict]] = {}
        for line in transcript_lines:
            spk_id = line.get("speaker", line.get("speaker_id", 0))
            if spk_id not in speaker_map:
                speaker_map[spk_id] = []
            speaker_map[spk_id].append(line)

        # 2. 构建说话人信息
        speakers = []
        for spk_id, utterances in speaker_map.items():
            u_count = len(utterances)
            samples = [u.get("text", "") for u in utterances[:3]]
            sample_text = " | ".join(samples)

            # 简单启发式分析
            emotion = self._detect_emotion(sample_text)
            rate = self._estimate_speech_rate(utterances, total_duration)

            speakers.append(SpeakerInfo(
                speaker_id=spk_id,
                gender=self._guess_gender(sample_text),
                emotion_profile=emotion,
                speech_rate=rate,
                utterance_count=u_count,
                sample_text=sample_text,
            ))

        speaker_count = len(speakers)

        # 3. 分析对话模式
        density = self._analyze_density(transcript_lines, total_duration)
        turn_pattern = self._analyze_turn_pattern(transcript_lines)

        # 4. 推荐角色
        recommendation = self._recommend_character(speaker_count, turn_pattern)

        return DialogueAnalysis(
            speaker_count=speaker_count,
            speakers=speakers,
            total_duration=total_duration,
            dialogue_density=density,
            turn_taking_pattern=turn_pattern,
            recommended_character=recommendation["character"],
            character_count=recommendation["count"],
            background_mood=recommendation["mood"],
        )

    def _empty_analysis(self) -> DialogueAnalysis:
        return DialogueAnalysis(
            speaker_count=1,
            speakers=[SpeakerInfo(speaker_id=0)],
            recommended_character="tabby_cat",
            character_count=1,
        )

    def _detect_emotion(self, text: str) -> str:
        """简单情绪检测"""
        text_lower = text.lower()
        positive_words = ["哈哈", "笑", "开心", "好", "棒", "喜欢", "爱", "😊"]
        negative_words = ["难过", "伤心", "哭", "气", "烦", "讨厌", "😢"]
        question_words = ["?", "？", "什么", "怎么", "为什么"]

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        q_count = sum(1 for w in question_words if w in text_lower)

        if pos_count > neg_count:
            return "happy"
        elif neg_count > pos_count:
            return "sad"
        elif q_count > 2:
            return "surprised"
        return "neutral"

    def _guess_gender(self, text: str) -> str:
        """简单性别猜测（中文性别特征词）"""
        female_indicators = ["人家", "嘛", "呀", "呢", "啦"]
        # 注意：这只是非常粗略的启发式方法
        score = sum(1 for w in female_indicators if w in text)
        if score >= 2:
            return "female"
        return "unknown"

    def _estimate_speech_rate(
        self, utterances: list[dict], total_duration: float
    ) -> str:
        """估算语速"""
        if total_duration <= 0:
            return "normal"

        total_chars = sum(len(u.get("text", "")) for u in utterances)
        chars_per_second = total_chars / max(total_duration, 1)

        if chars_per_second < 3:
            return "slow"
        elif chars_per_second > 8:
            return "fast"
        return "normal"

    def _analyze_density(
        self, transcript_lines: list[dict], total_duration: float
    ) -> str:
        """分析对话密度"""
        if total_duration <= 0:
            return "normal"

        utterances_per_min = len(transcript_lines) / (total_duration / 60)

        if utterances_per_min > 15:
            return "dense"
        elif utterances_per_min < 5:
            return "sparse"
        return "normal"

    def _analyze_turn_pattern(self, transcript_lines: list[dict]) -> str:
        """分析对话轮转模式"""
        if len(transcript_lines) < 3:
            return "balanced"

        # 统计轮流发言的频率
        prev_speaker = transcript_lines[0].get("speaker", 0)
        turns = 0
        same_speaker_streak = 1

        for line in transcript_lines[1:]:
            curr_speaker = line.get("speaker", 0)
            if curr_speaker != prev_speaker:
                turns += 1
                same_speaker_streak = 1
            else:
                same_speaker_streak += 1
            prev_speaker = curr_speaker

        total_lines = len(transcript_lines)
        turn_ratio = turns / max(total_lines, 1)

        if turn_ratio > 0.6:
            return "rapid_exchange"
        elif turn_ratio < 0.2:
            return "one_dominant"
        return "balanced"

    def _recommend_character(
        self, speaker_count: int, turn_pattern: str
    ) -> dict:
        """基于对话特征推荐角色"""
        # 默认推荐
        default = {"character": "tabby_cat", "count": min(speaker_count, 2), "mood": "bright"}

        for rule in self.CHARACTER_MATCH_RULES:
            conditions = rule["conditions"]
            match = True

            if "speaker_count" in conditions:
                if speaker_count != conditions["speaker_count"]:
                    match = False
            if "speaker_count_gte" in conditions and match:
                if speaker_count < conditions["speaker_count_gte"]:
                    match = False
            if "pattern" in conditions and match:
                if turn_pattern != conditions["pattern"]:
                    match = False

            if match:
                return {
                    "character": rule["recommend"],
                    "count": rule["count"],
                    "mood": rule["mood"],
                }

        return default
