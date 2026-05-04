# ── 后端 Dockerfile ──
FROM python:3.11-slim

WORKDIR /app

# 系统依赖（FFmpeg for 视频处理）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY backend/pyproject.toml backend/
COPY backend/src/ backend/src/
RUN pip install --no-cache-dir -e backend/.

# 输出目录
RUN mkdir -p /app/output/{audio,videos,characters,backgrounds}

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
