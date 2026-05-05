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
use crate::components::types::SceneMode;
use crate::components::user::use_user_provider;
use crate::hooks::use_animation::use_animation;
use crate::styles::theme::use_theme_provider;
use crate::styles::STYLE_CSS;

#[component]
pub fn App() -> Element {
    // 注入全局 CSS（直接内嵌在组件树中，桌面/Web 都生效）
    let theme_ctx = use_theme_provider();
    let c = theme_ctx.colors();

    // 初始化认证状态
    let _auth = use_user_provider();

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

    rsx! {
        // 内嵌 CSS 确保在桌面 webview 中也生效
        style { "{STYLE_CSS}" }
        main {
            class: "min-h-screen",
            style: "background: {c.bg_page}; position: relative;",
            DecorativeBlobs {}
            div { class: "relative max-w-2xl mx-auto px-5 py-12 md:py-16",
                Header {}
                SceneSelector { scene_mode, on_change: move |m| anim.scene_mode.set(m) }
                SourceInput { source: source.clone(), source_type, scene_mode, on_change: move |s| anim.source.set(s), on_type_change: move |t| anim.source_type.set(t) }
                if scene_mode != SceneMode::News {
                    div { class: "mb-8 overflow-hidden",
                        CharacterGrid { character: character.clone(), character_count, scene_mode, on_character_change: move |id| anim.character.set(id), on_count_change: move |n| anim.character_count.set(n) }
                    }
                }
                if scene_mode == SceneMode::News { NewsModeHint {} }
                if scene_mode == SceneMode::Dialogue { StyleSelector { style: style.clone(), on_change: move |s| anim.style.set(s) } }
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
    }
}
