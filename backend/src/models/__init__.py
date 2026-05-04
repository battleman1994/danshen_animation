"""
数据模型定义

使用 Pydantic 进行数据验证和序列化。
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pathlib import Path

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    TEXT = "text"
    DOUYIN_VIDEO = "douyin_video"
    BILIBILI_VIDEO = "bilibili_video"
    YOUTUBE_VIDEO = "youtube_video"
    WEB_LINK = "web_link"
    IMAGE = "image"
    WEIBO_POST = "weibo_post"
    NEWS = "news"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    EXTRACTING = "extracting"
    ADAPTING = "adapting"
    GENERATING_CHARACTERS = "generating_characters"
    SYNTHESIZING_VOICE = "synthesizing_voice"
    COMPOSING_VIDEO = "composing_video"
    COMPLETED = "completed"
    FAILED = "failed"


class Character(str, Enum):
    TABBY_CAT = "tabby_cat"
    BROWN_BEAR = "brown_bear"
    LITTLE_FOX = "little_fox"
    PANDA = "panda"
    RABBIT = "rabbit"
    SHIBA_INU = "shiba_inu"
    OWL = "owl"
    PENGUIN = "penguin"
    LION = "lion"


class Emotion(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    FUNNY = "funny"
    SERIOUS = "serious"
    SURPRISED = "surprised"
    ANGRY = "angry"
    NEUTRAL = "neutral"


class ContentInput(BaseModel):
    """内容输入"""
    source: str = Field(..., min_length=1, max_length=5000)
    source_type: SourceType = SourceType.TEXT
    metadata: dict = Field(default_factory=dict)


class AnimationRequest(BaseModel):
    """视频生成请求"""
    content: ContentInput
    character: Character = Character.TABBY_CAT
    character_count: int = Field(default=2, ge=1, le=5)
    style: str = "auto"
    resolution: str = "1080p"
    subtitle: bool = True
    webhook_url: Optional[str] = None


class AnimationTask(BaseModel):
    """视频生成任务"""
    task_id: str
    status: TaskStatus = TaskStatus.QUEUED
    progress: int = 0
    request: AnimationRequest
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    result: Optional[dict] = None
    error: Optional[str] = None


class CharacterPreset(BaseModel):
    """角色预设"""
    name: str
    emoji: str
    style: str
    personality: str
    speech_style: str
    voice: str
