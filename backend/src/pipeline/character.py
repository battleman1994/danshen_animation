import asyncio
import logging
from pathlib import Path

import httpx

from ..config import settings
from .storyboard import StoryboardScene

logger = logging.getLogger(__name__)

APPEARANCE_PROMPTS_SD15 = {
    "tabby_cat": (
        "chibi tabby cat, green eyes, orange striped fur, anthropomorphic, "
        "anime style, cute, masterpiece, best quality"
    ),
    "brown_bear": (
        "chibi brown bear, round glasses, suit, anthropomorphic, "
        "anime mascot style, cute, warm colors, masterpiece, best quality"
    ),
    "little_fox": (
        "chibi orange fox, mischievous grin, big ears, fluffy tail, anthropomorphic, "
        "anime style, playful, bright colors, masterpiece, best quality"
    ),
    "panda": (
        "chibi panda, sleepy eyes, black white fur, holding bamboo, anthropomorphic, "
        "kawaii style, pastel colors, masterpiece, best quality"
    ),
    "owl": (
        "chibi owl professor, half-moon spectacles, brown feathers, anthropomorphic, "
        "academic robe, wise expression, warm lighting, masterpiece, best quality"
    ),
    "shiba_inu": (
        "chibi shiba inu dog, happy smile, cream tan fur, bow tie, anthropomorphic, "
        "kawaii rendering, sunny, energetic, masterpiece, best quality"
    ),
    "rabbit": (
        "chibi white rabbit, long floppy ears, pink nose, pastel dress, anthropomorphic, "
        "dreamy soft lighting, flower garden, masterpiece, best quality"
    ),
    "penguin": (
        "chibi emperor penguin chick, fluffy gray, tiny glasses, ice podium, anthropomorphic, "
        "icy blue background, cute, masterpiece, best quality"
    ),
    "lion": (
        "chibi lion, golden mane, regal expression, formal suit, anthropomorphic, "
        "dramatic lighting, professional, masterpiece, best quality"
    ),
}

EMOTION_PROMPTS_SD15 = {
    "happy": "happy expression, big smile, sparkling eyes, joyful pose",
    "sad": "sad expression, teary eyes, drooping ears, melancholic",
    "funny": "laughing expression, tears of joy, pointing gesture, comedic",
    "serious": "serious expression, furrowed brows, stern look, professional",
    "surprised": "surprised expression, wide eyes, open mouth, startled",
    "angry": "angry expression, puffed cheeks, glaring, stomping",
    "neutral": "neutral expression, calm eyes, relaxed posture",
}

BACKGROUND_PROMPTS_SD15 = {
    "sunny_park": "sunny park, green grass, blue sky, trees, anime background, simple",
    "cozy_room": "cozy room, warm lighting, cute furniture, anime background, simple",
    "city_street": "city street, buildings, clean, anime background, simple",
    "simple_studio": "simple studio, gradient background, clean, anime background, minimal",
    "flower_garden": "flower garden, blossoms, pastel, anime background, dreamy",
    "news_studio": "news studio, professional, desk, warm lighting, clean background",
    "beach": "tropical beach, ocean, sunny, anime background, cheerful",
    "night_sky": "night sky, stars, moon, magical, anime background, dreamy",
}


CHARACTER_COLORS = {
    "tabby_cat": ("#FF8C42", "#FFD4A8"),
    "brown_bear": ("#8B6914", "#DEB887"),
    "little_fox": ("#FF6B35", "#FFE0B0"),
    "panda": ("#4A4A4A", "#F5F5F5"),
    "rabbit": ("#FFB6C1", "#FFF0F5"),
    "shiba_inu": ("#F4A460", "#FFECD2"),
    "owl": ("#8B7355", "#F5E6D3"),
    "penguin": ("#3A3A5C", "#E8E8F0"),
    "lion": ("#DAA520", "#FFF4D0"),
}

