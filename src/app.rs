use dioxus::prelude::*;
use crate::components::decorative_blobs::DecorativeBlobs;
use crate::components::footer::Footer;
use crate::components::header::Header;
use crate::components::scene_selector::SceneSelector;
use crate::components::source_input::SourceInput;
use crate::components::character_grid::CharacterGrid;
use crate::components::style_selector::StyleSelector;
use crate::components::news_mode_hint::NewsModeHint;
use crate::components::submit_button::SubmitButton;
use crate::components::progress_bar::ProgressBar;
use crate::components::result_card::ResultCard;
use crate::components::config_modal::ConfigModal;
use crate::components::types::SceneMode;
use crate::hooks::use_animation::use_animation;
use crate::styles::theme::use_theme_provider;
use crate::styles::STYLE_CSS;

#[component]
pub fn App() -> Element {
    let theme_ctx = use_theme_provider();
    let c = theme_ctx.colors();

    let mut anim = use_animation();
    let scene_mode = anim.scene_mode();
    let source = anim.source();
    let source_type = anim.source_type();
    let character = anim.character();
    let character_count = anim.character_count();
    let style = anim.style();
    let loading = anim.loading();
    let progress = anim.progress() as f64;
    let status_text = anim.status_text();
    let result = anim.result();
    let error_msg = anim.error();
    let can_submit = anim.can_submit();
    let llm_model = anim.llm_model();
    let llm_models = anim.llm_models();
    let mut show_config = use_signal(|| false);

    let ts = c.text_secondary;
    let tp = c.text_primary;
    let _tm = c.text_muted;
    let _ac = c.accent;
    let bd = c.border;
    let bgc = c.bg_card;
    let _bgp = c.bg_page;
    let rsm = c.radius_sm;
    let _rmd = c.radius_md;
    let _rlg = c.radius_lg;

    let row_label = format!(
        "font-size:12px;color:{ts};margin-bottom:4px;font-weight:500;"
    );
    let compact_select = format!(
        "width:100%;padding:6px 8px;border-radius:{rsm};border:1px solid {bd};background:{bgc};color:{tp};font-size:12px;outline:none;cursor:pointer;"
    );
    let gear_btn = format!(
        "padding:4px 8px;font-size:12px;border-radius:{rsm};border:1px solid {bd};background:{bgc};color:{ts};cursor:pointer;white-space:nowrap;"
    );

    rsx! {
        style { "{STYLE_CSS}" }
        main {
            class: "min-h-screen",
            style: "background: {c.bg_page}; position: relative;",
            DecorativeBlobs {}
            div { class: "relative max-w-2xl mx-auto px-5 py-12 md:py-16",
                Header {}
                SceneSelector { scene_mode, on_change: move |m| anim.scene_mode.set(m) }
                SourceInput { source: source.clone(), source_type, scene_mode, on_change: move |s| anim.source.set(s), on_type_change: move |t| anim.source_type.set(t) }

                // ── 内容分析模型选择器（紧贴输入区下方） ──
                div { class: "mb-6 flex items-end gap-2",
                    div { style: "flex: 1;",
                        div { style: "{row_label}", "🧠 内容分析模型 — 将输入内容转化为视频提示词" }
                        select {
                            style: "{compact_select}",
                            value: llm_model,
                            onchange: move |e| anim.llm_model.set(e.value()),
                            for model in llm_models.iter() {
                                option {
                                    value: "{model.id}",
                                    selected: llm_model == model.id,
                                    disabled: !(model.available && model.supported_input_types.contains(&source_type.as_str().to_string())),
                                    {format!("{} {}",
                                        if model.mode == "local" { "🔑" } else { "☁️" },
                                        model.name
                                    )}
                                }
                            }
                        }
                    }
                    button {
                        style: "{gear_btn}",
                        onclick: move |_| show_config.set(true),
                        title: "自定义模型配置",
                        "⚙️"
                    }
                }

                if scene_mode != SceneMode::News {
                    div { class: "mb-8 overflow-hidden",
                        CharacterGrid { character: character.clone(), character_count, scene_mode, on_character_change: move |id| anim.character.set(id), on_count_change: move |n| anim.character_count.set(n) }
                    }
                }
                if scene_mode == SceneMode::News { NewsModeHint {} }
                if scene_mode == SceneMode::Dialogue { StyleSelector { style: style.clone(), on_change: move |s| anim.style.set(s) } }

                // ── 视频生成模型选择器（在提交按钮上方） ──
                div { class: "mb-6 flex items-end gap-2",
                    div { style: "flex: 1;",
                        div { style: "{row_label}", "🎬 视频生成模型 — 将提示词生成最终视频" }
                        select {
                            style: "{compact_select}",
                            value: anim.provider(),
                            onchange: move |e| anim.provider.set(e.value()),
                            for prov in anim.providers().iter() {
                                option {
                                    value: "{prov.id}",
                                    selected: anim.provider() == prov.id,
                                    disabled: !(prov.available && prov.supported_input_types.contains(&source_type.as_str().to_string())),
                                    {format!("{} {} — {}",
                                        if prov.mode == "local" { "🔑" } else { "☁️" },
                                        prov.name,
                                        prov.description
                                    )}
                                }
                            }
                        }
                    }
                    button {
                        style: "{gear_btn}",
                        onclick: move |_| show_config.set(true),
                        title: "自定义模型配置",
                        "⚙️"
                    }
                }

                SubmitButton { loading, can_submit, on_submit: move |_| anim.handle_submit() }

                if let Some(ref msg) = error_msg {
                    div { class: "mb-6 p-4 animate-fade-up", style: "background: rgba(239,68,68,0.10); border: 1px solid rgba(239,68,68,0.30); border-radius: {c.radius_lg}; color: #fca5a5; font-size: 14px; line-height: 1.6;",
                        div { class: "flex items-start gap-3",
                            span { class: "text-lg flex-shrink-0", "⚠️" }
                            div {
                                p { class: "font-semibold mb-1", style: "color: #fca5a5;", "生成请求失败" }
                                p { style: "color: rgba(252,165,165,0.80); word-break: break-word;", "{msg}" }
                            }
                        }
                    }
                }
                if loading { ProgressBar { progress, status_text } }
                ResultCard { video_url: result, on_reset: move |_| anim.handle_reset() }
                Footer {}
            }
        }
        // ── 自定义模型配置弹窗 ──
        ConfigModal {
            show: show_config,
            llm_models: anim.llm_models,
            providers: anim.providers,
            default_llm: anim.llm_model,
            default_video: anim.provider,
        }
    }
}
