"""
脚本改编模块

将原始内容改写为适合动漫角色演绎的脚本：
- 保持原意
- 适配角色语气
- 生成对话脚本和旁白
"""

from dataclasses import dataclass, field
from typing import Optional

from openai import AsyncOpenAI

from ..config import settings
from .extractor import ExtractedContent


@dataclass
class ScriptLine:
    """脚本中的一行"""
    speaker: str            # 角色名
    text: str               # 台词
    emotion: str = "neutral"  # 情绪
    action: Optional[str] = None  # 动作描述


@dataclass
class AdaptedScript:
    """改编后的脚本"""
    title: str
    characters: list[dict]  # [{name, emoji, voice_id, description}]
    lines: list[ScriptLine]
    narration: list[str] = field(default_factory=list)  # 旁白
    background_mood: str = "bright"  # 背景氛围
    subtitle_style: str = "anime"  # 字幕风格

    def to_prompt(self) -> str:
        """转为给 TTS/视频合成的 prompt"""
        parts = [f"【{self.title}】\n"]
        for line in self.lines:
            emoji = ""
            for char in self.characters:
                if char["name"] == line.speaker:
                    emoji = char.get("emoji", "")
            parts.append(f"{emoji}{line.speaker}（{line.emotion}）：{line.text}")
        return "\n".join(parts)


