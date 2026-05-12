"""
后台管理路由 — 提示词资产管理 / 用户管理 / 数据统计
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..auth import require_admin
from ..database import get_db, new_id, now
from ..pipeline.prompt_builder import PromptBuilder, CHARACTER_INFO

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# ═══════════════════════════════════════════════════════════════════════════════
# 请求模型
# ═══════════════════════════════════════════════════════════════════════════════

class AdminCreatePromptRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    prompt_template: str = Field(..., min_length=10, max_length=5000)
    description: str = Field(default="", max_length=500)
    scene_type: str = Field(default="general")
    character_id: str = Field(default="orange_tabby")
    tags: list[str] = Field(default_factory=list)
    source_author: str = Field(default="")
    source_url: str = Field(default="")


class AdminUpdatePromptRequest(BaseModel):
    title: str | None = None
    prompt_template: str | None = None
    description: str | None = None
    scene_type: str | None = None
    character_id: str | None = None
    tags: list[str] | None = None
    source_author: str | None = None


class ExtractPromptRequest(BaseModel):
    url: str = Field(..., min_length=1)
    character_id: str = Field(default="orange_tabby")
    scene_type: str = Field(default="")


class UpdateUserRequest(BaseModel):
    role: str | None = Field(None, pattern="^(admin|user)$")
    status: str | None = Field(None, pattern="^(active|disabled)$")


# ═══════════════════════════════════════════════════════════════════════════════
# 提示词管理
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/prompts")
async def admin_list_prompts(
    status: str = "",
    source_type: str = "",
    search: str = "",
    limit: int = 50,
    offset: int = 0,
    user: dict = Depends(require_admin),
):
    db = await get_db()
    where = "WHERE 1=1"
    params: list = []

    if status:
        where += " AND status = ?"
        params.append(status)
    if source_type:
        where += " AND source_type = ?"
        params.append(source_type)
    if search:
        where += " AND (title LIKE ? OR source_author LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s])

    cursor = await db.execute(
        f"SELECT * FROM prompt_assets {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    )
    rows = await cursor.fetchall()

    cursor2 = await db.execute(f"SELECT COUNT(*) FROM prompt_assets {where}", params)
    total = (await cursor2.fetchone())[0]

    return {"items": [_row(r) for r in rows], "total": total}


@router.post("/prompts")
async def admin_create_prompt(req: AdminCreatePromptRequest, user: dict = Depends(require_admin)):
    db = await get_db()
    prompt_id = new_id()
    await db.execute(
        """INSERT INTO prompt_assets
           (id, title, prompt_template, description, source_type, source_url, source_author,
            scene_type, character_id, tags, status, created_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'system', ?, ?, ?, ?, ?, 'draft', ?, ?, ?)""",
        (prompt_id, req.title, req.prompt_template, req.description,
         req.source_url, req.source_author,
         req.scene_type, req.character_id, json.dumps(req.tags),
         user["id"], now(), now()),
    )
    await db.commit()
    return {"success": True, "prompt_id": prompt_id}


@router.put("/prompts/{prompt_id}")
async def admin_update_prompt(
    prompt_id: str, req: AdminUpdatePromptRequest, user: dict = Depends(require_admin)
):
    db = await get_db()
    cursor = await db.execute("SELECT id FROM prompt_assets WHERE id = ?", (prompt_id,))
    if not await cursor.fetchone():
        raise HTTPException(404, "提示词不存在")

    updates = {}
    for k in ("title", "prompt_template", "description", "scene_type", "character_id", "source_author"):
        v = getattr(req, k, None)
        if v is not None:
            updates[k] = v
    if req.tags is not None:
        updates["tags"] = json.dumps(req.tags)
    if updates:
        updates["updated_at"] = now()
        sets = ", ".join(f"{k} = ?" for k in updates)
        await db.execute(f"UPDATE prompt_assets SET {sets} WHERE id = ?", list(updates.values()) + [prompt_id])
        await db.commit()
    return {"success": True}


@router.delete("/prompts/{prompt_id}")
async def admin_delete_prompt(prompt_id: str, user: dict = Depends(require_admin)):
    db = await get_db()
    await db.execute("DELETE FROM prompt_assets WHERE id = ?", (prompt_id,))
    await db.commit()
    return {"success": True}


@router.post("/prompts/{prompt_id}/publish")
async def admin_toggle_publish(prompt_id: str, user: dict = Depends(require_admin)):
    db = await get_db()
    cursor = await db.execute("SELECT id, status FROM prompt_assets WHERE id = ?", (prompt_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(404, "提示词不存在")

    new_status = "draft" if row["status"] == "published" else "published"
    await db.execute(
        "UPDATE prompt_assets SET status = ?, updated_at = ? WHERE id = ?",
        (new_status, now(), prompt_id),
    )
    await db.commit()
    return {"success": True, "status": new_status, "message": "已上架" if new_status == "published" else "已下架"}


# ═══════════════════════════════════════════════════════════════════════════════
# 提示词提取（从视频/博客 URL 分析并提取提示词模板）
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/prompts/extract")
async def admin_extract_prompt(req: ExtractPromptRequest, user: dict = Depends(require_admin)):
    """从外部视频或博客链接提取提示词模板"""
    from ..pipeline.content_fetcher import fetch_content

    try:
        raw = await fetch_content(req.url, "web_link")
    except Exception as e:
        raise HTTPException(400, f"内容抓取失败: {e}")

    builder = PromptBuilder()
    char_info = CHARACTER_INFO.get(req.character_id, CHARACTER_INFO["orange_tabby"])

    system_prompt = (
        "你是一个提示词逆向工程专家。用户会给你一段热门短视频的描述或文案，"
        "你需要反推出这个视频的 AI 视频生成提示词模板。"
        "提示词必须是英文（200-400词），包含：主角外貌、场景、动作、运镜、光线、风格。"
        "同时给出视频标题（中文）、场景分类（daily_life/skit_comedy/social_commentary/pet_moments）。"
        "返回 JSON：{\"prompt\": \"...\", \"title\": \"...\", \"scene_type\": \"...\", \"tags\": [...]}"
    )

    user_prompt = (
        f"分析以下热门视频内容，反推 AI 视频生成提示词模板：\n\n{raw[:3000]}\n\n"
        f"指定角色：{char_info['name']} {char_info['emoji']}\n"
        f"外貌：{char_info['appearance']}\n"
        f"性格：{char_info['personality']}"
    )

    raw_response = await builder._call_llm(system_prompt, user_prompt)
    parsed = builder._parse(raw_response, req.character_id)

    return {
        "success": True,
        "extracted": {
            "title": parsed.title,
            "prompt_template": parsed.prompt,
            "scene_type": parsed.scene_type,
            "character_id": parsed.character,
            "source_url": req.url,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 用户管理
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/users")
async def admin_list_users(
    search: str = "",
    role: str = "",
    limit: int = 50,
    offset: int = 0,
    user: dict = Depends(require_admin),
):
    db = await get_db()
    where = "WHERE 1=1"
    params: list = []
    if role:
        where += " AND role = ?"
        params.append(role)
    if search:
        where += " AND (nickname LIKE ? OR phone LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s])

    cursor = await db.execute(
        f"SELECT id, nickname, avatar_url, phone, provider, role, status, created_at FROM users {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    )
    rows = await cursor.fetchall()
    cursor2 = await db.execute(f"SELECT COUNT(*) FROM users {where}", params)
    total = (await cursor2.fetchone())[0]
    return {"items": [dict(r) for r in rows], "total": total}


@router.put("/users/{user_id}")
async def admin_update_user(user_id: str, req: UpdateUserRequest, user: dict = Depends(require_admin)):
    db = await get_db()
    cursor = await db.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not await cursor.fetchone():
        raise HTTPException(404, "用户不存在")

    updates = {}
    if req.role is not None:
        updates["role"] = req.role
    if req.status is not None:
        updates["status"] = req.status
    if updates:
        updates["updated_at"] = now()
        sets = ", ".join(f"{k} = ?" for k in updates)
        await db.execute(f"UPDATE users SET {sets} WHERE id = ?", list(updates.values()) + [user_id])
        await db.commit()
    return {"success": True}


# ═══════════════════════════════════════════════════════════════════════════════
# 记录管理
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/history")
async def admin_list_history(
    status: str = "",
    limit: int = 50,
    offset: int = 0,
    user: dict = Depends(require_admin),
):
    db = await get_db()
    where = "WHERE 1=1"
    params: list = []
    if status:
        where += " AND status = ?"
        params.append(status)

    cursor = await db.execute(
        f"SELECT * FROM video_history {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    )
    rows = await cursor.fetchall()
    cursor2 = await db.execute(f"SELECT COUNT(*) FROM video_history {where}", params)
    total = (await cursor2.fetchone())[0]
    return {"items": [dict(r) for r in rows], "total": total}


# ═══════════════════════════════════════════════════════════════════════════════
# 统计数据
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/stats")
async def admin_stats(user: dict = Depends(require_admin)):
    db = await get_db()

    async def count(table, where=""):
        c = await db.execute(f"SELECT COUNT(*) FROM {table} {where}")
        return (await c.fetchone())[0]

    return {
        "users_total": await count("users"),
        "users_active": await count("users", "WHERE status = 'active'"),
        "prompts_total": await count("prompt_assets"),
        "prompts_published": await count("prompt_assets", "WHERE status = 'published'"),
        "prompts_draft": await count("prompt_assets", "WHERE status = 'draft'"),
        "video_total": await count("video_history"),
        "video_completed": await count("video_history", "WHERE status = 'completed'"),
        "video_failed": await count("video_history", "WHERE status = 'failed'"),
    }


# ── helpers ──

def _row(r) -> dict:
    d = dict(r)
    d["tags"] = json.loads(d.get("tags", "[]"))
    return d
