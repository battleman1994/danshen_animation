# 🎬 Danshen Animation（蛋生动画）

> 跨平台动漫风格视频生成工具 — 输入图片/文字/链接/热点视频，一键生成动漫版视频

支持 **iOS** · **浏览器** · **Windows** 三大平台

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🖼️ 图片转动漫 | 上传任意图片，AI 转换为动漫风格并生成短视频 |
| 📝 文字转动漫 | 输入文字描述，AI 根据语义生成匹配的动漫画面 |
| 🔗 链接转动漫 | 粘贴网页/文章链接，自动提取内容生成动漫视频 |
| 🔥 热点视频转动漫 | 输入热点视频 URL，转换为动漫风格二次创作 |

---

## 🎭 应用场景

### 场景一：抖音对话 → 狸花猫剧场

> 将抖音上两人对话视频，转换生成 **两只狸花猫对话** 的动漫版视频

原始视频中的人物自动识别，替换为可爱狸花猫形象，口型、表情、动作均由 AI 驱动匹配。

### 场景二：热点新闻 → 动物播报

> 将热点新闻自动转为 **动物主播播报**，根据新闻严肃程度智能匹配播报风格

| 新闻类型 | 匹配动物 | 播报风格 |
|---------|---------|---------|
| 🟢 娱乐八卦 | 柴犬 🐕 | 轻松调侃 |
| 🟡 社会民生 | 猫头鹰 🦉 | 温和稳重 |
| 🟠 财经科技 | 企鹅 🐧 | 严谨专业 |
| 🔴 重大事件 | 雄狮 🦁 | 庄重严肃 |

---

## 🏗️ 技术栈

- **前端**: Flutter（iOS）/ React（Web）/ Electron（Windows）
- **AI 引擎**: Stable Diffusion + ControlNet / AnimateDiff
- **语音合成**: VITS / RVC 声音克隆
- **口型同步**: Wav2Lip / SadTalker
- **视频处理**: FFmpeg

---

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/battleman1994/danshen_animation.git
cd danshen_animation

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python app.py
```

---

## 📱 平台支持

| 平台 | 状态 | 入口 |
|------|------|------|
| iOS | 🚧 开发中 | Flutter App |
| 浏览器 | 🚧 开发中 | Web App |
| Windows | 🚧 开发中 | Electron 桌面应用 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！请先查看 [贡献指南](CONTRIBUTING.md)。

---

## 📄 许可证

MIT License

---

<p align="center">Made with ❤️ by battleman1994</p>
