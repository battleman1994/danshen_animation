use crate::components::types::{Character, SceneMode, SourceType, Style};

pub fn get_characters() -> Vec<Character> { vec![
    Character { id: "tabby_cat", name: "狸花猫", emoji: "🐱", style: "活泼灵巧" },
    Character { id: "brown_bear", name: "棕熊", emoji: "🐻", style: "稳重憨厚" },
    Character { id: "little_fox", name: "小狐狸", emoji: "🦊", style: "机灵俏皮" },
    Character { id: "panda", name: "熊猫", emoji: "🐼", style: "呆萌可爱" },
    Character { id: "rabbit", name: "兔子", emoji: "🐰", style: "温柔敏捷" },
    Character { id: "shiba_inu", name: "柴犬", emoji: "🐶", style: "忠诚阳光" },
    Character { id: "owl", name: "猫头鹰", emoji: "🦉", style: "智慧专业" },
    Character { id: "penguin", name: "企鹅", emoji: "🐧", style: "憨态可掬" },
    Character { id: "lion", name: "雄狮", emoji: "🦁", style: "庄重威严" },
] }
pub fn get_scene_modes() -> Vec<SceneMode> { vec![SceneMode::Auto, SceneMode::Dialogue, SceneMode::News] }
pub fn get_source_types() -> Vec<SourceType> { vec![SourceType::Text, SourceType::WebLink, SourceType::Image, SourceType::DouyinVideo] }
pub fn get_styles() -> Vec<Style> { vec![Style { id: "auto", label: "🤖 自动" }, Style { id: "funny", label: "😂 搞笑" }, Style { id: "serious", label: "🎯 严肃" }, Style { id: "cute", label: "💕 可爱" }] }
pub fn get_status_label(status: &str) -> &'static str { match status { "queued" => "⏳ 排队中...", "extracting" => "📥 正在提取内容...", "adapting" => "✍️ 正在改编脚本...", "generating_characters" => "🎨 正在生成角色...", "synthesizing_voice" => "🔊 正在合成语音...", "composing_video" => "🎬 正在合成视频...", "completed" => "✨ 生成完成！", "failed" => "❌ 生成失败", _ => "⏳ 处理中..." } }

pub fn get_placeholder(source_type: SourceType, scene_mode: SceneMode) -> &'static str { match (scene_mode, source_type) {
    (SceneMode::News, SourceType::WebLink) => "粘贴新闻链接...例如：https://news.example.com/...",
    (SceneMode::News, SourceType::Text) => "输入或粘贴新闻内容...例如：今日股市大涨3%...",
    (SceneMode::News, _) => "粘贴新闻相关内容...",
    (SceneMode::Dialogue, SourceType::DouyinVideo) => "粘贴抖音对话视频链接...",
    (SceneMode::Dialogue, SourceType::Text) => "输入对话内容...例如：甲：今天天气真好！乙：是啊！",
    (SceneMode::Dialogue, _) => "粘贴对话相关内容...",
    (_, SourceType::Text) => "输入你想改编的内容...支持文字、链接、视频URL",
    (_, SourceType::WebLink) => "粘贴网页链接...",
    (_, SourceType::DouyinVideo) => "粘贴抖音视频链接...",
    (_, _) => "上传或粘贴内容...",
} }
