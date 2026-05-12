use dioxus::prelude::*;
use crate::config::local_config::{self, LocalLLMConfig, LocalVideoConfig};
use crate::styles::theme::use_theme;

#[derive(Clone, Copy, PartialEq)]
enum CfgTab { LLM, Video }

#[component]
pub fn ConfigModal(
    show: Signal<bool>,
    llm_models: Signal<Vec<crate::components::types::LLMModelInfo>>,
    providers: Signal<Vec<crate::components::types::ProviderInfo>>,
    default_llm: Signal<String>,
    default_video: Signal<String>,
) -> Element {
    let c = use_theme().colors();
    if !show() { return rsx! {}; }

    let mut tab = use_signal(|| CfgTab::LLM);
    let mut e_name = use_signal(String::new);
    let mut e_provider = use_signal(|| "openai".to_string());
    let mut e_key = use_signal(String::new);
    let mut e_url = use_signal(String::new);
    let mut e_model = use_signal(String::new);
    let mut e_id = use_signal(String::new);
    let mut show_form = use_signal(|| false);
    let mut test_msg = use_signal(String::new);

    let cfg = local_config::load_config();

    let ov = "position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:1000;display:flex;align-items:center;justify-content:center;";

    let is_llm = tab() == CfgTab::LLM;
    let is_vid = tab() == CfgTab::Video;
    let accent = c.accent.to_string();
    let text_muted = c.text_muted.to_string();
    let llm_color = if is_llm { accent.clone() } else { text_muted.clone() };
    let llm_border = if is_llm { accent.clone() } else { String::from("transparent") };
    let vid_color = if is_vid { accent.clone() } else { text_muted.clone() };
    let vid_border = if is_vid { accent.clone() } else { String::from("transparent") };
    let test_color = if test_msg().contains("✓") { "#22c55e".to_string() } else { "#ef4444".to_string() };

    rsx! {
        div {
            style: "{ov}",
            onclick: move |_| show.set(false),
            div {
                style: "background:{c.bg_card};border-radius:{c.radius_lg};width:560px;max-height:80vh;overflow-y:auto;padding:24px;border:1px solid {c.border};",
                onclick: move |e| e.stop_propagation(),
                // Header
                div { style: "display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;",
                    h3 { style: "color:{c.text_primary};font-size:18px;font-weight:600;margin:0;", "⚙️ 自定义模型配置" }
                    button {
                        style: "background:none;border:none;color:{c.text_muted};font-size:20px;cursor:pointer;",
                        onclick: move |_| show.set(false),
                        "×"
                    }
                }
                // Tabs
                div { style: "display:flex;gap:0;margin-bottom:20px;border-bottom:2px solid {c.border};",
                    button {
                        style: "flex:1;padding:10px;border:none;background:none;cursor:pointer;font-size:14px;font-weight:500;color:{llm_color};border-bottom:2px solid {llm_border};",
                        onclick: move |_| tab.set(CfgTab::LLM),
                        "🧠 LLM 模型"
                    }
                    button {
                        style: "flex:1;padding:10px;border:none;background:none;cursor:pointer;font-size:14px;font-weight:500;color:{vid_color};border-bottom:2px solid {vid_border};",
                        onclick: move |_| tab.set(CfgTab::Video),
                        "🎬 视频生成"
                    }
                }

                // LLM Tab Content
                if tab() == CfgTab::LLM {
                    div {
                        if cfg.llm_models.is_empty() {
                            p { style: "color:{c.text_muted};font-size:13px;", "暂无自定义 LLM 模型" }
                        }
                        for m in cfg.llm_models.iter() {
                            div { style: "display:flex;align-items:center;justify-content:space-between;padding:10px;margin-bottom:8px;border-radius:{c.radius_md};background:{c.bg_page};border:1px solid {c.border};",
                                div {
                                    div { style: "color:{c.text_primary};font-size:14px;font-weight:500;", "{m.name}" }
                                    div { style: "color:{c.text_muted};font-size:11px;", "{m.provider} | {m.model_id}" }
                                }
                                div { style: "display:flex;gap:6px;",
                                    button {
                                        style: "padding:4px 10px;font-size:12px;border:1px solid {c.border};border-radius:{c.radius_sm};background:{c.bg_card};color:{c.text_primary};cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: {
                                            let m = m.clone();
                                            move |_| { e_id.set(m.id.clone()); e_name.set(m.name.clone()); e_provider.set(m.provider.clone()); e_key.set(m.api_key.clone()); e_url.set(m.base_url.clone()); e_model.set(m.model_id.clone()); show_form.set(true); }
                                        },
                                        "编辑"
                                    }
                                    button {
                                        style: "padding:4px 10px;font-size:12px;border:1px solid {c.border};border-radius:{c.radius_sm};background:{c.bg_card};color:#ef4444;cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: {
                                            let id = m.id.clone();
                                            move |_| { let mut nc = local_config::load_config(); nc.llm_models.retain(|x| x.id != id); local_config::save_config(&nc); local_config::reload_config(); }
                                        },
                                        "删除"
                                    }
                                }
                            }
                        }
                        // Form
                        if show_form() {
                            div { style: "padding:16px;border-radius:{c.radius_md};background:{c.bg_page};border:2px solid {c.accent};margin-bottom:8px;",
                                h4 { style: "color:{c.text_primary};margin:0 0 12px 0;font-size:14px;", "编辑 LLM 模型" }
                                input { style: "width:100%;padding:8px;border-radius:{c.radius_sm};border:1px solid {c.border};background:{c.bg_page};color:{c.text_primary};font-size:13px;margin-bottom:8px;", placeholder: "名称", value: "{e_name}", oninput: move |ev| e_name.set(ev.value()) }
                                select { style: "width:100%;padding:8px;border-radius:{c.radius_sm};border:1px solid {c.border};background:{c.bg_page};color:{c.text_primary};font-size:13px;margin-bottom:8px;", value: "{e_provider}", onchange: move |ev| e_provider.set(ev.value()),
                                    option { value: "openai", "OpenAI" }
                                    option { value: "anthropic", "Anthropic" }
                                    option { value: "deepseek", "DeepSeek" }
                                }
                                input { style: "width:100%;padding:8px;border-radius:{c.radius_sm};border:1px solid {c.border};background:{c.bg_page};color:{c.text_primary};font-size:13px;margin-bottom:8px;", placeholder: "API Key", value: "{e_key}", oninput: move |ev| e_key.set(ev.value()) }
                                input { style: "width:100%;padding:8px;border-radius:{c.radius_sm};border:1px solid {c.border};background:{c.bg_page};color:{c.text_primary};font-size:13px;margin-bottom:8px;", placeholder: "Base URL", value: "{e_url}", oninput: move |ev| e_url.set(ev.value()) }
                                input { style: "width:100%;padding:8px;border-radius:{c.radius_sm};border:1px solid {c.border};background:{c.bg_page};color:{c.text_primary};font-size:13px;margin-bottom:8px;", placeholder: "Model ID (如 gpt-4o)", value: "{e_model}", oninput: move |ev| e_model.set(ev.value()) }
                                div { style: "display:flex;gap:8px;margin-top:8px;",
                                    button {
                                        style: "padding:8px 16px;border-radius:{c.radius_sm};background:{c.accent};color:#fff;border:none;font-size:13px;cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: move |_| {
                                            let id = if e_id().is_empty() { format!("local-{:x}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_nanos()) } else { e_id() };
                                            let mut nc = local_config::load_config();
                                            nc.llm_models.retain(|x| x.id != id);
                                            nc.llm_models.push(LocalLLMConfig { id, name: e_name(), provider: e_provider(), api_key: e_key(), base_url: e_url(), model_id: e_model(), supported_input_types: vec!["text".into(), "web_link".into()] });
                                            local_config::save_config(&nc);
                                            local_config::reload_config();
                                            show_form.set(false);
                                        },
                                        "💾 保存"
                                    }
                                    button {
                                        style: "padding:8px 16px;border-radius:{c.radius_sm};background:{c.bg_card};color:{c.text_primary};border:1px solid {c.border};font-size:13px;cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: move |_| {
                                            let key = e_key(); let url = e_url();
                                            spawn(async move {
                                                let ok = test_conn(&url, &key).await;
                                                if ok { test_msg.set("✓ 连接成功".into()); } else { test_msg.set("✗ 连接失败".into()); }
                                            });
                                        },
                                        "🔌 测试连接"
                                    }
                                    button {
                                        style: "padding:8px 16px;border-radius:{c.radius_sm};background:none;color:{c.text_muted};border:none;font-size:13px;cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: move |_| show_form.set(false),
                                        "取消"
                                    }
                                }
                                if !test_msg.read().is_empty() {
                                    div { style: "margin-top:8px;font-size:12px;color:{test_color};", "{test_msg}" }
                                }
                            }
                        }
                        button {
                            style: "width:100%;padding:10px;margin-top:8px;border:1px dashed {c.border};border-radius:{c.radius_md};background:none;color:{c.accent};font-size:14px;cursor:pointer;",
                            onclick: move |_| { e_id.set(String::new()); e_name.set(String::new()); e_provider.set("openai".into()); e_key.set(String::new()); e_url.set("https://api.openai.com/v1".into()); e_model.set("gpt-4o".into()); show_form.set(true); },
                            "+ 添加 LLM 模型"
                        }
                    }
                }

                // Video Tab Content (simplified — reuses same signals)
                if tab() == CfgTab::Video {
                    div {
                        if cfg.video_providers.is_empty() {
                            p { style: "color:{c.text_muted};font-size:13px;", "暂无自定义视频生成服务" }
                        }
                        for m in cfg.video_providers.iter() {
                            div { style: "display:flex;align-items:center;justify-content:space-between;padding:10px;margin-bottom:8px;border-radius:{c.radius_md};background:{c.bg_page};border:1px solid {c.border};",
                                div {
                                    div { style: "color:{c.text_primary};font-size:14px;font-weight:500;", "{m.name}" }
                                    div { style: "color:{c.text_muted};font-size:11px;", "{m.provider} | {m.base_url}" }
                                }
                                div { style: "display:flex;gap:6px;",
                                    button {
                                        style: "padding:4px 10px;font-size:12px;border:1px solid {c.border};border-radius:{c.radius_sm};background:{c.bg_card};color:{c.text_primary};cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: {
                                            let m = m.clone();
                                            move |_| { e_id.set(m.id.clone()); e_name.set(m.name.clone()); e_provider.set(m.provider.clone()); e_key.set(m.api_key.clone()); e_url.set(m.base_url.clone()); show_form.set(true); }
                                        },
                                        "编辑"
                                    }
                                    button {
                                        style: "padding:4px 10px;font-size:12px;border:1px solid {c.border};border-radius:{c.radius_sm};background:{c.bg_card};color:#ef4444;cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: {
                                            let id = m.id.clone();
                                            move |_| { let mut nc = local_config::load_config(); nc.video_providers.retain(|x| x.id != id); local_config::save_config(&nc); local_config::reload_config(); }
                                        },
                                        "删除"
                                    }
                                }
                            }
                        }
                        if show_form() {
                            div { style: "padding:16px;border-radius:{c.radius_md};background:{c.bg_page};border:2px solid {c.accent};margin-bottom:8px;",
                                h4 { style: "color:{c.text_primary};margin:0 0 12px 0;font-size:14px;", "编辑视频服务" }
                                input { style: "width:100%;padding:8px;border-radius:{c.radius_sm};border:1px solid {c.border};background:{c.bg_page};color:{c.text_primary};font-size:13px;margin-bottom:8px;", placeholder: "名称", value: "{e_name}", oninput: move |ev| e_name.set(ev.value()) }
                                select { style: "width:100%;padding:8px;border-radius:{c.radius_sm};border:1px solid {c.border};background:{c.bg_page};color:{c.text_primary};font-size:13px;margin-bottom:8px;", value: "{e_provider}", onchange: move |ev| e_provider.set(ev.value()),
                                    option { value: "openai", "OpenAI (Sora)" }
                                    option { value: "kling", "可灵 Kling" }
                                    option { value: "runway", "Runway" }
                                    option { value: "jimeng", "即梦 Jimeng" }
                                    option { value: "hailuo", "海螺 Hailuo" }
                                }
                                input { style: "width:100%;padding:8px;border-radius:{c.radius_sm};border:1px solid {c.border};background:{c.bg_page};color:{c.text_primary};font-size:13px;margin-bottom:8px;", placeholder: "API Key", value: "{e_key}", oninput: move |ev| e_key.set(ev.value()) }
                                input { style: "width:100%;padding:8px;border-radius:{c.radius_sm};border:1px solid {c.border};background:{c.bg_page};color:{c.text_primary};font-size:13px;margin-bottom:8px;", placeholder: "Base URL", value: "{e_url}", oninput: move |ev| e_url.set(ev.value()) }
                                div { style: "display:flex;gap:8px;margin-top:8px;",
                                    button {
                                        style: "padding:8px 16px;border-radius:{c.radius_sm};background:{c.accent};color:#fff;border:none;font-size:13px;cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: move |_| {
                                            let id = if e_id().is_empty() { format!("local-{:x}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_nanos()) } else { e_id() };
                                            let mut nc = local_config::load_config();
                                            nc.video_providers.retain(|x| x.id != id);
                                            nc.video_providers.push(LocalVideoConfig { id, name: e_name(), provider: e_provider(), api_key: e_key(), base_url: e_url(), supported_input_types: vec!["text".into(), "web_link".into()] });
                                            local_config::save_config(&nc);
                                            local_config::reload_config();
                                            show_form.set(false);
                                        },
                                        "💾 保存"
                                    }
                                    button {
                                        style: "padding:8px 16px;border-radius:{c.radius_sm};background:{c.bg_card};color:{c.text_primary};border:1px solid {c.border};font-size:13px;cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: move |_| {
                                            let key = e_key(); let url = e_url();
                                            spawn(async move {
                                                let ok = test_conn(&url, &key).await;
                                                if ok { test_msg.set("✓ 连接成功".into()); } else { test_msg.set("✗ 连接失败".into()); }
                                            });
                                        },
                                        "🔌 测试连接"
                                    }
                                    button {
                                        style: "padding:8px 16px;border-radius:{c.radius_sm};background:none;color:{c.text_muted};border:none;font-size:13px;cursor:pointer;",
                                        prevent_default: "onclick",
                                        onclick: move |_| show_form.set(false),
                                        "取消"
                                    }
                                }
                                if !test_msg.read().is_empty() {
                                    div { style: "margin-top:8px;font-size:12px;", "{test_msg}" }
                                }
                            }
                        }
                        button {
                            style: "width:100%;padding:10px;margin-top:8px;border:1px dashed {c.border};border-radius:{c.radius_md};background:none;color:{c.accent};font-size:14px;cursor:pointer;",
                            onclick: move |_| { e_id.set(String::new()); e_name.set(String::new()); e_provider.set("openai".into()); e_key.set(String::new()); e_url.set("https://api.openai.com/v1".into()); show_form.set(true); },
                            "+ 添加视频生成服务"
                        }
                    }
                }

                div { style: "margin-top:20px;padding-top:16px;border-top:1px solid {c.border};",
                    label { style: "color:{c.text_secondary};font-size:13px;", "默认选择" }
                    div { style: "display:flex;gap:12px;margin-top:8px;",
                        span { style: "color:{c.text_muted};font-size:12px;", "LLM: {default_llm} | 视频: {default_video}" }
                    }
                }
            }
        }
    }
}

async fn test_conn(base_url: &str, api_key: &str) -> bool {
    let client = reqwest::Client::new();
    let url = format!("{}/models", base_url.trim_end_matches('/'));
    match client.get(&url)
        .header("Authorization", format!("Bearer {}", api_key))
        .timeout(std::time::Duration::from_secs(10))
        .send().await
    {
        Ok(resp) => resp.status().is_success(),
        Err(_) => false,
    }
}
