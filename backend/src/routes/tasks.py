"""
GET /api/v1/tasks/{task_id} — 查询任务状态

轮询接口，前端可以定期查询任务进度。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from .animate import _task_store

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int = 0
    result: Optional[dict] = None
    error: Optional[str] = None


@router.get("/{task_id}", response_model=TaskStatus)
async def get_task(task_id: str):
    """查询任务状态"""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatus(
        task_id=task["task_id"],
        status=task["status"],
        progress=task["progress"],
        result=task.get("result"),
        error=task.get("error"),
    )


@router.get("")
async def list_tasks(limit: int = 20, status: Optional[str] = None):
    """列出所有任务"""
    tasks = list(_task_store.values())
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    tasks.sort(key=lambda t: t["task_id"], reverse=True)
    return tasks[:limit]
