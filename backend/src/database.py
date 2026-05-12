"""
数据库层 — SQLite (aiosqlite)

管理所有持久化数据：用户、会话、提示词资产、评分、视频生成记录。
"""

import json
import logging
import sqlite3
import uuid
from pathlib import Path
from typing import Optional

import aiosqlite

from .config import settings

logger = logging.getLogger(__name__)

DB_PATH: Optional[Path] = None
DB_POOL: Optional[aiosqlite.Connection] = None


async def get_db() -> aiosqlite.Connection:
    """获取数据库连接（单连接复用，SQLite 写操作串行化安全）"""
    global DB_POOL
    if DB_POOL is None:
        DB_POOL = await aiosqlite.connect(str(DB_PATH))
        DB_POOL.row_factory = aiosqlite.Row
        await DB_POOL.execute("PRAGMA journal_mode=WAL")
        await DB_POOL.execute("PRAGMA foreign_keys=ON")
    return DB_POOL


async def init_db():
    """初始化数据库文件和表结构"""
    global DB_PATH
    DB_PATH = Path(settings.database_url.replace("sqlite:///", ""))
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys=ON")

        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                nickname TEXT NOT NULL,
                avatar_url TEXT DEFAULT '',
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                provider TEXT NOT NULL,
                provider_uid TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(provider, provider_uid)
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS prompt_assets (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                prompt_template TEXT NOT NULL,
                description TEXT DEFAULT '',
                source_type TEXT NOT NULL DEFAULT 'system',
                source_url TEXT DEFAULT '',
                source_author TEXT DEFAULT '',
                scene_type TEXT NOT NULL DEFAULT 'general',
                character_id TEXT NOT NULL DEFAULT 'orange_tabby',
                cover_keywords TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                rating_avg REAL DEFAULT 0,
                rating_count INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'draft',
                created_by TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS prompt_ratings (
                id TEXT PRIMARY KEY,
                prompt_id TEXT NOT NULL REFERENCES prompt_assets(id) ON DELETE CASCADE,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                score INTEGER NOT NULL CHECK(score >= 1 AND score <= 5),
                created_at TEXT NOT NULL,
                UNIQUE(prompt_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS video_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                task_id TEXT NOT NULL,
                source TEXT NOT NULL,
                source_type TEXT NOT NULL DEFAULT 'text',
                character_id TEXT NOT NULL,
                prompt_used TEXT NOT NULL,
                provider TEXT NOT NULL,
                llm_model TEXT NOT NULL,
                video_url TEXT DEFAULT '',
                title TEXT DEFAULT '',
                duration_estimate INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                error TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
        """)
        await db.commit()

    logger.info("Database initialized at %s", DB_PATH)
    # 预热连接
    await get_db()


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
