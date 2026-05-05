# 🦀 Rust 跨平台桌面端 — macOS + Windows 技术方案

## 目标

将 `danshen_animation` Web 前端重构为 **Rust 原生桌面应用**，一份代码同时编译为 **macOS (.app)** 和 **Windows (.exe)** 两个平台的原生应用。

---

## 方案对比

### 方案 A：Tauri v2 🏆（强烈推荐）

| 项目 | 说明 |
|:----|:-----|
| **UI 层** | 复用现有 Next.js + React + Tailwind CSS 代码（通过 WebView 渲染） |
| **Rust 层** | Tauri 核心（系统 API、文件处理、窗口管理、进程通信） |
| **原生能力** | macOS WKWebView / Windows WebView2 — 系统级 WebView，不打包浏览器 |
| **包体积** | ~5-10MB（不含 UI 资源） |
| **成熟度** | ⭐⭐⭐⭐⭐ 最成熟，社区最大，文档最全 |
| **开发速度** | ⭐⭐⭐⭐⭐ 现有 UI 可直接复用，只需写 Tauri 胶水代码 |

**适合**：快速出成果，复用现有设计，调后端 API 即可

### 方案 B：Dioxus

| 项目 | 说明 |
|:----|:-----|
| **UI 层** | 纯 Rust 声明式 UI（RSX 宏），类似 React |
| **Rust 层** | 全部 Rust，无 JS/HTML 依赖 |
| **原生能力** | macOS WebView / Windows WebView2（桌面模式） |
| **体验** | 需要全部重写 UI 组件，无法复用现有代码 |
| **成熟度** | ⭐⭐⭐ 半成熟，API 仍在快速迭代 |

**适合**：想全栈 Rust，不介意重写 UI

### 方案 C：Slint

| 项目 | 说明 |
|:----|:-----|
| **UI 层** | 专用 .slint 声明式语言 |
| **Rust 层** | Rust 业务逻辑绑定 |
| **原生能力** | 原生渲染（非 WebView），CPU/GPU 渲染 |
| **包体积** | ~2-3MB 极小 |
| **成熟度** | ⭐⭐⭐ 发展期，UI 组件库仍在完善 |

**适合**：嵌入式/轻量级应用，需要极致性能

---

## 🏆 推荐方案：Tauri v2

### 为什么选 Tauri？

1. **零成本复用 UI** — 刚完成的 Web UI 重设计（React + Tailwind + framer-motion）直接搬过来，不用重写
2. **原生能力** — Rust 后端直接调用系统 API（文件对话框、通知、菜单栏、快捷键）
3. **包体积小** — 不像 Electron 打包 Chromium，Tauri 用系统 WebView
4. **安全性** — 严格的权限模型，Rust 后端隔离
5. **macOS + Windows 支持完善** — 原生窗口、菜单、托盘、安装包
6. **Rust 最新版** — Tauri v2 兼容 Rust 1.77+（稳定版完全没问题）

### 架构设计

```
┌──────────────────────────────────────────────────┐
│                  Tauri App                        │
│  ┌────────────────────────────────────────────┐  │
│  │           WebView (前端 UI)                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ React UI │ │ Tailwind │ │ framer-  │   │  │
│  │  │ 组件     │ │ 样式     │ │ motion   │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘   │  │
│  └──────────────────┬─────────────────────────┘  │
│                     │ IPC (invoke/event)           │
│  ┌──────────────────▼─────────────────────────┐  │
│  │          Rust 后端 (Tauri Core)              │  │
│  │                                             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ Commands │ │ System   │ │ 视频处理  │   │  │
│  │  │ (API)    │ │ (fs/通知)│ │ (ffmpeg)  │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘   │  │
│  └─────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
         │                    │
         │ HTTP API           │ HTTP API
         ▼                    ▼
    ┌──────────────────────────────┐
    │    Python 后端服务            │
    │   (FastAPI + Celery + AI)   │
    └──────────────────────────────┘
```

### 目录结构设计

```
danshen_animation/
├── src-tauri/                  # ← 新增：Rust 项目根目录
│   ├── Cargo.toml              # Rust 依赖
│   ├── tauri.conf.json         # Tauri 配置（窗口、权限、打包）
│   ├── capabilities/           # 权限声明
│   ├── src/
│   │   ├── main.rs             # 入口
│   │   ├── lib.rs              # Tauri 插件注册
│   │   ├── commands.rs         # 自定义 IPC 命令
│   │   ├── system.rs           # 系统集成（通知、菜单、文件）
│   │   └── media.rs            # 视频/音频处理 (ffmpeg 绑定)
│   ├── icons/
│   │   ├── icon.icns           # macOS 图标
│   │   └── icon.ico            # Windows 图标
│   └── Info.plist              # macOS 应用信息
│
├── web/                        # ← 现有 UI（直接复用，无需大改）
│   ├── src/app/                # React 组件
│   ├── package.json
│   └── ...
│
└── backend/                    # 现有 Python 后端
```

