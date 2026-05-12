use dioxus::prelude::*;
use crate::api::client;
use crate::config::local_config;
use crate::components::constants::get_status_label;
use crate::components::types::*;

#[derive(Clone, Copy)]
pub struct UseAnimation {
    pub scene_mode: Signal<SceneMode>,
    pub source: Signal<String>,
    pub source_type: Signal<SourceType>,
    pub character: Signal<String>,
    pub character_count: Signal<u32>,
    pub style: Signal<String>,
    pub provider: Signal<String>,
    pub providers: Signal<Vec<ProviderInfo>>,
    pub llm_model: Signal<String>,
    pub llm_models: Signal<Vec<LLMModelInfo>>,
    pub loading: Signal<bool>,
    pub progress: Signal<u32>,
    pub status_text: Signal<String>,
    pub result: Signal<Option<String>>,
    pub error: Signal<Option<String>>,
}

impl UseAnimation {
    pub fn scene_mode(&self) -> SceneMode { *self.scene_mode.read() }
    pub fn source(&self) -> String { self.source.read().clone() }
    pub fn source_type(&self) -> SourceType { *self.source_type.read() }
    pub fn character(&self) -> String { self.character.read().clone() }
    pub fn character_count(&self) -> u32 { *self.character_count.read() }
    pub fn style(&self) -> String { self.style.read().clone() }
    pub fn provider(&self) -> String { self.provider.read().clone() }
    pub fn providers(&self) -> Vec<ProviderInfo> { self.providers.read().clone() }
    pub fn llm_model(&self) -> String { self.llm_model.read().clone() }
    pub fn llm_models(&self) -> Vec<LLMModelInfo> { self.llm_models.read().clone() }
    pub fn loading(&self) -> bool { *self.loading.read() }
    pub fn progress(&self) -> u32 { *self.progress.read() }
    pub fn status_text(&self) -> String { self.status_text.read().clone() }
    pub fn result(&self) -> Option<String> { self.result.read().clone() }
    pub fn error(&self) -> Option<String> { self.error.read().clone() }
    pub fn can_submit(&self) -> bool {
        if self.source.read().trim().is_empty() || *self.loading.read() {
            return false;
        }
        let st = self.source_type.read().as_str().to_string();
        let model_id = self.llm_model.read().clone();
        for m in self.llm_models.read().iter() {
            if m.id == model_id {
                return m.available && m.supported_input_types.contains(&st);
            }
        }
        let prov_id = self.provider.read().clone();
        for p in self.providers.read().iter() {
            if p.id == prov_id {
                return p.available && p.supported_input_types.contains(&st);
            }
        }
        true
    }

    pub fn handle_reset(&mut self) {
        self.source.set(String::new()); self.result.set(None);
        self.progress.set(0); self.status_text.set(String::new());
        self.error.set(None); self.loading.set(false);
    }

    pub fn handle_submit(&mut self) {
        if self.source.read().trim().is_empty() { return; }
        self.loading.set(true); self.progress.set(0);
        self.status_text.set(get_status_label("queued").to_string());
        self.result.set(None); self.error.set(None);

        let req = AnimateRequest {
            source: self.source.read().clone(),
            source_type: self.source_type.read().as_str().to_string(),
            character: self.character.read().clone(),
            style: self.style.read().clone(),
            provider: self.provider.read().clone(),
            llm_model: self.llm_model.read().clone(),
            resolution: "1080p".to_string(),
            subtitle: true,
        };
        let mut loading = self.loading.clone();
        let mut progress = self.progress.clone();
        let mut status_text = self.status_text.clone();
        let mut result = self.result.clone();
        let mut error = self.error.clone();

        spawn(async move {
            match client::submit_animation(&req).await {
                Ok(resp) => {
                    if let Some(task_id) = resp.task_id {
                        loop {
                            #[cfg(not(target_family = "wasm"))]
                            tokio::time::sleep(std::time::Duration::from_secs(2)).await;

                            match client::poll_task(&task_id).await {
                                Ok(task_status) => {
                                    let pct = task_status.progress.unwrap_or(0.0).round() as u32;
                                    progress.set(pct);
                                    status_text.set(get_status_label(&task_status.status).to_string());
                                    match task_status.status.as_str() {
                                        "completed" => {
                                            progress.set(100);
                                            status_text.set("✨ 生成完成！".to_string());
                                            if let Some(url) = task_status.result.and_then(|r| r.video_url) {
                                                if !url.is_empty() { result.set(Some(url)); }
                                                else { error.set(Some("未返回视频链接".to_string())); }
                                            }
                                            loading.set(false); break;
                                        }
                                        "failed" => {
                                            let msg = task_status.error.unwrap_or("生成失败".to_string());
                                            error.set(Some(msg)); loading.set(false); break;
                                        }
                                        _ => {}
                                    }
                                }
                                Err(_) => {}
                            }
                        }
                    } else {
                        error.set(Some(resp.error.unwrap_or("任务创建失败".to_string())));
                        loading.set(false);
                    }
                }
                Err(e) => { error.set(Some(e)); loading.set(false); }
            }
        });
    }
}

