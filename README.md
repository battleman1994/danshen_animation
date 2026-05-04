<p align="center">
  <img src="https://img.shields.io/badge/🔥-danshen_animation-ff6b6b?style=for-the-badge" alt="danshen_animation">
</p>

<h1 align="center">🔥 单身动画 — Danshen Animation</h1>
<p align="center"><strong>AI 驱动的动漫风格视频生成器</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-iOS%20%7C%20Web%20%7C%20Windows-blue" alt="platforms">
  <img src="https://img.shields.io/badge/python-3.10+-green" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="license">
</p>

---

## 🎬 这是什么？

**单身动画** 是一个 AI 驱动的视频生成工具。你给它热点内容（图片、文字、链接、视频），它帮你生成**动漫风格**的配音视频。

### 典型场景

| 输入 | 输出 |
|------|------|
| 🎵 抖音两个人搞笑对话 | 🐱 两只狸花猫演绎同样对话 |
| 📰 热点新闻 | 🐻 可爱的动物严肃/可爱播报 |
| 🖼️ 一张表情包 | 🎭 动漫角色配音演绎 |
| 🔗 微博/小红书帖子 | 🦊 小狐狸配音朗读 |

---

## 🏗️ 架构总览

```
┌──────────────────────────────────────────────────┐
│                   输入端                          │
│   📝 文字  🖼️ 图片  🔗 链接  🎵 视频URL         │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│              AI 视频生成流水线                     │
│                                                   │
│  ① 内容提取 → ② 脚本改编 → ③ 角色生成            │
│         → ④ 语音合成 → ⑤ 视频合成                │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│                   输出端                          │
│     iOS App  │  Web 浏览器  │  Windows 桌面       │
└──────────────────────────────────────────────────┘
```

### AI 流水线详解

1. **内容提取** (`extractor`) — Whisper 转写音频、OCR 识别图片文字、爬虫抓取链接内容、LLM 理解语义
2. **脚本改编** (`adapter`) — LLM 将原始内容改写为适合动漫角色的脚本，保留原意，适配角色语气
3. **角色生成** (`character`) — ComfyUI / Stable Diffusion 生成动漫动物角色（狸花猫🐱、狐狸🦊、熊猫🐼...）
4. **语音合成** (`voice`) — TTS 引擎合成配音，匹配内容情绪（开心/严肃/搞笑）
5. **视频合成** (`composer`) — FFmpeg / MoviePy 组合角色动画 + 配音 + 字幕 + 背景

---

## 🚀 快速开始

### 后端

```bash
cd backend
pip install -e ".[dev]"
uvicorn src.main:app --reload
```

### Web 前端

```bash
cd web
npm install
npm run dev
```

### iOS

```bash
cd ios/DanshenAnimation
open DanshenAnimation.xcodeproj
```

### Windows

```bash
cd windows/electron
npm install
npm start
```

---

## 📂 项目结构

```
danshen_animation/
├── backend/               # Python FastAPI 后端
│   ├── src/
│   │   ├── main.py        # FastAPI 入口
│   │   ├── config.py      # 配置管理
│   │   ├── pipeline/      # 🔥 AI 视频生成流水线
│   │   │   ├── extractor.py    # 内容提取
│   │   │   ├── adapter.py      # 脚本改编
│   │   │   ├── character.py    # 角色生成
│   │   │   ├── voice.py        # 语音合成
│   │   │   └── composer.py     # 视频合成
│   │   ├── models/        # 数据模型
│   │   ├── routes/        # API 路由
│   │   └── utils/         # 工具函数
│   └── tests/
├── web/                   # Next.js Web 前端
├── ios/                   # SwiftUI iOS App
├── windows/               # Electron Windows 桌面端
├── shared/                # 共享类型定义
└── docs/                  # 文档
```

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python + FastAPI |
| AI 模型 | Whisper, LLM (DeepSeek/OpenAI), Stable Diffusion |
| 语音合成 | Edge TTS / ElevenLabs / Coqui TTS |
| 视频合成 | FFmpeg + MoviePy |
| Web 前端 | Next.js + React + TailwindCSS |
| iOS | SwiftUI |
| Windows | Electron + React |
| 任务队列 | Celery + Redis |

---

## 📋 开发计划

详见 [docs/plan.md](docs/plan.md)

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License
