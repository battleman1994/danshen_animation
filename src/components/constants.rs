use crate::components::types::{Character, SceneMode, SourceType, Style};

pub fn get_characters() -> Vec<Character> { vec![
    Character { id: "orange_tabby", name: "橘猫", emoji: "🐱", style: "活泼好动，表情丰富" },
    Character { id: "calico_cat", name: "三花猫", emoji: "😺", style: "优雅灵动，聪明机敏" },
    Character { id: "black_cat", name: "黑猫", emoji: "🐈‍⬛", style: "神秘呆萌，温柔粘人" },
    Character { id: "ragdoll_cat", name: "布偶猫", emoji: "😻", style: "温顺可爱，软萌优雅" },
    Character { id: "british_shorthair", name: "英短", emoji: "🐱", style: "憨态可掬，自带喜感" },
    Character { id: "orange_cat_fat", name: "胖橘", emoji: "🍊", style: "贪吃贪睡，佛系慵懒" },
    Character { id: "panda", name: "熊猫", emoji: "🐼", style: "呆萌可爱，国宝级萌物" },
] }
pub fn get_scene_modes() -> Vec<SceneMode> { vec![SceneMode::Auto, SceneMode::Dialogue, SceneMode::News] }
pub fn get_source_types() -> Vec<SourceType> { vec![SourceType::Text, SourceType::WebLink, SourceType::Image, SourceType::DouyinVideo] }
pub fn get_styles() -> Vec<Style> { vec![Style { id: "auto", label: "🤖 自动" }, Style { id: "funny", label: "😂 搞笑" }, Style { id: "serious", label: "🎯 严肃" }, Style { id: "cute", label: "💕 可爱" }] }
pub fn get_status_label(status: &str) -> &'static str { match status { "queued" => "⏳ 排队中...", "generating_prompt" => "🧠 正在分析内容，生成提示词...", "generating_video" => "🎬 正在调用 AI 生成视频...", "completed" => "✨ 生成完成！", "failed" => "❌ 生成失败", _ => "⏳ 处理中..." } }

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
