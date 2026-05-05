<p align="center">
  <img src="https://img.shields.io/badge/🔥-danshen_animation-5e6ad2?style=for-the-badge" alt="danshen_animation">
</p>

<h1 align="center">🔥 单身动画 — Danshen Animation</h1>
<p align="center"><strong>AI 驱动的动漫风格视频生成器</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/桌面-Rust%20%7C%20Dioxus-5e6ad2" alt="desktop">
  <img src="https://img.shields.io/badge/后端-Python%20%7C%20FastAPI-28a745" alt="backend">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="license">
</p>

<p align="center">
  <sub>🎨 双主题 UI：暗色 Linear 风格 · 暖色 Claude 风格</sub>
</p>

<p align="center">
  <a href="sketches/001-linear-dark/index.html">🌙 暗色主题预览</a> ·
  <a href="sketches/002-claude-warm/index.html">☀️ 暖色主题预览</a>
</p>

---

## 🎬 这是什么？

**单身动画** 是一个 AI 驱动的视频生成工具。你给它热点内容（图片、文字、链接、视频），它帮你生成**动漫风格**的配音视频——角色是可爱的动物们 🐱🐻🦊！

### 🎨 UI 设计预览

我们提供了两套完整的设计方案，打开即可在浏览器中预览：

| 暗色 Linear 风格 | 暖色 Claude 风格 |
|:---:|:---:|
| 🌙 受 Linear.app / Cursor 启发 | ☀️ 受 Claude AI / Notion 启发 |
| 黑底 + 靛紫强调色 | 羊皮纸底 + 陶土红强调色 |
| 科技极简，专注高效 | 温暖亲切，人情味十足 |
| **[预览 →](sketches/001-linear-dark/index.html)** | **[预览 →](sketches/002-claude-warm/index.html)** |

> 💡 桌面端默认使用**暗色 Linear 风格**，支持一键切换主题。

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
│               跨平台桌面客户端                     │
│       Rust + Dioxus (macOS / Windows / Web)      │
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

### 桌面客户端（macOS / 开发模式）

```bash
# 启动 Dioxus 桌面应用
cargo run

# 启动 Dioxus Web 版本
cargo run --features web
```

> 桌面端默认使用 macOS 原生窗口渲染，无需额外配置。

---

## 📂 项目结构

```
danshen_animation/
├── src/                    # 🦀 Rust + Dioxus 桌面客户端
│   ├── main.rs             # 入口，启动桌面应用
│   ├── app.rs              # 主组件（主题切换、布局）
│   ├── components/         # UI 组件
│   │   ├── header.rs       # 页眉
│   │   ├── scene_selector.rs   # 场景选择
│   │   ├── source_input.rs     # 源内容输入
│   │   ├── character_grid.rs   # 角色选择网格
│   │   ├── style_selector.rs   # 风格选择
│   │   ├── submit_button.rs    # 提交按钮
│   │   ├── progress_bar.rs     # 进度条
│   │   ├── result_card.rs      # 结果展示卡片
│   │   ├── news_mode_hint.rs   # 新闻模式提示
│   │   ├── decorative_blobs.rs # 装饰背景元素
│   │   └── footer.rs           # 页脚
│   ├── hooks/              # 自定义 Hooks
│   ├── styles/             # 样式系统
│   │   ├── theme.rs        # 🌈 双主题系统（暗色/暖色）
│   │   ├── tailwind.css    # CSS 工具类
│   │   └── mod.rs          # 模块导出
├── backend/                # 🐍 Python FastAPI 后端
│   ├── src/
│   │   ├── main.py         # FastAPI 入口
│   │   ├── config.py       # 配置管理
│   │   ├── pipeline/       # 🔥 AI 视频生成流水线
│   │   │   ├── extractor.py     # 内容提取
│   │   │   ├── adapter.py       # 脚本改编
│   │   │   ├── character.py     # 角色生成
│   │   │   ├── voice.py         # 语音合成
│   │   │   └── composer.py      # 视频合成
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # API 路由
│   │   └── utils/          # 工具函数
│   └── tests/
├── sketches/               # 🎨 UI 设计稿
│   ├── 001-linear-dark/    # 🌙 暗色 Linear 风格
│   └── 002-claude-warm/    # ☀️ 暖色 Claude 风格
└── docs/                   # 📚 文档
```

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 桌面客户端 | **Rust** + **Dioxus**（跨平台：macOS / Windows / Web） |
| 后端框架 | Python + FastAPI |
| AI 模型 | Whisper, LLM (DeepSeek/OpenAI), Stable Diffusion |
| 语音合成 | Edge TTS / ElevenLabs / Coqui TTS |
| 视频合成 | FFmpeg + MoviePy |
| 主题系统 | Rust 内联样式 + CSS 工具类（双主题：暗色/暖色） |
| 任务队列 | Celery + Redis |

### 为什么选择 Rust + Dioxus？

| 对比项 | Rust + Dioxus | Next.js + Web | Electron |
|--------|:---:|:---:|:---:|
| 性能 | 🚀 原生编译 | ⚡ 浏览器 | 🐢 浏览器 |
| 跨平台 | ✅ macOS/Win/Web | ✅ 仅 Web | ✅ macOS/Win |
| 包体积 | 小巧 (~5MB) | 中 | 臃肿 (~150MB) |
| 开发体验 | Rust 类型安全 | JS 生态成熟 | JS 生态成熟 |

---

## 📋 开发计划

详见 [docs/plan.md](docs/plan.md)

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License
