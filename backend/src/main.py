"""
danshen_animation FastAPI 应用入口

API 路由：
  POST /api/v1/animate   — 提交视频生成任务
  GET  /api/v1/tasks/{id} — 查询任务状态
  GET  /api/v1/health    — 健康检查
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routes import tasks, animate, auth, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    print(f"🚀 {settings.app_name} started on http://{settings.host}:{settings.port}")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title="🔥 Danshen Animation",
    description="AI 驱动的动漫风格视频生成器 — 输入热点内容，生成可爱动物配音视频",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS（允许所有前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保输出目录存在（在 StaticFiles 挂载前）
settings.output_dir.mkdir(parents=True, exist_ok=True)

# 静态文件服务（输出视频和图片）
app.mount("/output", StaticFiles(directory=str(settings.output_dir)), name="output")

# 注册路由
app.include_router(animate.router, prefix=settings.api_prefix)
app.include_router(tasks.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(admin.router, prefix=settings.api_prefix)


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
