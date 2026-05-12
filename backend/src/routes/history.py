"""
视频生成记录路由 — 用户查看自己的生成记录
"""

import logging

from fastapi import APIRouter, Depends

from ..auth import require_user
from ..database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
async def list_history(
    status: str = "",
    limit: int = 20,
    offset: int = 0,
    user: dict = Depends(require_user),
):
    db = await get_db()
    where = "WHERE user_id = ?"
    params: list = [user["id"]]

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

    return {"items": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}


@router.get("/{history_id}")
async def get_history(history_id: str, user: dict = Depends(require_user)):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM video_history WHERE id = ? AND user_id = ?",
        (history_id, user["id"]),
    )
    row = await cursor.fetchone()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(404, "记录不存在")
    return {"item": dict(row)}
