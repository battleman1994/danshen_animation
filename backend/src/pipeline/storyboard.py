from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

VALID_EMOTIONS = {"happy", "sad", "funny", "serious", "surprised", "angry", "neutral"}
VALID_CAMERAS = {"medium_shot", "close_up", "wide_shot"}
VALID_STYLES = {"funny", "serious", "cute", "news"}


@dataclass
class StoryboardScene:
    index: int
    duration_s: int
    dialogue: str
    character: str
    emotion: str = "neutral"
    action: str = ""
    background: str = "simple_studio"
    camera: str = "medium_shot"

    def __post_init__(self):
        if self.duration_s < 2 or self.duration_s > 8:
            raise ValueError(
                f"Scene {self.index}: duration_s must be 2-8, got {self.duration_s}"
            )
        if self.emotion not in VALID_EMOTIONS:
            raise ValueError(
                f"Scene {self.index}: invalid emotion '{self.emotion}', must be one of {VALID_EMOTIONS}"
            )
        if self.camera not in VALID_CAMERAS:
            raise ValueError(
                f"Scene {self.index}: invalid camera '{self.camera}', must be one of {VALID_CAMERAS}"
            )

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "duration_s": self.duration_s,
            "dialogue": self.dialogue,
            "character": self.character,
            "emotion": self.emotion,
            "action": self.action,
            "background": self.background,
            "camera": self.camera,
        }

    @classmethod
    def from_dict(cls, data: dict) -> StoryboardScene:
        return cls(
            index=data["index"],
            duration_s=data["duration_s"],
            dialogue=data["dialogue"],
            character=data.get("character", "tabby_cat"),
            emotion=data.get("emotion", "neutral"),
            action=data.get("action", ""),
            background=data.get("background", "simple_studio"),
            camera=data.get("camera", "medium_shot"),
        )


@dataclass
class Storyboard:
    scenes: list[StoryboardScene]
    total_duration_s: int
    style: str = "funny"

    def __post_init__(self):
        if len(self.scenes) < 1:
            raise ValueError("Storyboard must have at least 1 scene")
        if self.total_duration_s > 60:
            raise ValueError(
                f"total_duration_s must be <= 60, got {self.total_duration_s}"
            )
        if self.style not in VALID_STYLES:
            raise ValueError(
                f"Invalid style '{self.style}', must be one of {VALID_STYLES}"
            )
        computed = sum(s.duration_s for s in self.scenes)
        if abs(computed - self.total_duration_s) > 1:
            self.total_duration_s = computed

    def to_json(self) -> str:
        payload = {
            "scenes": [s.to_dict() for s in self.scenes],
            "total_duration_s": self.total_duration_s,
            "style": self.style,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def to_dict(self) -> dict:
        return {
            "scenes": [s.to_dict() for s in self.scenes],
            "total_duration_s": self.total_duration_s,
            "style": self.style,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Storyboard:
        scenes = [StoryboardScene.from_dict(s) for s in data["scenes"]]
        total = data.get("total_duration_s", 0)
        if total == 0:
            total = sum(s.duration_s for s in scenes)
        style = data.get("style", "funny")
        return cls(scenes=scenes, total_duration_s=total, style=style)
