"""
视频提示词生成模块 — 真实动物风格

将用户输入（文字/网页内容）转化为高质量英文视频提示词，
供 Kling / Runway / Jimeng / Hailuo 等第三方视频生成 API 使用。

核心风格：真实猫咪（或熊猫等动物）+ 可爱生动 + 搞笑萌动。
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from ..config import settings

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 角色系统 — 真实动物 + 可爱生动
# ═══════════════════════════════════════════════════════════════════════════════

CHARACTER_INFO = {
    "orange_tabby": {
        "name": "橘猫",
        "emoji": "🐱",
        "personality": "活泼好动，表情丰富，好奇心强，偶尔犯蠢",
        "appearance": (
            "A round-faced orange tabby cat with amber eyes, soft striped orange fur, "
            "chubby cheeks, fluffy tail, cute and expressive face"
        ),
    },
    "calico_cat": {
        "name": "三花猫",
        "emoji": "😺",
        "personality": "优雅灵动，聪明机敏，带点小傲娇",
        "appearance": (
            "A elegant calico cat with white, orange and black patches, emerald green eyes, "
            "sleek soft fur, delicate features, graceful posture"
        ),
    },
    "black_cat": {
        "name": "黑猫",
        "emoji": "🐈‍⬛",
        "personality": "神秘呆萌，偶尔神经质，实则温柔粘人",
        "appearance": (
            "A sleek black short-haired cat with big golden round eyes, slender body, "
            "pointed ears, shiny black fur, mysterious yet adorable expression"
        ),
    },
    "ragdoll_cat": {
        "name": "布偶猫",
        "emoji": "😻",
        "personality": "温顺可爱，优雅慵懒，像毛绒玩具一样软萌",
        "appearance": (
            "A fluffy Ragdoll cat with striking blue eyes, long soft cream-colored fur "
            "with seal-point markings, round face, gentle sweet expression, cloud-like fluffiness"
        ),
    },
    "british_shorthair": {
        "name": "英短",
        "emoji": "🐱",
        "personality": "憨态可掬，圆脸胖腮，表情一本正经但自带喜感",
        "appearance": (
            "A chubby blue-gray British Shorthair cat with round copper eyes, dense plush coat, "
            "famously round face with full cheeks, sturdy body, adorably serious expression"
        ),
    },
    "orange_cat_fat": {
        "name": "胖橘",
        "emoji": "🍊",
        "personality": "贪吃贪睡，慵懒佛系，走路摇晃，偶尔为食物爆发惊人活力",
        "appearance": (
            "An adorably overweight orange tabby cat, round body with rolls of fluff, "
            "sleepy amber eyes, chubby face, waddling walk, permanently hungry expression"
        ),
    },
    "panda": {
        "name": "熊猫",
        "emoji": "🐼",
        "personality": "呆萌可爱，动作缓慢笨拙，憨态可掬，国宝级萌物",
        "appearance": (
            "A round chubby giant panda with distinctive black and white fur, black eye patches "
            "giving a cute innocent look, round body, clumsy gentle movements, fluffy ears"
        ),
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# 场景模板系统
# ═══════════════════════════════════════════════════════════════════════════════

SCENE_TEMPLATES = {
    "daily_life": {
        "label": "日常模拟",
        "description": "猫咪模拟普通人的日常生活场景",
        "visual_style": (
            "warm cozy indoor setting with natural lighting, lived-in apartment or office feel, "
            "everyday objects scaled to cat size, soft morning or afternoon light through windows, "
            "comfortable domestic atmosphere"
        ),
        "camera_style": "medium shots and close-ups, smooth gentle camera movement, documentary-style framing",
    },
    "skit_comedy": {
        "label": "搞笑段子",
        "description": "猫咪演绎吐槽、段子、搞笑内容",
        "visual_style": (
            "bright colorful setting, slightly exaggerated props and details, "
            "clean modern background, vibrant lighting, playful atmosphere"
        ),
        "camera_style": "dynamic close-ups on facial expressions, quick cuts, energetic camera movement, reaction shots",
    },
    "social_commentary": {
        "label": "社会评论",
        "description": "猫咪评论社会热点和新闻",
        "visual_style": (
            "semi-formal setting with warm touches, clean desk or simple studio backdrop, "
            "soft professional lighting, subtle warm tones, approachable atmosphere"
        ),
        "camera_style": "steady medium shot like a news anchor, occasional zoom for emphasis, clean composition",
    },
    "pet_moments": {
        "label": "萌宠时刻",
        "description": "猫咪的可爱日常、治愈瞬间",
        "visual_style": (
            "bright warm natural light, soft pastel tones, cozy blankets and cushions, "
            "sunlight streaming through windows, dreamy bokeh background, gentle atmosphere"
        ),
        "camera_style": "slow gentle pans, intimate close-ups, soft focus transitions, heartwarming slow-motion feel",
    },
}

SCENE_FALLBACK = {
    "label": "通用",
    "description": "猫咪趣味演绎",
    "visual_style": (
        "warm inviting indoor setting, soft natural lighting, cozy and clean background, "
        "pleasant atmosphere with cute decorative elements"
    ),
    "camera_style": "balanced mix of medium shots and close-ups, smooth camera movement, natural framing",
}

# ═══════════════════════════════════════════════════════════════════════════════
# 统一风格约束
# ═══════════════════════════════════════════════════════════════════════════════

STYLE_CONSTRAINT = (
    "## Critical Style Requirements\n"
    "1. The main subject MUST be a REALISTIC cat (or the specified animal) — NOT a cartoon, "
    "anime character, illustration, or 3D rendered model. The cat should look like a real "
    "photographed animal with fur texture, natural anatomy, and lifelike features.\n"
    "2. The cat's facial expressions should be lively and expressive — capable of showing "
    "emotions (surprise, anger, joy, sadness, smugness) through subtle eye changes, ear positions, "
    "whisker movements, and mouth shapes, while still looking like a REAL cat, not a caricature.\n"
    "3. Movement should be natural cat behavior — walking, sitting, tail swishing, ear twitching, "
    "head tilting, paw gesturing — with slight animated exaggeration only in timing and emphasis, "
    "not in squash-and-stretch cartoon physics.\n"
    "4. Overall aesthetic: high-quality live-action photography quality with subtle motion, "
    "like a well-shot pet video with the cat naturally performing the scene. Think "
    "\"cats in a live-action movie\" not \"animated cat cartoon.\"\n"
    "5. The cat should be the only speaking/acting character. Voiceover should feel like "
    "the cat is thinking or speaking naturally.\n"
    "6. Lighting and color grading should be warm and inviting — soft natural light, "
    "gentle shadows, cozy atmosphere. Avoid harsh studio lighting or cold clinical looks."
)

# ═══════════════════════════════════════════════════════════════════════════════
# LLM 模型注册
# ═══════════════════════════════════════════════════════════════════════════════

ALL_SOURCE_TYPES = ["text", "web_link", "image", "douyin_video"]
TEXT_ONLY_SOURCE_TYPES = ["text", "web_link"]


@dataclass
class LLMModelInfo:
    id: str
    name: str
    provider: str
    supported_input_types: list[str]
    mode: str = "remote"
    requires_config: list[str] = field(default_factory=list)
    available: bool = True


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
    for key in requires_config:
        if not getattr(settings, key, None):
            return False
    return True


def list_llm_models() -> list[dict]:
    result = []
    for m in LLM_MODELS:
        available = m.available
        if m.mode == "local":
            available = _check_local_config(m.requires_config)
        result.append({
            "id": m.id, "name": m.name, "provider": m.provider,
            "supported_input_types": m.supported_input_types,
            "mode": m.mode, "requires_config": m.requires_config,
            "available": available,
        })
    return result


def get_llm_model(model_id: str | None = None) -> LLMModelInfo:
    target = model_id or settings.llm_model
    for m in LLM_MODELS:
        if m.id == target:
            return m
    return LLM_MODELS[0]


def supports_input_type(model_id: str, source_type: str) -> bool:
    model = get_llm_model(model_id)
    return source_type in model.supported_input_types


# ═══════════════════════════════════════════════════════════════════════════════
# 核心数据类
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VideoPrompt:
    prompt: str
    title: str
    scene_type: str = "general"
    character: str = "orange_tabby"
    duration_estimate: int = 15
    model_used: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# PromptBuilder — 核心提示词引擎
# ═══════════════════════════════════════════════════════════════════════════════

class PromptBuilder:
    """内容分析 + 视频提示词生成"""

    def __init__(self, model_id: str | None = None):
        self.model_id = model_id or settings.llm_model
        self.model_info = get_llm_model(self.model_id)

    async def build(
        self,
        content: str,
        character: str = "orange_tabby",
        scene_mode: str = "auto",
    ) -> VideoPrompt:
        char_info = CHARACTER_INFO.get(character, CHARACTER_INFO["orange_tabby"])

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(content, char_info, scene_mode)

        raw = await self._call_llm(system_prompt, user_prompt)
        return self._parse(raw, character)

    # ── Prompt 构造 ──────────────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        return f"""You are an expert video prompt engineer specializing in AI video generation APIs (Kling, Runway, Jimeng, Hailuo).

