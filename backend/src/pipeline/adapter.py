import json
import re
import logging
from dataclasses import dataclass, field
from typing import Optional

from anthropic import AsyncAnthropic

from ..config import settings
from .storyboard import Storyboard, StoryboardScene

logger = logging.getLogger(__name__)


@dataclass
class ScriptLine:
    speaker: str
    text: str
    emotion: str = "neutral"
    action: Optional[str] = None


@dataclass
class AdaptedScript:
    title: str
    characters: list[dict]
    lines: list[ScriptLine]
    narration: list[str] = field(default_factory=list)
    background_mood: str = "bright"
    subtitle_style: str = "anime"

    def to_prompt(self) -> str:
        parts = [f"【{self.title}】\n"]
        for line in self.lines:
            emoji = ""
            for char in self.characters:
                if char["name"] == line.speaker:
                    emoji = char.get("emoji", "")
            parts.append(f"{emoji}{line.speaker}（{line.emotion}）：{line.text}")
        return "\n".join(parts)

CHARACTER_TEMPLATES = {
    "tabby_cat": {
        "name": "狸花猫", "emoji": "🐱",
        "personality": "活泼好动，伶牙俐齿，喜欢调侃",
        "speech_style": "语速较快，语气俏皮，爱用'喵'结尾",
        "voice": "zh-CN-XiaoxiaoNeural",
    },
    "brown_bear": {
        "name": "棕熊", "emoji": "🐻",
        "personality": "稳重憨厚，声音低沉，不怒自威",
        "speech_style": "语速缓慢，字正腔圆，偶尔犯困",
        "voice": "zh-CN-YunxiNeural",
    },
    "little_fox": {
        "name": "小狐狸", "emoji": "🦊",
        "personality": "机灵狡猾，消息灵通，爱八卦",
        "speech_style": "语速快，音调高，爱用反问句",
        "voice": "zh-CN-XiaoxiaoNeural",
    },
    "panda": {
        "name": "熊猫", "emoji": "🐼",
        "personality": "呆萌可爱，憨态可掬，慵懒随性",
        "speech_style": "慢悠悠，软萌，爱吃竹子",
        "voice": "zh-CN-XiaoyiNeural",
    },
    "owl": {
        "name": "猫头鹰", "emoji": "🦉",
        "personality": "博学多识，严肃专业，偶尔毒舌",
        "speech_style": "学术化表达，喜欢引经据典",
        "voice": "zh-CN-YunxiNeural",
    },
    "shiba_inu": {
        "name": "柴犬", "emoji": "🐶",
        "personality": "阳光开朗，忠诚热情，带点小幽默",
        "speech_style": "语气明快，带感叹词'汪'，偶尔自黑",
        "voice": "zh-CN-YunjianNeural",
    },
    "rabbit": {
        "name": "兔子", "emoji": "🐰",
        "personality": "温柔细腻，善良敏感，偶尔害羞",
        "speech_style": "轻声细语，用词文雅，带'呢''呀'语气词",
        "voice": "zh-CN-XiaochenNeural",
    },
    "penguin": {
        "name": "企鹅", "emoji": "🐧",
        "personality": "憨态可掬，偶尔出糗，但关键时刻很靠谱",
        "speech_style": "有点结巴的萌感，喜欢说'呃...'，带数据控倾向",
        "voice": "zh-CN-XiaoyiNeural",
    },
    "lion": {
        "name": "雄狮", "emoji": "🦁",
        "personality": "威严庄重，王者风范，公正不阿",
        "speech_style": "字正腔圆，语气坚定，播报级发音",
        "voice": "zh-CN-YunyangNeural",
    },
}


class ScriptAdapter:
    def __init__(self):
        self.llm = AsyncAnthropic(
            api_key=settings.llm_api_key or "not-needed",
            base_url=settings.llm_base_url,
        )

    async def adapt(self, text: str, character: str = "tabby_cat", style: str = "funny") -> Storyboard:
        char_info = CHARACTER_TEMPLATES.get(character, CHARACTER_TEMPLATES["tabby_cat"])

        style_descriptions = {
            "funny": "幽默搞笑，台词要有梗，节奏轻快",
            "serious": "严肃庄重，台词正式，信息量足",
            "cute": "可爱卖萌，台词软萌，充满童趣",
            "news": "新闻播报风格，事实准确，语气专业",
        }
        style_desc = style_descriptions.get(style, style_descriptions["funny"])

        prompt = f"""你是一个专业的动画分镜编剧。将以下文字改编成{char_info['name']}{char_info['emoji']}的动漫短视频分镜脚本。

【输入文字】
{text[:2000]}

【角色设定】
- 角色：{char_info['name']} {char_info['emoji']}
- 性格：{char_info['personality']}
- 说话风格：{char_info['speech_style']}
- 整体风格：{style_desc}

【分镜规则】
1. 每段 3-5 秒，总时长不超过 60 秒
2. 对话使用角色语气改写，保持原意
3. 每段配上情绪（happy/sad/funny/serious/surprised/angry/neutral）
4. 每段配上动作描述（简洁动词短语，如 waving_paw, nodding, pointing, shrugging, jumping, sitting）
5. 每段配上简单背景描述（如 sunny_park, cozy_room, city_street, simple_studio）
6. 每段配上镜头类型（medium_shot/close_up/wide_shot）
7. 角色固定为 {character}

请只输出以下 JSON 格式（不要 markdown 标记，不要额外解释）：
{{"scenes":[{{"index":1,"duration_s":4,"dialogue":"台词","character":"{character}","emotion":"happy","action":"waving_paw","background":"sunny_park","camera":"medium_shot"}}],"total_duration_s":4,"style":"{style}","title":"视频标题"}}"""

        resp = await self.llm.messages.create(
            model=settings.llm_model,
            max_tokens=2000,
            temperature=0.8,
            system="你是一个严格的 JSON 输出机器。只输出符合要求格式的 JSON，不输出 markdown 标记、解释或额外文字。",
            messages=[{"role": "user", "content": prompt}],
        )

        text_parts = []
        for block in resp.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)
        raw = "".join(text_parts).strip()
        if not raw:
            raise ValueError("LLM returned no text content (all thinking, no output)")
        return self._parse_storyboard(raw, character, style)

    def _parse_storyboard(self, raw: str, character: str, style: str) -> Storyboard:
        json_str = raw
        if "```" in raw:
            match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
        json_str = json_str.strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            brace_start = json_str.find("{")
            brace_end = json_str.rfind("}")
            if brace_start != -1 and brace_end != -1:
                data = json.loads(json_str[brace_start:brace_end + 1])
            else:
                raise ValueError(f"LLM did not return valid JSON: {raw[:300]}")

        try:
            return Storyboard.from_dict(data)
        except Exception as e:
            raise ValueError(f"Storyboard validation failed: {e}\nRaw JSON: {json.dumps(data, ensure_ascii=False)[:500]}")
