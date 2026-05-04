# 🔥 单身动画 — 实现计划

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 构建 AI 驱动的动漫风格视频生成器，支持 iOS / Web / Windows 三端

**Architecture:** FastAPI 后端 + 五阶段视频生成流水线 + Next.js Web + SwiftUI iOS + Electron Windows

**Tech Stack:** Python/FastAPI, Whisper, ComfyUI/SDXL, Edge-TTS, FFmpeg, Next.js, SwiftUI, Electron

---

## Phase 1: 后端基础设施

### Task 1.1: 项目初始化与依赖安装

**Objective:** 安装后端依赖，确保项目可运行

**Files:**
- Create: `backend/.env`
- Modify: `backend/pyproject.toml`

**Step 1: 创建虚拟环境**
```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

**Step 2: 配置环境变量**
```bash
cp .env.example .env
# 编辑 .env，填入 LLM API Key 等
```

**Step 3: 验证启动**
```bash
uvicorn src.main:app --reload
# 预期: http://localhost:8000/docs 可访问
```

### Task 1.2: 配置管理

**Objective:** 完善配置系统，支持 .env 和环境变量

**Files:**
- Modify: `backend/src/config.py`

**Step 1:** 添加更多配置项验证
**Step 2:** 添加配置热加载
**Step 3:** 单元测试

```bash
pytest tests/test_config.py -v
```

### Task 1.3: Celery 任务队列

**Objective:** 将视频生成改为异步 Celery 任务

**Files:**
- Create: `backend/src/worker.py`
- Modify: `backend/src/routes/animate.py`

**Step 1:** 安装 Redis 并启动
```bash
redis-server
```

**Step 2:** 启动 Celery Worker
```bash
celery -A src.worker worker --loglevel=info
```

**Step 3:** 修改 `/animate` 路由使用 Celery 任务

---

## Phase 2: AI 流水线

### Task 2.1: 视频下载与音频提取

**Objective:** 完善 extractor 模块的抖音/B站下载

**Files:**
- Modify: `backend/src/pipeline/extractor.py`

**Step 1:** 测试 yt-dlp 下载
```bash
yt-dlp -f best "https://v.douyin.com/xxxxx" -o test.mp4
```

**Step 2:** 测试 Whisper 转写
```python
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu")
segments, _ = model.transcribe("test.wav", language="zh")
```

**Step 3:** 单元测试
```bash
pytest tests/test_extractor.py -v
```

### Task 2.2: 说话人分离

**Objective:** 多人对话中识别不同说话人

**Files:**
- Modify: `backend/src/pipeline/extractor.py`

**Step 1:** 集成 pyannote-audio
```bash
pip install pyannote.audio
```

**Step 2:** 实现 `_transcribe_with_speakers()`

**Step 3:** 测试对话分离准确率

### Task 2.3: 脚本改编优化

**Objective:** 改进 LLM 脚本改编质量

**Files:**
- Modify: `backend/src/pipeline/adapter.py`

**Step 1:** 优化 prompt 模板
**Step 2:** 添加角色库扩展（支持自定义角色）
**Step 3:** 添加脚本后处理（长度控制、情绪校验）
**Step 4:** 测试
```bash
pytest tests/test_adapter.py -v
```

### Task 2.4: ComfyUI 集成

**Objective:** 连接 ComfyUI 生成角色图片

**Files:**
- Modify: `backend/src/pipeline/character.py`

**Step 1:** 启动 ComfyUI
```bash
cd ComfyUI && python main.py
```

**Step 2:** 加载 SDXL 模型和 LoRA
**Step 3:** 测试角色图片生成
**Step 4:** 添加图片缓存机制

### Task 2.5: TTS 引擎完善

**Objective:** 多角色多情绪 TTS

**Files:**
- Modify: `backend/src/pipeline/voice.py`

**Step 1:** 测试 Edge-TTS 中文效果
**Step 2:** 添加 ElevenLabs 集成
**Step 3:** 添加音效后处理（混响、EQ）
**Step 4:** 测试
```bash
pytest tests/test_voice.py -v
```

### Task 2.6: FFmpeg 视频合成

**Objective:** 完善视频合成，支持口型同步

**Files:**
- Modify: `backend/src/pipeline/composer.py`

**Step 1:** 实现基础合成流程
**Step 2:** 添加字幕烧录
**Step 3:** 添加转场效果
**Step 4:** 集成 Wav2Lip 口型同步
**Step 5:** 端到端测试

---

## Phase 3: Web 前端

### Task 3.1: Next.js 项目初始化

**Objective:** 创建 Next.js 前端项目

**Files:**
- Create: `web/src/app/layout.tsx`
- Create: `web/tailwind.config.js`
- Create: `web/postcss.config.js`
- Create: `web/tsconfig.json`

**Step 1:** 初始化项目
```bash
cd web && npm install && npm run dev
```

**Step 2:** 配置 TailwindCSS
**Step 3:** 创建基础布局

### Task 3.2: 动画生成页面完善

**Objective:** 完善首页交互

**Files:**
- Modify: `web/src/app/page.tsx`

**Step 1:** 添加上传图片功能（react-dropzone）
**Step 2:** 添加进度条显示
**Step 3:** 添加历史记录

### Task 3.3: 视频播放器

**Objective:** 自定义视频播放器组件

**Files:**
- Create: `web/src/components/VideoPlayer.tsx`

### Task 3.4: 响应式设计

**Objective:** 适配移动端和桌面端

---

## Phase 4: iOS App

### Task 4.1: SwiftUI 项目配置

**Objective:** 完善 Xcode 项目配置

**Files:**
- Create: `ios/DanshenAnimation.xcodeproj/`

**Step 1:** 在 Xcode 中打开项目
**Step 2:** 配置 Info.plist（网络权限等）
**Step 3:** 添加依赖（Alamofire / URLSession）

### Task 4.2: API 集成

**Objective:** 连接后端 API

**Files:**
- Create: `ios/DanshenAnimation/APIService.swift`
- Modify: `ios/DanshenAnimation/ContentView.swift`

**Step 1:** 实现网络请求层
**Step 2:** 实现任务轮询
**Step 3:** 视频播放

---

## Phase 5: Windows 桌面端

### Task 5.1: Electron 配置完善

**Objective:** 完善 Electron 打包配置

**Files:**
- Modify: `windows/electron/main.js`
- Create: `windows/electron/preload.js`

**Step 1:** 测试启动
```bash
cd windows/electron && npm install && npm start
```

**Step 2:** 配置自动更新
**Step 3:** 测试打包
```bash
npm run build
```

---

## Phase 6: 测试与部署

### Task 6.1: 单元测试

```bash
cd backend && pytest tests/ -v --cov=src
```

### Task 6.2: 集成测试

端到端测试完整流水线

### Task 6.3: Docker 部署

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

```bash
docker-compose up -d
```

### Task 6.4: CI/CD

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/deploy.yml`

---

## 里程碑

| 里程碑 | 目标 | 预计时间 |
|--------|------|---------|
| M1: MVP | 文字→视频基本流程 | 2 周 |
| M2: 视频源 | 支持抖音/B站链接 | +1 周 |
| M3: Web 端 | 完整 Web 前端 | +1 周 |
| M4: 角色系统 | 8个角色 + 情绪表情 | +1 周 |
| M5: iOS 端 | SwiftUI App 上架 | +2 周 |
| M6: Windows 端 | Electron 打包发布 | +1 周 |
| M7: 生产就绪 | Docker + CI/CD + 监控 | +1 周 |