BG_COLORS = {
    "sunny_park": ("#87CEEB", "#90EE90"),
    "cozy_room": ("#FFE4B5", "#FFF8DC"),
    "city_street": ("#B0C4DE", "#D3D3D3"),
    "simple_studio": ("#E8E0D8", "#F5F0EB"),
    "flower_garden": ("#FFB7C5", "#E8F5E9"),
    "news_studio": ("#1A1A2E", "#2D2D44"),
    "beach": ("#00CED1", "#FFE4B5"),
    "night_sky": ("#191970", "#483D8B"),
}


class CharacterGenerator:
    def __init__(self):
        self._comfyui_url = settings.comfyui_url.rstrip("/")
        self._gpu_checked = False
        self._gpu_available = False

    async def _check_gpu(self) -> bool:
        """Probe ComfyUI availability. Cached after first call."""
        if self._gpu_checked:
            return self._gpu_available
        self._gpu_checked = True
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._comfyui_url}/system_stats", timeout=5,
                )
                if resp.status_code == 200:
                    self._gpu_available = True
                    logger.info("ComfyUI GPU detected at %s", self._comfyui_url)
                    return True
        except Exception:
            pass
        logger.info("ComfyUI not available, using CPU fallback render")
        return False

    async def generate_scene_frame(
        self, scene: StoryboardScene, seed: int, output_dir: Path
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"scene_{scene.index:02d}.png"

        if out_path.exists():
            return out_path

        if await self._check_gpu():
            return await self._generate_scene_comfyui(scene, seed, out_path)
        else:
            return self._render_fallback_frame(scene, seed, out_path)

    async def _generate_scene_comfyui(
        self, scene: StoryboardScene, seed: int, out_path: Path
    ) -> Path:
        base_prompt = APPEARANCE_PROMPTS_SD15.get(scene.character, APPEARANCE_PROMPTS_SD15["tabby_cat"])
        emotion_prompt = EMOTION_PROMPTS_SD15.get(scene.emotion, EMOTION_PROMPTS_SD15["neutral"])
        positive = f"{base_prompt}, {emotion_prompt}, doing {scene.action}, {scene.camera}"
        negative = "low quality, blurry, distorted, realistic, photorealistic, ugly, bad anatomy, deformed"

        lora_name = settings.lora_model_paths.get(scene.character, "")
        lora_weight = settings.lora_weights.get(scene.character, 0.8)

        workflow = self._build_workflow(
            seed=seed,
            positive_prompt=positive,
            negative_prompt=negative,
            lora_name=lora_name,
            lora_weight=lora_weight,
            filename_prefix=f"scene_{scene.index:02d}",
        )

        try:
            return await self._comfyui_generate(workflow, out_path)
        except ComfyUIError as e:
            logger.warning("ComfyUI generation failed, falling back: %s", e)
            return self._render_fallback_frame(scene, seed, out_path)

    async def generate_background(self, background_key: str, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"bg_{background_key}.png"

        if out_path.exists():
            return out_path

        if await self._check_gpu():
            return await self._generate_bg_comfyui(background_key, out_path)
        else:
            return self._render_fallback_bg(background_key, out_path)

    async def _generate_bg_comfyui(self, background_key: str, out_path: Path) -> Path:
        bg_prompt = BACKGROUND_PROMPTS_SD15.get(
            background_key, BACKGROUND_PROMPTS_SD15["simple_studio"]
        )
        positive = f"{bg_prompt}, masterpiece, best quality"
        negative = "low quality, blurry, distorted, characters, people, animals, text, watermark"

        workflow = self._build_workflow(
            seed=settings.default_seed,
            positive_prompt=positive,
            negative_prompt=negative,
            lora_name="",
            lora_weight=0,
            filename_prefix=f"bg_{background_key}",
        )

        try:
            return await self._comfyui_generate(workflow, out_path)
        except ComfyUIError as e:
            logger.warning("ComfyUI background failed, falling back: %s", e)
            return self._render_fallback_bg(background_key, out_path)

    def _render_fallback_frame(self, scene: StoryboardScene, seed: int, out_path: Path) -> Path:
        from PIL import Image, ImageDraw, ImageFont
        import random as _random
        _rng = _random.Random(seed)

        primary, secondary = CHARACTER_COLORS.get(
            scene.character, CHARACTER_COLORS["tabby_cat"]
        )
        char_name = {"tabby_cat": "狸花猫", "panda": "熊猫", "little_fox": "小狐狸",
                     "brown_bear": "棕熊", "shiba_inu": "柴犬", "rabbit": "兔子",
                     "owl": "猫头鹰", "penguin": "企鹅", "lion": "雄狮"}.get(
            scene.character, scene.character)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 22)
            font_sm = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 16)
            font_lg = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
        except Exception:
            font = ImageFont.load_default()
            font_sm = font
            font_lg = font

        img = Image.new("RGB", (1280, 720), color=secondary)
        draw = ImageDraw.Draw(img)

        # ── emotion expression parameters ──
        eye_h = {"happy": 0.5, "funny": 0.2, "sad": 0.7, "surprised": 1.0,
                 "angry": 0.3, "serious": 0.5, "neutral": 0.6}.get(scene.emotion, 0.6)
        mouth_curve = {"happy": "up", "funny": "wide_up", "sad": "down",
                       "surprised": "o", "angry": "tight", "serious": "flat",
                       "neutral": "flat"}.get(scene.emotion, "flat")

        # ── draw animal face ──
        self._draw_animal_face(draw, scene.character, primary, secondary, eye_h,
                               mouth_curve, _rng, img.size)

        # ── dialogue bubble ──
        img_w, img_h = img.size
        dialogue = scene.dialogue[:60] if len(scene.dialogue) <= 60 else scene.dialogue[:57] + "..."
        bubble_w = min(len(dialogue) * 18, 1200)
        bubble_h = 50
        bubble_x = (img_w - bubble_w) // 2
        bubble_y = 600
        draw.rounded_rectangle(
            [bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h],
            radius=16, fill="white", outline=primary, width=2,
        )
        tw = draw.textlength(dialogue, font=font)
        draw.text(
            (bubble_x + (bubble_w - tw) // 2, bubble_y + 10),
            dialogue, fill=primary, font=font,
        )

        # ── bottom info ──
        draw.text((12, img_h - 28), f"{char_name} | {scene.emotion} | {scene.action}",
                  fill="#888", font=font_sm)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "PNG")
        return out_path

    def _draw_animal_face(self, draw, character, primary, secondary, eye_h, mouth, rng, size):
        """Draw an animal face centered in the frame."""
        w, h = size
        cx, cy = w // 2, 300

        # Main head shape
        head_rx, head_ry = 105, 95
        draw.ellipse(
            [cx - head_rx, cy - head_ry, cx + head_rx, cy + head_ry],
            fill=primary,
        )

        if character == "panda":
            # Panda: white face with black eye patches
            draw.ellipse(
                [cx - head_rx, cy - head_ry, cx + head_rx, cy + head_ry],
                fill="#F5F5F5", outline="#333", width=2,
            )
            for ex in [-35, 35]:
                draw.ellipse([cx + ex - 22, cy - 25, cx + ex + 22, cy + 10],
                             fill="#333")
            draw.ellipse([cx - 8, cy + 15, cx + 8, cy + 25], fill="#333")
            # Ears
            for ex in [-60, 60]:
                draw.ellipse([cx + ex - 28, cy - 95, cx + ex + 28, cy - 30],
                             fill="#333")
        elif character == "rabbit":
            # Rabbit: white face, long ears, pink nose
            for ex in [-20, 20]:
                draw.ellipse([cx + ex - 12, cy - 140, cx + ex + 12, cy - 50],
                             fill="white", outline="#FFB6C1", width=2)
            draw.ellipse([cx - 5, cy + 10, cx + 5, cy + 20], fill="#FFB6C1")
        elif character == "little_fox":
            # Fox: triangular face, big pointed ears
            for ex in [-55, 55]:
                draw.polygon([
                    (cx + ex, cy - 100), (cx + ex - 25, cy - 20),
                    (cx + ex + 25, cy - 20),
                ], fill=primary)
            draw.polygon([
                (cx - 5, cy + 25), (cx + 5, cy + 25), (cx, cy + 10),
            ], fill="#333")
        elif character == "brown_bear":
            # Bear: round face, small round ears, brown
            for ex in [-60, 60]:
                draw.ellipse([cx + ex - 22, cy - 100, cx + ex + 22, cy - 40],
                             fill="#5C3317")
            draw.ellipse([cx - 8, cy + 15, cx + 8, cy + 25], fill="#5C3317")
        elif character == "shiba_inu":
            # Dog: cream face, triangle ears
            for ex in [-55, 55]:
                draw.polygon([
                    (cx + ex, cy - 100), (cx + ex - 22, cy - 25),
                    (cx + ex + 22, cy - 25),
                ], fill=primary)
            draw.ellipse([cx - 10, cy + 18, cx + 10, cy + 30], fill="#FFE4C4")
        elif character == "owl":
            # Owl: big round face, huge eyes, small beak
            draw.ellipse(
                [cx - 90, cy - 60, cx + 90, cy + 60],
                fill="#E8D5B7", outline="#8B7355", width=3,
            )
            draw.polygon([(cx - 6, cy), (cx + 6, cy), (cx, cy + 10)], fill="#FF8C00")
        elif character == "penguin":
            # Penguin: round dark body, white belly patch, small beak
            draw.ellipse(
                [cx - 75, cy - 55, cx + 75, cy + 75],
                fill="#3A3A5C",
            )
            draw.ellipse([cx - 45, cy - 10, cx + 45, cy + 60], fill="white")
            draw.polygon([(cx - 5, cy - 10), (cx + 5, cy - 10), (cx, cy + 2)],
                         fill="#FF8C00")
        elif character == "lion":
            # Lion: mane around face
            for ang in range(0, 360, 20):
                import math
                rad = math.radians(ang)
                mx = cx + int(125 * math.cos(rad))
                my = cy + int(110 * math.sin(rad))
                draw.ellipse([mx - 15, my - 15, mx + 15, my + 15], fill="#DAA520")
        else:
            # Tabby cat (default): pointed ears, whiskers
            for ex in [-50, 50]:
                draw.polygon([
                    (cx + ex, cy - 100), (cx + ex - 20, cy - 15),
                    (cx + ex + 20, cy - 15),
                ], fill=primary)
            # Whiskers
            for sx, sy, ex, ey in [
                (cx - 55, cy + 5, cx - 110, cy - 5),
                (cx - 55, cy + 15, cx - 110, cy + 20),
                (cx + 55, cy + 5, cx + 110, cy - 5),
                (cx + 55, cy + 15, cx + 110, cy + 20),
            ]:
                draw.line([(sx, sy), (ex, ey)], fill="#666", width=1)
            # Nose
            draw.polygon([(cx - 6, cy + 10), (cx + 6, cy + 10), (cx, cy + 18)],
                         fill="#FF9999")

        # ── Eyes (common to all characters except penguin, owl) ──
        if character not in ("penguin",):
            eye_open = eye_h
            eye_w = 22 if character != "owl" else 35
            eye_h_px = int(eye_w * eye_open) if eye_open > 0.3 else 4
            eye_y = cy - 15

            for ex in [-32, 32]:
                if character == "owl":
                    ex = ex * 1.2
                draw.ellipse(
                    [cx + ex - eye_w, eye_y - eye_h_px,
                     cx + ex + eye_w, eye_y + eye_h_px],
                    fill="white", outline="#333", width=2,
                )
                if eye_open > 0.3:
                    pupil_w = 9
                    draw.ellipse(
                        [cx + ex - pupil_w, eye_y - pupil_w,
                         cx + ex + pupil_w, eye_y + pupil_w],
                        fill="#222",
                    )
                    # highlight
                    draw.ellipse(
                        [cx + ex + 2, eye_y - eye_h_px + 3,
                         cx + ex + 8, eye_y - eye_h_px + 9],
                        fill="white",
                    )

        # ── Mouth ──
        mouth_y = cy + 30
        if mouth == "up":
            draw.arc([cx - 20, mouth_y - 10, cx + 20, mouth_y + 10],
                     start=0, end=180, fill="#333", width=2)
        elif mouth == "wide_up":
            draw.arc([cx - 30, mouth_y - 15, cx + 30, mouth_y + 5],
                     start=0, end=180, fill="#333", width=2)
        elif mouth == "down":
            draw.arc([cx - 20, mouth_y, cx + 20, mouth_y + 20],
                     start=180, end=360, fill="#333", width=2)
        elif mouth == "o":
            draw.ellipse([cx - 12, mouth_y - 12, cx + 12, mouth_y + 12],
                         fill="#333")
        elif mouth == "tight":
            draw.line([(cx - 15, mouth_y), (cx + 15, mouth_y)], fill="#333", width=2)
        else:
            draw.line([(cx - 18, mouth_y), (cx + 18, mouth_y)], fill="#333", width=2)

        # ── Blush ──
        if mouth in ("up", "wide_up", "neutral"):
            for ex in [-55, 55]:
                draw.ellipse(
                    [cx + ex - 14, mouth_y - 22, cx + ex + 14, mouth_y - 6],
                    fill="#FFB6C1", outline=None,
                )

    def _render_fallback_bg(self, bg_key: str, out_path: Path) -> Path:
        from PIL import Image

        color1, color2 = BG_COLORS.get(bg_key, BG_COLORS["simple_studio"])
        img = Image.new("RGB", (1280, 720), color=color2)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        for y in range(720):
            ratio = y / 720
            r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
            g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
            b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)
            draw.line([(0, y), (1920, y)], fill=(r, g, b))

        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "PNG")
        return out_path

    def _build_workflow(
        self,
        seed: int,
        positive_prompt: str,
        negative_prompt: str,
        lora_name: str,
        lora_weight: float,
        filename_prefix: str,
    ) -> dict:
        w = settings.sd_image_width
        h = settings.sd_image_height
        ckpt = settings.sd_model

        workflow = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed, "steps": 25, "cfg": 7.0,
                    "sampler_name": "euler_ancestral", "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["12", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": ckpt},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": w, "height": h, "batch_size": 1},
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": positive_prompt, "clip": ["12", 1]},
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": negative_prompt, "clip": ["12", 1]},
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": filename_prefix, "images": ["8", 0]},
            },
        }

        if lora_name:
            workflow["12"] = {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "model": ["4", 0],
                    "lora_name": lora_name,
                    "strength_model": lora_weight,
                },
            }
        else:
            workflow["12"] = {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "model": ["4", 0],
                    "lora_name": lora_name,
                    "strength_model": 0,
                },
            }

        return workflow

    async def _comfyui_generate(self, workflow: dict, output_path: Path) -> Path:
        prompt_url = f"{self._comfyui_url}/prompt"

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    prompt_url, json={"prompt": workflow}, timeout=30,
                )
                resp.raise_for_status()
            except httpx.HTTPError as e:
                raise ComfyUIError(f"ComfyUI POST /prompt failed: {e}")

            data = resp.json()
            prompt_id = data.get("prompt_id")
            if not prompt_id:
                raise ComfyUIError(f"No prompt_id in response: {data}")

            history_url = f"{self._comfyui_url}/history/{prompt_id}"
            for attempt in range(60):
                await asyncio.sleep(2)
                try:
                    hist_resp = await client.get(history_url, timeout=10)
                    hist_resp.raise_for_status()
                    hist = hist_resp.json()
                except httpx.HTTPError:
                    continue

                if prompt_id not in hist:
                    continue

                outputs = hist[prompt_id].get("outputs", {})
                for _node_id, node_output in outputs.items():
                    for img in node_output.get("images", []):
                        filename = img["filename"]
                        img_url = f"{self._comfyui_url}/view?filename={filename}"
                        img_resp = await client.get(img_url, timeout=30)
                        output_path.write_bytes(img_resp.content)
                        return output_path

            raise ComfyUIError(f"ComfyUI generation timed out after 60 polls for prompt {prompt_id}")


class ComfyUIError(Exception):
    pass
