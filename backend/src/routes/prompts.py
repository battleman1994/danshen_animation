"""
提示词库路由 — 用户浏览已上架提示词 / 打分 / 创建自定义提示词
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..auth import require_user
from ..database import get_db, new_id, now

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prompts", tags=["prompts"])


# ── 请求模型 ──

class CreatePromptRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    prompt_template: str = Field(..., min_length=10, max_length=5000)
    description: str = Field(default="", max_length=500)
    scene_type: str = Field(default="general")
    character_id: str = Field(default="orange_tabby")
    tags: list[str] = Field(default_factory=list)


class UpdatePromptRequest(BaseModel):
    title: str | None = None
    prompt_template: str | None = None
    description: str | None = None
    scene_type: str | None = None
    character_id: str | None = None
    tags: list[str] | None = None


class RateRequest(BaseModel):
    score: int = Field(..., ge=1, le=5)


# ── 端点 ──

@router.get("")
async def list_prompts(
    scene_type: str = "",
    character_id: str = "",
    search: str = "",
    sort: str = "rating",  # rating, newest, usage
    limit: int = 20,
    offset: int = 0,
    user: dict = Depends(require_user),
):
    """已上架的提示词列表，按评分降序"""
    db = await get_db()
    where = "WHERE p.status = 'published'"
    params: list = []

    if scene_type:
        where += " AND p.scene_type = ?"
        params.append(scene_type)
    if character_id:
        where += " AND p.character_id = ?"
        params.append(character_id)
    if search:
        where += " AND (p.title LIKE ? OR p.description LIKE ? OR p.tags LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    order = "p.rating_avg DESC, p.rating_count DESC" if sort == "rating" else \
            "p.created_at DESC" if sort == "newest" else \
            "p.usage_count DESC"

    cursor = await db.execute(
        f"SELECT * FROM prompt_assets p {where} ORDER BY {order} LIMIT ? OFFSET ?",
        params + [limit, offset],
    )
    rows = await cursor.fetchall()

    cursor2 = await db.execute(f"SELECT COUNT(*) FROM prompt_assets p {where}", params)
    total = (await cursor2.fetchone())[0]

    items = [_prompt_row(r) for r in rows]
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{prompt_id}")
async def get_prompt(prompt_id: str, user: dict = Depends(require_user)):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM prompt_assets WHERE id = ? AND status = 'published'",
        (prompt_id,),
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(404, "提示词不存在或未上架")
    return {"item": _prompt_row(row)}


@router.post("/{prompt_id}/rate")
async def rate_prompt(prompt_id: str, req: RateRequest, user: dict = Depends(require_user)):
    db = await get_db()
    # 检查提示词是否存在且已上架
    cursor = await db.execute(
        "SELECT id FROM prompt_assets WHERE id = ? AND status = 'published'",
        (prompt_id,),
    )
    if not await cursor.fetchone():
        raise HTTPException(404, "提示词不存在或未上架")

    rate_id = new_id()
    try:
        await db.execute(
            "INSERT INTO prompt_ratings (id, prompt_id, user_id, score, created_at) VALUES (?, ?, ?, ?, ?)",
            (rate_id, prompt_id, user["id"], req.score, now()),
        )
    except Exception:
        # 已打过分的更新分数
        await db.execute(
            "UPDATE prompt_ratings SET score = ?, created_at = ? WHERE prompt_id = ? AND user_id = ?",
            (req.score, now(), prompt_id, user["id"]),
        )

    # 更新平均分
    cursor = await db.execute(
        "SELECT AVG(score), COUNT(*) FROM prompt_ratings WHERE prompt_id = ?",
        (prompt_id,),
    )
    avg_row = await cursor.fetchone()
    await db.execute(
        "UPDATE prompt_assets SET rating_avg = ?, rating_count = ?, updated_at = ? WHERE id = ?",
        (round(avg_row[0], 2), avg_row[1], now(), prompt_id),
    )
    await db.commit()
    return {"success": True, "message": "评分成功"}


@router.post("")
async def create_prompt(req: CreatePromptRequest, user: dict = Depends(require_user)):
    db = await get_db()
    prompt_id = new_id()
    await db.execute(
        """INSERT INTO prompt_assets (id, title, prompt_template, description, source_type,
           scene_type, character_id, tags, status, created_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'user', ?, ?, ?, 'draft', ?, ?, ?)""",
        (prompt_id, req.title, req.prompt_template, req.description,
         req.scene_type, req.character_id, json.dumps(req.tags),
         user["id"], now(), now()),
    )
    await db.commit()
    return {"success": True, "prompt_id": prompt_id}


@router.put("/{prompt_id}")
async def update_prompt(prompt_id: str, req: UpdatePromptRequest, user: dict = Depends(require_user)):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM prompt_assets WHERE id = ?", (prompt_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(404, "提示词不存在")
    if row["created_by"] != user["id"]:
        raise HTTPException(403, "只能编辑自己的提示词")

    updates = {}
    for k in ("title", "prompt_template", "description", "scene_type", "character_id"):
        v = getattr(req, k, None)
        if v is not None:
            updates[k] = v
    if req.tags is not None:
        updates["tags"] = json.dumps(req.tags)
    if updates:
        updates["updated_at"] = now()
        sets = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [prompt_id]
        await db.execute(f"UPDATE prompt_assets SET {sets} WHERE id = ?", vals)
        await db.commit()
    return {"success": True}


@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str, user: dict = Depends(require_user)):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM prompt_assets WHERE id = ?", (prompt_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(404, "提示词不存在")
    if row["created_by"] != user["id"]:
        raise HTTPException(403, "只能删除自己的提示词")
    await db.execute("DELETE FROM prompt_assets WHERE id = ?", (prompt_id,))
    await db.commit()
    return {"success": True}


# ── helpers ──

def _prompt_row(r) -> dict:
    d = dict(r)
    d["tags"] = json.loads(d.get("tags", "[]"))
    return d
