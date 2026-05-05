use dioxus::prelude::*;
use crate::styles::theme::use_theme;

#[component]
pub fn Footer() -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let s = format!("color: {};", c.text_muted);
    rsx! {
        div { class: "text-center pb-8",
            p { class: "text-xs", style: "{s}", "🔥 蛋神动画 · AI 驱动的动漫风格视频生成器" }
        }
    }
}