class ScriptAdapter:
    """脚本改编器"""

    CHARACTER_TEMPLATES = {
        "tabby_cat": {
            "name": "狸花猫",
            "emoji": "🐱",
            "personality": "活泼好动，伶牙俐齿，喜欢调侃",
            "speech_style": "语速较快，语气俏皮，爱用'喵'结尾",
            "voice": "zh-CN-XiaoxiaoNeural",
        },
        "brown_bear": {
            "name": "棕熊",
            "emoji": "🐻",
            "personality": "稳重憨厚，声音低沉，不怒自威",
            "speech_style": "语速缓慢，字正腔圆，偶尔犯困",
            "voice": "zh-CN-YunxiNeural",
        },
        "little_fox": {
            "name": "小狐狸",
            "emoji": "🦊",
            "personality": "机灵狡猾，消息灵通，爱八卦",
            "speech_style": "语速快，音调高，爱用反问句",
            "voice": "zh-CN-XiaoxiaoNeural",
        },
        "panda": {
            "name": "熊猫",
            "emoji": "🐼",
            "personality": "呆萌可爱，憨态可掬，慵懒随性",
            "speech_style": "慢悠悠，软萌，爱吃竹子",
            "voice": "zh-CN-XiaoyiNeural",
        },
        "owl": {
            "name": "猫头鹰",
            "emoji": "🦉",
            "personality": "博学多识，严肃专业，偶尔毒舌",
            "speech_style": "学术化表达，喜欢引经据典",
            "voice": "zh-CN-YunxiNeural",
        },
        "shiba_inu": {
            "name": "柴犬",
            "emoji": "🐶",
            "personality": "阳光开朗，忠诚热情，带点小幽默",
            "speech_style": "语气明快，带感叹词'汪'，偶尔自黑",
            "voice": "zh-CN-YunjianNeural",
        },
        "rabbit": {
            "name": "兔子",
            "emoji": "🐰",
            "personality": "温柔细腻，善良敏感，偶尔害羞",
            "speech_style": "轻声细语，用词文雅，带'呢''呀'语气词",
            "voice": "zh-CN-XiaochenNeural",
        },
        "penguin": {
            "name": "企鹅",
            "emoji": "🐧",
            "personality": "憨态可掬，偶尔出糗，但关键时刻很靠谱",
            "speech_style": "有点结巴的萌感，喜欢说'呃...'，带数据控倾向",
            "voice": "zh-CN-XiaoyiNeural",
        },
        "lion": {
            "name": "雄狮",
            "emoji": "🦁",
            "personality": "威严庄重，王者风范，公正不阿",
            "speech_style": "字正腔圆，语气坚定，播报级发音",
            "voice": "zh-CN-YunyangNeural",
        },
    }

    def __init__(self):
        self.llm = AsyncOpenAI(
            api_key=settings.llm_api_key or "not-needed",
            base_url=settings.llm_base_url,
        )

    async def adapt(
        self,
        content: ExtractedContent,
        character: str = "tabby_cat",
        character_count: int = 2,
        style: str = "funny",
    ) -> AdaptedScript:
        """改编内容为动漫脚本"""
        char_info = self.CHARACTER_TEMPLATES.get(character, self.CHARACTER_TEMPLATES["tabby_cat"])

        prompt = self._build_prompt(content, char_info, character_count, style)

        resp = await self.llm.chat.completions.create(
            model=settings.llm_model,
            messages=[{
                "role": "system",
                "content": "你是一个专业的动画脚本编剧。把用户提供的内容改编成有趣的动漫角色对话脚本。"
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.8,
            max_tokens=2000,
        )

        script_text = resp.choices[0].message.content
        mood = "bright" if style == "funny" else "calm"
        return self._parse_script(script_text, char_info, character_count, background_mood=mood)

    async def adapt_news(
        self,
        content: ExtractedContent,
        character: str = "shiba_inu",
        broadcast_style: str = "轻松调侃",
    ) -> AdaptedScript:
        """将新闻改编为动物主播播报脚本"""
        char_info = self.CHARACTER_TEMPLATES.get(character, self.CHARACTER_TEMPLATES["shiba_inu"])

        # 新闻播报风格 prompt
        news_prompt = f"""你是一个动物新闻主播的脚本编剧。请将以下新闻改编成{char_info['name']}{char_info['emoji']}主播的播报脚本。

【角色设定】
- 主播：{char_info['name']} {char_info['emoji']}
- 性格：{char_info['personality']}
- 说话风格：{char_info['speech_style']}
- 播报风格：{broadcast_style}

【原始新闻】
{content.text[:2000]}

【改编要求】
1. 开场打招呼，介绍自己是{char_info['name']}主播
2. 用{char_info['name']}的语气播报新闻
3. 保持新闻事实准确
4. 适合 30-90 秒短视频
5. 以动物卖萌的方式增强趣味性
6. 结尾有标志性告别语

请用以下格式输出：
---
标题：xxx
{char_info['name']}（情绪）：台词
...
---

注意只保留一位主播（{char_info['name']}），不要多个角色。"""

        resp = await self.llm.chat.completions.create(
            model=settings.llm_model,
            messages=[{
                "role": "system",
                "content": "你是一个专业的新闻动画脚本编剧。将新闻改编成动物主播播报脚本。"
            }, {
                "role": "user",
                "content": news_prompt
            }],
            temperature=0.7,
            max_tokens=2000,
        )

        script_text = resp.choices[0].message.content
        # 新闻播报用偏正式背景
        return self._parse_script(script_text, char_info, 1, background_mood="news")  # 单个主播

    def _build_prompt(
        self, content: ExtractedContent, char_info: dict, char_count: int, style: str
    ) -> str:
        """构建 LLM prompt"""
        emotion_map = {
            "serious": "严肃庄重",
            "funny": "幽默搞笑",
            "happy": "开心活泼",
            "sad": "感人温馨",
            "neutral": "自然流畅",
        }
        tone = emotion_map.get(content.emotion, "自然流畅")

        return f"""请将以下内容改编成 {char_count} 个{char_info['name']}的对话脚本。

【原始内容】
{content.text[:2000]}

【角色设定】
- 角色：{char_info['name']} {char_info['emoji']}
- 性格：{char_info['personality']}
- 说话风格：{char_info['speech_style']}

【改编要求】
1. 保持原始内容的核心意思不变
2. 风格：{tone}（{style}）
3. 适合短视频时长（30-90秒）
4. 加入有趣的动作描述
5. 每句话配上情绪标注（开心/惊讶/严肃/搞笑/疑惑）

请用以下格式输出：
---
标题：xxx
角色1（情绪）：台词
角色2（情绪）：台词
[动作描述]
角色1（情绪）：台词
...
---
"""

    def _parse_script(
        self, script_text: str, char_info: dict, char_count: int,
        background_mood: str = "bright",
    ) -> AdaptedScript:
        """解析 LLM 输出的脚本"""
        lines = []
        characters = [char_info]
        title = "动画短片"

        # 如果多个角色，创建变体
        if char_count > 1:
            char2 = dict(char_info)
            char2["name"] = f"{char_info['name']}2号"
            if char_count > 2:
                char3 = dict(char_info)
                char3["name"] = f"{char_info['name']}3号"
                characters.append(char3)
            characters.append(char2)

        # 简单解析（生产环境用更健壮的解析器）
        for line in script_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("标题："):
                title = line.replace("标题：", "").strip()
                continue
            if line.startswith("[") and line.endswith("]"):
                continue  # 跳过动作描述行

            # 解析 "角色（情绪）：台词"
            if "：" in line or ":" in line:
                sep = "：" if "：" in line else ":"
                speaker_part, text = line.split(sep, 1)
                # 提取情绪
                emotion = "neutral"
                if "（" in speaker_part and "）" in speaker_part:
                    name_part = speaker_part.split("（")[0].strip()
                    emotion = speaker_part.split("（")[1].replace("）", "").strip()
                    speaker_part = name_part
                speaker = speaker_part.strip()
                lines.append(ScriptLine(
                    speaker=characters[0]["name"] if speaker in ["角色1", char_info["name"]] else speaker,
                    text=text.strip(),
                    emotion=emotion,
                ))

        return AdaptedScript(
            title=title,
            characters=characters,
            lines=lines,
            background_mood=background_mood,
        )
