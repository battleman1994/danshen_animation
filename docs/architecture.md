# 🏗️ 架构设计文档

## 1. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │ iOS App  │    │ Web Browser  │    │ Windows Desktop  │  │
│  │ SwiftUI  │    │ Next.js+React│    │    Electron      │  │
│  └────┬─────┘    └──────┬───────┘    └────────┬─────────┘  │
│       │                 │                     │             │
│       └─────────────────┼─────────────────────┘             │
│                         │ REST API / WebSocket              │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                     API 网关层                               │
│                   FastAPI + Nginx                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               /api/v1/animate                         │  │
│  │        POST { source, content_type, style }           │  │
│  └──────────────────────┬───────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                   任务调度层                                 │
│                  Celery + Redis                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Task Queue → Worker → Pipeline → Result Storage     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

                    AI 视频生成流水线

┌─────────────────────────────────────────────────────────────┐
│  ① ContentExtractor (内容提取)                               │
│     ├─ VideoDownloader: yt-dlp 下载视频                      │
│     ├─ AudioTranscriber: Whisper 语音转文字                   │
│     ├─ ImageOCR: 图片文字识别                                 │
│     ├─ WebScraper: 网页内容抓取                               │
│     └─ ContentAnalyzer: LLM 内容分析（主题、情绪、关键点）     │
├─────────────────────────────────────────────────────────────┤
│  ② ScriptAdapter (脚本改编)                                  │
│     ├─ ToneAnalyzer: 情绪分析                                 │
│     ├─ CharacterMapper: 内容→角色映射                         │
│     ├─ ScriptWriter: LLM 改写脚本                             │
│     └─ SubtitleGenerator: 字幕生成                            │
├─────────────────────────────────────────────────────────────┤
│  ③ CharacterGenerator (角色生成)                             │
│     ├─ CharacterDesigner: LLM 设计角色外观                    │
│     ├─ ImageGenerator: ComfyUI/SD 生成角色图                  │
│     ├─ ExpressionMapper: 表情映射                             │
│     └─ AnimationEngine: 口型/表情动画                         │
├─────────────────────────────────────────────────────────────┤
│  ④ VoiceSynthesizer (语音合成)                               │
│     ├─ EmotionDetector: 情绪检测                              │
│     ├─ VoiceSelector: 音色选择                                │
│     ├─ TTS Engine: 文字转语音                                 │
│     └─ AudioPostProcess: 音频后处理                           │
├─────────────────────────────────────────────────────────────┤
│  ⑤ VideoComposer (视频合成)                                  │
│     ├─ ScenePlanner: 场景编排                                 │
│     ├─ LipSync: 口型同步                                      │
│     ├─ BackgroundGen: 背景生成                                │
│     ├─ SubtitleOverlay: 字幕叠加                              │
│     └─ FFmpegEncoder: 视频编码输出                            │
└─────────────────────────────────────────────────────────────┘
```

## 2. 数据流

### 输入类型处理策略

| 输入类型 | 提取方式 | 示例 |
|---------|---------|------|
| 抖音/B站链接 | yt-dlp 下载 → Whisper 转写 | 两人对话视频 |
| 文字描述 | 直接使用 | "两只猫讨论天气" |
| 图片 | OCR + 视觉理解 | 表情包、梗图 |
| 新闻链接 | 网页抓取 + 摘要 | 热点新闻 |
| 微博/小红书 | API/爬虫 | 热帖 |

### 角色库

```
角色预设:
  🐱 狸花猫    — 活泼、灵巧    (适合搞笑对话)
  🐻 棕熊      — 稳重、憨厚    (适合严肃新闻)
  🦊 小狐狸    — 机灵、俏皮    (适合八卦/娱乐)
  🐼 熊猫      — 呆萌、可爱    (适合萌系内容)
  🐰 兔子      — 温柔、敏捷    (适合温馨内容)
  🐶 柴犬      — 忠诚、阳光    (适合正能量)
  🦉 猫头鹰    — 智慧、专业    (适合知识科普)
  🐧 企鹅      — 憨态可掬      (适合搞笑失败集锦)
```

## 3. API 设计

### POST /api/v1/animate

```json
{
  "source": "https://v.douyin.com/xxxxx",
  "source_type": "douyin_video",
  "character": "tabby_cat",
  "character_count": 2,
  "style": "funny",
  "background": "auto",
  "resolution": "1080p",
  "subtitle": true,
  "webhook_url": null
}
```

响应：
```json
{
  "task_id": "anim_20240504_001",
  "status": "queued",
  "estimated_time": 120,
  "poll_url": "/api/v1/tasks/anim_20240504_001"
}
```

### GET /api/v1/tasks/{task_id}

```json
{
  "task_id": "anim_20240504_001",
  "status": "completed",
  "progress": 100,
  "result": {
    "video_url": "https://cdn.example.com/output/anim_001.mp4",
    "duration": 45.2,
    "thumbnail_url": "https://cdn.example.com/thumb/anim_001.jpg"
  }
}
```

## 4. 技术选型

| 组件 | 技术 | 理由 |
|------|------|------|
| API 框架 | FastAPI | 高性能、异步、自动文档 |
| 异步任务 | Celery + Redis | 成熟的分布式任务队列 |
| 视频下载 | yt-dlp | 支持 1000+ 网站 |
| 语音识别 | Whisper (faster-whisper) | 高精度、多语言 |
| 内容理解 | DeepSeek / GPT-4 | 强大的语义理解 |
| 图片生成 | ComfyUI + SDXL | 灵活的 workflow |
| TTS | Edge-TTS / ElevenLabs | 免费/高质量 |
| 视频合成 | FFmpeg + MoviePy | 工业标准 |
| 口型同步 | Wav2Lip / SadTalker | 开源方案 |
| 存储 | MinIO / S3 | 对象存储 |
| Web 前端 | Next.js 14 + Tailwind | 现代化框架 |
| iOS | SwiftUI + AVFoundation | 原生体验 |
| Windows | Electron + React | 跨平台桌面 |
