"""
Admin 管理后台路由骨架

后续将在此添加：
- 内置模型管理（CRUD）
- 系统配置管理
- 任务队列监控
- 用量统计
"""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
async def admin_dashboard():
    return {
        "status": "ok",
        "service": "danshen_admin",
        "version": "0.1.0",
        "features": [],
    }


@router.get("/health")
async def admin_health():
    return {"status": "ok", "module": "admin"}


@router.get("/models")
async def list_managed_models():
    """列出平台管理的内置模型（占位，后续从配置/数据库读取）"""
    from ..pipeline.prompt_builder import list_llm_models
    from ..pipeline.video_gen import list_providers
    return {
        "llm_models": list_llm_models(),
        "video_providers": list_providers(),
    }
