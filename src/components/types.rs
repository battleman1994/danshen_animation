use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SceneMode { #[serde(rename = "auto")] Auto, #[serde(rename = "dialogue")] Dialogue, #[serde(rename = "news")] News }
impl SceneMode {
    pub fn as_str(&self) -> &'static str { match self { Self::Auto => "auto", Self::Dialogue => "dialogue", Self::News => "news" } }
    pub fn name(&self) -> &'static str { match self { Self::Auto => "智能识别", Self::Dialogue => "对话剧场", Self::News => "新闻播报" } }
    pub fn desc(&self) -> &'static str { match self { Self::Auto => "AI 自动选择最佳模式", Self::Dialogue => "抖音对话 → 动物演绎", Self::News => "热点新闻 → 动物主播" } }
    pub fn icon(&self) -> &'static str { match self { Self::Auto => "⚡", Self::Dialogue => "💬", Self::News => "📰" } }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SourceType { #[serde(rename = "text")] Text, #[serde(rename = "web_link")] WebLink, #[serde(rename = "image")] Image, #[serde(rename = "douyin_video")] DouyinVideo }
impl SourceType {
    pub fn as_str(&self) -> &'static str { match self { Self::Text => "text", Self::WebLink => "web_link", Self::Image => "image", Self::DouyinVideo => "douyin_video" } }
    pub fn label(&self) -> &'static str { match self { Self::Text => "文字", Self::WebLink => "链接", Self::Image => "图片", Self::DouyinVideo => "抖音" } }
    pub fn icon(&self) -> &'static str { match self { Self::Text => "Aa", Self::WebLink => "🔗", Self::Image => "📷", Self::DouyinVideo => "▶" } }
}

#[derive(Debug, Clone, PartialEq)]
pub struct Character { pub id: &'static str, pub name: &'static str, pub emoji: &'static str, pub style: &'static str }
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Style { pub id: &'static str, pub label: &'static str }
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnimateRequest { pub source: String, pub source_type: String, pub character: String, pub character_count: u32, pub style: String, pub scene_mode: String }
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskResponse { pub task_id: Option<String>, pub error: Option<String> }
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskStatus { pub status: String, pub progress: Option<f64>, pub error: Option<String>, pub result: Option<TaskResult> }
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskResult { pub video_url: Option<String> }

// ── User / Auth Types ──

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct UserInfo {
    pub user_id: String,
    pub nickname: String,
    pub avatar_url: String,
    pub provider: String,
    pub phone: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthResponse {
    pub success: bool,
    pub token: String,
    pub user: Option<UserInfo>,
    pub message: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OAuthUrlResponse {
    pub url: String,
    pub provider: String,
    pub message: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SendSmsResponse {
    pub success: bool,
    pub message: String,
    pub debug_code: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimpleResponse {
    pub success: bool,
    pub message: String,
}