### Cargo.toml 关键依赖

```toml
[dependencies]
tauri = { version = "2", features = ["tray-icon", "dialog"] }
tauri-plugin-shell = "2"       # 调用 ffmpeg 等外部命令
tauri-plugin-dialog = "2"      # 原生文件选择对话框
tauri-plugin-fs = "2"          # 文件读写
tauri-plugin-notification = "2" # 系统通知
serde = { version = "1", features = ["derive"] }
serde_json = "1"
reqwest = { version = "0.12", features = ["json"] }     # 调用 Python 后端 API
tokio = { version = "1", features = ["full"] }

[build-dependencies]
tauri-build = { version = "2", features = [] }
```

### 实施步骤

#### 第一阶段：项目骨架（1-2天）

| 步骤 | 内容 |
|:----|:-----|
| 1️⃣ | `cargo init src-tauri` — 初始化 Rust 项目 |
| 2️⃣ | 配置 `tauri.conf.json` — 窗口标题、尺寸、图标 |
| 3️⃣ | 配置权限 (`capabilities/`) — 允许网络请求、文件访问 |
| 4️⃣ | 将 `web/` 构建输出设为 Tauri 的前端资源 |
| 5️⃣ | 验证：`cargo tauri dev` 启动窗口，显示现有 UI |

#### 第二阶段：Rust 后端服务（2-3天）

| 步骤 | 内容 |
|:----|:-----|
| 6️⃣ | `commands.rs` — 实现 Tauri IPC 命令列表 |
| 7️⃣ | 前端 API 转发 — React 通过 `@tauri-apps/api` 调用 Rust 命令 |
| 8️⃣ | `media.rs` — ffmpeg 视频/音频处理（通过 `tauri-plugin-shell`） |
| 9️⃣ | `system.rs` — 系统菜单、托盘图标、通知 |
| 🔟 | API 客户端 — Rust 调用 Python 后端 `POST /api/v1/animate` |

#### 第三阶段：平台适配与打包（1-2天）

| 步骤 | 内容 |
|:----|:-----|
| 11️⃣ | **macOS** — 打包 `.app` + `.dmg`，签名（可选） |
| 12️⃣ | **Windows** — 打包 `.msi` / `.exe` 安装包 |
| 13️⃣ | 自动更新 (`tauri-plugin-updater`) |
| 14️⃣ | 测试跨平台功能一致性 |

### 需要修改的前端文件

| 文件 | 改动 |
|:----|:-----|
| `web/src/hooks/useAnimation.ts` | 替换 axios 调用为 `@tauri-apps/api/core` 的 invoke |
| `web/package.json` | 添加 `@tauri-apps/api` 依赖 |
| `web/src/app/layout.tsx` | 添加 Tauri 事件监听 |
| `web/next.config.js` | 配置输出为静态导出（Tauri 需要） |

### 验证方式

```bash
# 开发模式
cd danshen_animation
cargo tauri dev          # 启动带热重载的桌面窗口

# 构建 macOS 版本
cargo tauri build --target aarch64-apple-darwin

# 构建 Windows 版本（跨编译或在 Windows 上）
cargo tauri build --target x86_64-pc-windows-msvc
```

---

## 风险与注意事项

| 风险 | 缓解措施 |
|:----|:---------|
| WebView 兼容性 | macOS WKWebView / Windows WebView2 均支持现代 CSS/JS |
| Python 后端依赖 | Rust 端仅通过 HTTP 调用，后端无需改动 |
| ffmpeg 依赖 | 通过 `tauri-plugin-shell` 调用系统 ffmpeg 或捆绑 |
| 图标/资源 | 需准备 macOS (.icns) 和 Windows (.ico) 两种格式 |
| Windows 签名 | 发布前需要代码签名证书（可选但推荐） |

---

## 结论

**推荐走 Tauri v2 方案**，原因：
1. ✅ 现有 React + Tailwind UI 零成本复用（UI 刚重设计完）
2. ✅ Rust 最新稳定版（1.77+）完全兼容
3. ✅ macOS + Windows 双平台打包成熟
4. ✅ 包体积极小（~5MB），远优于 Electron
5. ✅ 安全模型清晰，Rust 后端隔离

若要纯 Rust UI，可选 **Dioxus**，但需要全部重写 UI 组件，周期较长。
