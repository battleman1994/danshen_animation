"""
多模态提示词生成模块

将输入内容（文字/对话/新闻）分析后，生成可直接提交给第三方 AI 视频生成 API 的完整提示词。
整个视频（角色表演、配音、字幕、运镜）全部由外部 API 一次性生成。

支持多种 LLM 后端：DeepSeek / OpenAI / Anthropic，各有不同的输入类型支持能力。
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from ..config import settings

logger = logging.getLogger(__name__)

CHARACTER_INFO = {
    "tabby_cat": {"name": "狸花猫", "emoji": "🐱", "personality": "活泼好动，伶牙俐齿，喜欢调侃", "appearance": "一只可爱的橘色虎斑猫，绿色大眼睛，橙色条纹毛发，chibi动漫风格"},
    "brown_bear": {"name": "棕熊", "emoji": "🐻", "personality": "稳重憨厚，声音低沉，不怒自威", "appearance": "一只稳重的棕色熊，戴圆眼镜，穿西装，chibi动漫风格"},
    "little_fox": {"name": "小狐狸", "emoji": "🦊", "personality": "机灵狡猾，消息灵通，爱八卦", "appearance": "一只机灵的橙色小狐狸，大耳朵，蓬松尾巴，chibi动漫风格"},
    "panda": {"name": "熊猫", "emoji": "🐼", "personality": "呆萌可爱，憨态可掬，慵懒随性", "appearance": "一只呆萌的熊猫，黑白毛发，慵懒眼神，kawaii风格"},
    "rabbit": {"name": "兔子", "emoji": "🐰", "personality": "温柔细腻，善良敏感，偶尔害羞", "appearance": "一只温柔的白色兔子，长耳朵，粉色鼻子，梦幻柔光风格"},
    "shiba_inu": {"name": "柴犬", "emoji": "🐶", "personality": "阳光开朗，忠诚热情，带点小幽默", "appearance": "一只阳光开朗的柴犬，奶油色毛发，蝴蝶领结，kawaii风格"},
    "owl": {"name": "猫头鹰", "emoji": "🦉", "personality": "博学多识，严肃专业，偶尔毒舌", "appearance": "一只博学的猫头鹰教授，半月眼镜，棕色羽毛，穿学术袍"},
    "penguin": {"name": "企鹅", "emoji": "🐧", "personality": "憨态可掬，偶尔出糗，但关键时刻很靠谱", "appearance": "一只可爱的帝企鹅幼崽，灰色绒毛，小眼镜，冰蓝背景"},
    "lion": {"name": "雄狮", "emoji": "🦁", "personality": "威严庄重，王者风范，公正不阿", "appearance": "一只威严的金鬃雄狮，王者表情，穿正式主播西装，戏剧性灯光"},
}

STYLE_DESCRIPTIONS = {
    "funny": "幽默搞笑风格，节奏轻快活泼，画面明亮色彩丰富，角色表情夸张有趣",
    "serious": "严肃庄重风格，画面沉稳大气，色调偏冷，信息传达清晰准确",
    "cute": "可爱卖萌风格，粉色柔和色调，角色Q萌，画面充满童趣和温暖",
    "news": "新闻播报风格，专业严谨，画面干净简洁，类似新闻演播室效果",
    "auto": "根据内容自动选择最合适的风格",
}

ALL_SOURCE_TYPES = ["text", "web_link", "image", "douyin_video"]
TEXT_ONLY_SOURCE_TYPES = ["text", "web_link"]


@dataclass
class LLMModelInfo:
    """LLM 模型元信息"""
    id: str
    name: str
    provider: str                          # anthropic, openai, deepseek
    supported_input_types: list[str]       # 支持的 SourceType 列表
    mode: str = "remote"                   # "local" = 用户自配 API key, "remote" = 平台提供
    requires_config: list[str] = field(default_factory=list)  # local 模式需要的配置项
    available: bool = True


# 已注册的 LLM 模型列表
LLM_MODELS: list[LLMModelInfo] = [
    LLMModelInfo(
        id="deepseek-v4-pro[1m]",
        name="DeepSeek V4 Pro",
        provider="deepseek",
        supported_input_types=TEXT_ONLY_SOURCE_TYPES,
        mode="remote",
    ),
    LLMModelInfo(
        id="deepseek-chat",
        name="DeepSeek Chat",
        provider="deepseek",
        supported_input_types=TEXT_ONLY_SOURCE_TYPES,
        mode="remote",
    ),
    LLMModelInfo(
        id="gpt-4o",
        name="GPT-4o",
        provider="openai",
        supported_input_types=ALL_SOURCE_TYPES,
        mode="local",
        requires_config=["llm_api_key"],
    ),
    LLMModelInfo(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        provider="openai",
        supported_input_types=ALL_SOURCE_TYPES,
        mode="local",
        requires_config=["llm_api_key"],
    ),
    LLMModelInfo(
        id="claude-opus-4-7",
        name="Claude Opus 4.7",
        provider="anthropic",
        supported_input_types=ALL_SOURCE_TYPES,
        mode="local",
        requires_config=["llm_api_key"],
    ),
    LLMModelInfo(
        id="claude-sonnet-4-6",
        name="Claude Sonnet 4.6",
        provider="anthropic",
        supported_input_types=ALL_SOURCE_TYPES,
        mode="local",
        requires_config=["llm_api_key"],
    ),
]


def _check_local_config(requires_config: list[str]) -> bool:
    """检查本地配置项是否已设置"""
    for key in requires_config:
        val = getattr(settings, key, None)
        if not val:
            return False
    return True


def list_llm_models() -> list[dict]:
    """列出所有可用 LLM 模型及其能力"""
    result = []
    for m in LLM_MODELS:
        available = m.available
        if m.mode == "local":
            available = _check_local_config(m.requires_config)
        result.append({
            "id": m.id,
            "name": m.name,
            "provider": m.provider,
            "supported_input_types": m.supported_input_types,
            "mode": m.mode,
            "requires_config": m.requires_config,
            "available": available,
        })
    return result


def get_llm_model(model_id: str | None = None) -> LLMModelInfo:
    """获取指定 LLM 模型信息，默认使用配置中的模型"""
    target = model_id or settings.llm_model
    for m in LLM_MODELS:
        if m.id == target:
            return m
    return LLM_MODELS[0]


def supports_input_type(model_id: str, source_type: str) -> bool:
    """检查模型是否支持给定的输入类型"""
    model = get_llm_model(model_id)
    return source_type in model.supported_input_types


@dataclass
class VideoPrompt:
    """生成的视频提示词"""
    prompt: str
    title: str
    style: str
    duration_estimate: int
    model_used: str = ""


class PromptBuilder:
    """多模态内容分析 → 视频提示词生成（支持多种 LLM 后端）"""

    def __init__(self, model_id: str | None = None):
        self.model_id = model_id or settings.llm_model
        self.model_info = get_llm_model(self.model_id)

    async def build(
        self,
        content: str,
        character: str = "tabby_cat",
        style: str = "funny",
        scene_mode: str = "auto",
    ) -> VideoPrompt:
        char_info = CHARACTER_INFO.get(character, CHARACTER_INFO["tabby_cat"])
        style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["funny"])

        system_prompt = """你是一个专业的 AI 视频生成提示词工程师。你的任务是将用户提供的内容，转化为一个完整的、可直接提交给 AI 视频生成 API 的英文提示词。