/// 将本地 LLM 配置合并到内置模型列表
fn merge_llm_models(remote: Vec<LLMModelInfo>) -> Vec<LLMModelInfo> {
    let cfg = local_config::load_config();
    let mut models = remote;
    for lc in &cfg.llm_models {
        models.push(LLMModelInfo {
            id: lc.id.clone(),
            name: lc.name.clone(),
            provider: lc.provider.clone(),
            supported_input_types: lc.supported_input_types.clone(),
            available: !lc.api_key.is_empty(),
            mode: "local".into(),
            requires_config: vec![],
        });
    }
    models
}

/// 将本地视频配置合并到内置 provider 列表
fn merge_providers(remote: Vec<ProviderInfo>) -> Vec<ProviderInfo> {
    let cfg = local_config::load_config();
    let mut providers = remote;
    for lc in &cfg.video_providers {
        providers.push(ProviderInfo {
            id: lc.id.clone(),
            name: lc.name.clone(),
            description: format!("本地配置 — {}", lc.provider),
            available: !lc.api_key.is_empty(),
            supported_input_types: lc.supported_input_types.clone(),
            mode: "local".into(),
            requires_config: vec![],
        });
    }
    providers
}

pub fn use_animation() -> UseAnimation {
    let providers_signal = use_signal(|| Vec::<ProviderInfo>::new());
    let llm_models_signal = use_signal(|| Vec::<LLMModelInfo>::new());

    let mut p = providers_signal.clone();
    spawn(async move {
        if let Ok(resp) = client::fetch_providers().await {
            p.set(merge_providers(resp.providers));
        } else {
            // 离线：至少展示本地配置
            p.set(merge_providers(vec![]));
        }
    });
    let mut lm = llm_models_signal.clone();
    spawn(async move {
        if let Ok(resp) = client::fetch_llm_models().await {
            lm.set(merge_llm_models(resp.models));
        } else {
            lm.set(merge_llm_models(vec![]));
        }
    });

    // 从本地配置读取默认值
    let cfg = local_config::load_config();
    let default_llm = if cfg.default_llm.is_empty() {
        "deepseek-v4-pro[1m]".into()
    } else {
        cfg.default_llm.clone()
    };
    let default_provider = if cfg.default_video.is_empty() {
        "mock".into()
    } else {
        cfg.default_video.clone()
    };

    UseAnimation {
        scene_mode: use_signal(|| SceneMode::Auto),
        source: use_signal(String::new),
        source_type: use_signal(|| SourceType::Text),
        character: use_signal(|| String::from("orange_tabby")),
        character_count: use_signal(|| 2u32),
        style: use_signal(|| String::from("auto")),
        provider: use_signal(|| default_provider),
        providers: providers_signal,
        llm_model: use_signal(|| default_llm),
        llm_models: llm_models_signal,
        loading: use_signal(|| false),
        progress: use_signal(|| 0u32),
        status_text: use_signal(String::new),
        result: use_signal(|| None::<String>),
        error: use_signal(|| None::<String>),
    }
}