Your task: analyze user-provided content and generate a complete English video prompt.

{STYLE_CONSTRAINT}

## Scene Type Classification
Analyze the content and classify it into ONE of:
- "daily_life": cats simulating daily human life (work, vacation, cooking, commuting)
- "skit_comedy": cats performing comedy skits (complaints, jokes, satire, rants)
- "social_commentary": cats commenting on social topics, news, trends
- "pet_moments": cute cat moments, heartwarming pet scenarios

## Output Format
Return ONLY valid JSON (no markdown, no explanation):
{{"scene_type": "<type>", "prompt": "<full English video prompt 200-400 words>", "title": "<Chinese title under 20 chars>", "duration_estimate": <seconds 10-30>}}

## Prompt Quality Standards
The "prompt" field must include ALL of:
1. Main subject description (cat breed, appearance, expression) — be specific
2. Scene and environment description — detailed setting
3. Action and performance — what the cat is doing, how it moves
4. Camera direction — shot types, movement, framing
5. Lighting and atmosphere — mood, time of day, color tone
6. Overall style and quality keywords"""

    def _build_user_prompt(self, content: str, char_info: dict, scene_mode: str) -> str:
        scene_hint = ""
        if scene_mode == "news":
            scene_hint = "\nNote: this is news/social commentary content. The cat should be in a semi-formal anchor/reporter role."
        elif scene_mode == "dialogue":
            scene_hint = "\nNote: this is dialogue/skit content. The cat should perform with expressive reactions and comedic timing."

        return f"""Generate a video prompt based on the following content:

## Content
{content[:3000]}

## Character
- Name: {char_info['name']} {char_info['emoji']}
- Personality: {char_info['personality']}
- Appearance: {char_info['appearance']}
{scene_hint}

## Available Scene Types
- daily_life: {SCENE_TEMPLATES['daily_life']['visual_style']}
- skit_comedy: {SCENE_TEMPLATES['skit_comedy']['visual_style']}
- social_commentary: {SCENE_TEMPLATES['social_commentary']['visual_style']}
- pet_moments: {SCENE_TEMPLATES['pet_moments']['visual_style']}

Choose the most appropriate scene type and generate the prompt JSON."""

    # ── LLM 调用 ─────────────────────────────────────────────────────────

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        provider = self.model_info.provider

        if provider == "openai":
            return await self._call_openai(system_prompt, user_prompt)
        else:
            # anthropic / deepseek — both use Anthropic-compatible API
            return await self._call_anthropic(system_prompt, user_prompt)

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
            system="You are a JSON-only output machine. Output only valid JSON in the exact format requested. No markdown, no explanation.",
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
                {"role": "system", "content": "You are a JSON-only output machine. Output only valid JSON in the exact format requested. No markdown, no explanation."},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content.strip() if resp.choices else ""

    # ── 解析 ─────────────────────────────────────────────────────────────

    def _parse(self, raw: str, character: str) -> VideoPrompt:
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
            scene_type=data.get("scene_type", "general"),
            character=character,
            duration_estimate=data.get("duration_estimate", 15),
            model_used=self.model_id,
        )