要求：
1. 提示词必须是英文（因为主流视频生成 API 对英文支持最好）
2. 提示词应描述完整的视频画面：角色外貌、动作表演、场景背景、镜头运动、光影氛围
3. 提示词应引导 API 在生成视频时自然包含配音和字幕
4. 提示词长度控制在 200-400 词之间
5. 角色必须全程出现在画面中，表演自然流畅
6. 视频风格要匹配指定风格

输出 JSON 格式（不要 markdown 标记）：
{"prompt": "完整英文提示词", "title": "中文视频标题", "duration_estimate": 15}
duration_estimate 根据内容长度估算（短新闻 10-15s，对话 15-30s，长内容 30-60s）。"""

        user_prompt = f"""请为以下内容生成 AI 视频提示词：

【内容】
{content[:3000]}

【角色设定】
- 名称：{char_info['name']} {char_info['emoji']}
- 性格：{char_info['personality']}
- 外貌：{char_info['appearance']}

【视频风格】
{style_desc}

【场景模式】
{scene_mode}

请生成提示词，让视频 API 一次性生成完整的动漫风格视频（包含角色表演、配音、字幕）。"""

        raw = await self._call_llm(system_prompt, user_prompt)
        return self._parse(raw, character, style)

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        provider = self.model_info.provider

        if provider == "anthropic":
            return await self._call_anthropic(system_prompt, user_prompt)
        elif provider == "openai":
            return await self._call_openai(system_prompt, user_prompt)
        elif provider == "deepseek":
            return await self._call_deepseek(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(
            api_key=settings.llm_api_key or "not-needed",
            base_url=settings.llm_base_url,
        )
        resp = await client.messages.create(
            model=self.model_id,
            max_tokens=2000,
            temperature=0.8,
            system="你是一个严格的 JSON 输出机器。只输出符合要求格式的 JSON，不输出 markdown 标记、解释或额外文字。",
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(
            block.text for block in resp.content if hasattr(block, "text")
        ).strip()

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.llm_api_key or "not-needed",
            base_url=settings.llm_base_url,
        )
        resp = await client.chat.completions.create(
            model=self.model_id,
            max_tokens=2000,
            temperature=0.8,
            messages=[
                {"role": "system", "content": "你是一个严格的 JSON 输出机器。只输出符合要求格式的 JSON，不输出 markdown 标记、解释或额外文字。"},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content.strip() if resp.choices else ""

    async def _call_deepseek(self, system_prompt: str, user_prompt: str) -> str:
        # DeepSeek 使用 Anthropic 兼容 API
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(
            api_key=settings.llm_api_key or "not-needed",
            base_url=settings.llm_base_url,
        )
        resp = await client.messages.create(
            model=self.model_id,
            max_tokens=2000,
            temperature=0.8,
            system="你是一个严格的 JSON 输出机器。只输出符合要求格式的 JSON，不输出 markdown 标记、解释或额外文字。",
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(
            block.text for block in resp.content if hasattr(block, "text")
        ).strip()

    def _parse(self, raw: str, character: str, style: str) -> VideoPrompt:
        if not raw:
            raise ValueError("LLM returned no text content")

        json_str = raw
        if "```" in raw:
            match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
            if match:
                json_str = match.group(1).strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            brace_start = json_str.find("{")
            brace_end = json_str.rfind("}")
            if brace_start != -1 and brace_end != -1:
                data = json.loads(json_str[brace_start:brace_end + 1])
            else:
                raise ValueError(f"LLM did not return valid JSON: {raw[:300]}")

        return VideoPrompt(
            prompt=data.get("prompt", ""),
            title=data.get("title", "未命名视频"),
            style=style,
            duration_estimate=data.get("duration_estimate", 15),
            model_used=self.model_id,
        )
