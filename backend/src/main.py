"""
danshen_animation FastAPI 应用入口

API 路由：
  POST /api/v1/animate   — 提交视频生成任务
  GET  /api/v1/tasks/{id} — 查询任务状态
  GET  /api/v1/health    — 健康检查
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routes import animate, tasks, auth, prompts, admin, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    await init_db()
    print(f"🚀 {settings.app_name} started on http://{settings.host}:{settings.port}")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title="🔥 Danshen Animation",
    description="AI 驱动的动漫风格视频生成器 — 输入热点内容，生成可爱动物配音视频",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(animate.router, prefix=settings.api_prefix)
app.include_router(tasks.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(prompts.router, prefix=settings.api_prefix)
app.include_router(admin.router, prefix=settings.api_prefix)
app.include_router(history.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": f"http://{settings.host}:{settings.port}/docs",
        "api": f"{settings.api_prefix}/",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
