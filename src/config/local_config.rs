use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::fs;
use std::sync::Mutex;

static CONFIG: Mutex<Option<LocalConfig>> = Mutex::new(None);

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LocalLLMConfig {
    pub id: String,
    pub name: String,
    pub provider: String,           // "openai" | "anthropic" | "deepseek"
    pub api_key: String,
    pub base_url: String,
    pub model_id: String,           // 实际 API model 参数
    pub supported_input_types: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LocalVideoConfig {
    pub id: String,
    pub name: String,
    pub provider: String,           // "kling" | "runway" | "jimeng" | "hailuo" | "openai" | ...
    pub api_key: String,
    pub base_url: String,
    pub supported_input_types: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LocalConfig {
    pub llm_models: Vec<LocalLLMConfig>,
    pub video_providers: Vec<LocalVideoConfig>,
    pub default_llm: String,
    pub default_video: String,
}

impl Default for LocalConfig {
    fn default() -> Self {
        Self {
            llm_models: vec![],
            video_providers: vec![],
            default_llm: String::new(),
            default_video: String::new(),
        }
    }
}

fn config_path() -> PathBuf {
    let base = dirs_next().unwrap_or_else(|| PathBuf::from("."));
    let dir = base.join(".danshen");
    fs::create_dir_all(&dir).ok();
    dir.join("config.json")
}

fn dirs_next() -> Option<PathBuf> {
    #[cfg(target_os = "macos")]
    { dirs_fallback_home() }
    #[cfg(not(target_os = "macos"))]
    { dirs_fallback_home() }
}

fn dirs_fallback_home() -> Option<PathBuf> {
    std::env::var("HOME").ok().map(PathBuf::from)
}

pub fn load_config() -> LocalConfig {
    let mut guard = CONFIG.lock().unwrap();
    if let Some(ref cfg) = *guard {
        return cfg.clone();
    }
    let path = config_path();
    let cfg = if path.exists() {
        fs::read_to_string(&path)
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default()
    } else {
        LocalConfig::default()
    };
    *guard = Some(cfg.clone());
    cfg
}

pub fn save_config(cfg: &LocalConfig) {
    let path = config_path();
    if let Ok(json) = serde_json::to_string_pretty(cfg) {
        fs::write(&path, json).ok();
    }
    let mut guard = CONFIG.lock().unwrap();
    *guard = Some(cfg.clone());
}

pub fn reload_config() -> LocalConfig {
    let mut guard = CONFIG.lock().unwrap();
    *guard = None;
    drop(guard);
    load_config()
}
