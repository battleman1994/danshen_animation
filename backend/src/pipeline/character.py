"""
角色生成模块

为动漫视频生成角色图片：
- 设计角色外观
- 调用 ComfyUI / Stable Diffusion 生成
- 生成不同表情的变体
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

import httpx
from openai import AsyncOpenAI

from ..config import settings


class CharacterGenerator:
    """动漫角色图片生成器"""

    # 角色外观描述预设
    APPEARANCE_PROMPTS = {
        "tabby_cat": (
            "A cute tabby cat with green eyes, orange and black striped fur, "
            "chibi anime style, soft shading, simple background, standing on two legs, "
            "wearing casual clothes, Pixar-style rendering, high quality"
        ),
        "brown_bear": (
            "A dignified brown bear with round glasses, wearing a suit and tie, "
            "chibi anime style, warm brown fur, serious but adorable expression, "
            "sitting at a news desk, high quality rendering"
        ),
        "little_fox": (
            "A sly orange fox with a mischievous grin, big ears, fluffy tail, "
            "chibi anime style, wearing a hoodie, playful pose, "
            "bright colors, high quality"
        ),
        "panda": (
            "A chubby panda with sleepy eyes, black and white fur, "
            "chibi anime style, holding a bamboo stick, lounging on a cushion, "
            "soft pastel colors, kawaii style"
        ),
        "owl": (
            "A wise owl professor with half-moon spectacles, brown feathers, "
            "chibi anime style, wearing an academic robe, holding a pointer, "
            "sitting at a podium, warm lighting"
        ),
        "shiba_inu": (
            "A cheerful shiba inu dog with a happy smile, cream and tan fur, "
            "chibi anime style, wearing a cute bow tie, energetic pose, "
            "bright sunny background, high quality kawaii rendering"
        ),
        "rabbit": (
            "A gentle white rabbit with long floppy ears, pink nose, "
            "chibi anime style, wearing a soft pastel dress, delicate pose, "
            "flower garden background, dreamy soft lighting"
        ),
        "penguin": (
            "A cute emperor penguin chick with fluffy gray feathers, round body, "
            "chibi anime style, wearing tiny glasses, standing at an ice podium, "
            "holding a pointer stick, icy blue background"
        ),
        "lion": (
            "A majestic lion with a golden mane, regal expression, "
            "chibi anime style, wearing a formal anchor suit with a tiny tie, "
            "sitting at a grand news desk, dramatic lighting, "
            "high quality rendering, professional broadcast style"
        ),
    }

    # 情绪对应的表情 prompt
    EMOTION_PROMPTS = {
        "happy": "happy expression, big smile, sparkling eyes, joyful pose",
        "sad": "sad expression, teary eyes, drooping ears, melancholic pose",
        "funny": "laughing expression, tears of joy, pointing gesture",
        "serious": "serious expression, furrowed brows, stern look, professional posture",
        "surprised": "surprised expression, wide eyes, open mouth, startled pose",
        "angry": "angry expression, puffed cheeks, glaring eyes, stomping",
        "neutral": "neutral expression, calm eyes, relaxed posture",
    }

    def __init__(self):
        self.llm = AsyncOpenAI(
            api_key=settings.llm_api_key or "not-needed",
            base_url=settings.llm_base_url,
        )

    async def generate_character_set(
        self,
        character: str,
        expressions: list[str] = None,
        output_dir: Optional[Path] = None,
    ) -> dict[str, Path]:
        """
        生成角色图片集（不同表情）

        Returns:
            {emotion: image_path}
        """
        if expressions is None:
            expressions = ["neutral", "happy", "surprised", "serious", "funny"]

        base_prompt = self.APPEARANCE_PROMPTS.get(character, self.APPEARANCE_PROMPTS["tabby_cat"])
        out_dir = output_dir or settings.output_dir / "characters" / character
        out_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        for emotion in expressions:
            emotion_prompt = self.EMOTION_PROMPTS.get(emotion, "")
            full_prompt = f"{base_prompt}, {emotion_prompt}, white background"

            image_path = await self._generate_image(full_prompt, out_dir / f"{emotion}.png")
            results[emotion] = image_path

        return results

    async def generate_background(
        self, mood: str = "bright", output_path: Optional[Path] = None
    ) -> Path:
        """生成背景图"""
        mood_prompts = {
            "bright": "bright cheerful anime background, pastel colors, sunny day, simple clean style",
            "calm": "calm peaceful anime background, soft blue tones, gentle lighting, minimal style",
            "dark": "dark moody anime background, dramatic lighting, mysterious atmosphere",
            "news": "professional news studio background, clean modern design, warm lighting",
        }
        prompt = mood_prompts.get(mood, mood_prompts["bright"])

        out_path = output_path or settings.output_dir / "backgrounds" / f"{mood}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        return await self._generate_image(prompt, out_path)

    async def _generate_image(self, prompt: str, output_path: Path) -> Path:
        """调用图片生成服务"""
        if output_path.exists():
            return output_path

        if settings.image_gen_provider == "comfyui":
            return await self._comfyui_generate(prompt, output_path)
        else:
            return await self._dalle_generate(prompt, output_path)

    async def _comfyui_generate(self, prompt: str, output_path: Path) -> Path:
        """通过 ComfyUI 生成图片"""
        # ComfyUI workflow — 使用默认 SDXL 工作流
        workflow = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 42,
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": f"chibi anime style, {prompt}, masterpiece, best quality",
                    "clip": ["4", 1]
                }
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "low quality, blurry, distorted, realistic, photorealistic, ugly",
                    "clip": ["4", 1]
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": output_path.stem,
                    "images": ["8", 0]
                }
            }
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.comfyui_url}/prompt",
                json={"prompt": workflow},
                timeout=120,
            )
            data = resp.json()
            prompt_id = data.get("prompt_id")

            # 轮询等待完成
            for _ in range(60):
                await asyncio.sleep(2)
                hist_resp = await client.get(f"{settings.comfyui_url}/history/{prompt_id}")
                hist = hist_resp.json()
                if prompt_id in hist:
                    # 下载生成的图片
                    for node_id, node_output in hist[prompt_id].get("outputs", {}).items():
                        for img in node_output.get("images", []):
                            img_url = f"{settings.comfyui_url}/view?filename={img['filename']}"
                            img_resp = await client.get(img_url)
                            output_path.write_bytes(img_resp.content)
                            return output_path

            # Fallback: 创建占位图
            return self._create_placeholder(output_path, prompt)

    async def _dalle_generate(self, prompt: str, output_path: Path) -> Path:
        """通过 OpenAI DALL-E 生成图片"""
        try:
            resp = await self.llm.images.generate(
                model="dall-e-3",
                prompt=f"Chibi anime style, {prompt}",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = resp.data[0].url
            async with httpx.AsyncClient() as client:
                img_resp = await client.get(image_url)
                output_path.write_bytes(img_resp.content)
            return output_path
        except Exception:
            return self._create_placeholder(output_path, prompt)

    def _create_placeholder(self, path: Path, prompt: str) -> Path:
        """创建占位图（开发阶段使用）"""
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (512, 512), color=(255, 240, 245))
        draw = ImageDraw.Draw(img)
        # 画一个简单的角色轮廓
        draw.ellipse([156, 50, 356, 250], fill=(255, 200, 150), outline=(200, 150, 100))
        draw.ellipse([180, 80, 210, 110], fill=(255, 255, 255))
        draw.ellipse([300, 80, 330, 110], fill=(255, 255, 255))
        draw.ellipse([185, 85, 205, 105], fill=(0, 0, 0))
        draw.ellipse([305, 85, 325, 105], fill=(0, 0, 0))
        draw.arc([220, 120, 290, 180], 0, 180, fill=(0, 0, 0), width=2)
        draw.text((156, 260), "🔧 开发中...", fill=(100, 100, 100))
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
        return path
