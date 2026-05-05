use dioxus::prelude::*;
use crate::styles::theme::use_theme;

#[component]
pub fn DecorativeBlobs() -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let b1 = format!("background: radial-gradient(circle, {} 0%, transparent 70%); animation: float 6s ease-in-out infinite;", c.accent);
    let b2 = format!("background: radial-gradient(circle, {} 0%, transparent 70%); animation: float 8s ease-in-out 2s infinite;", c.accent);
    let b3 = format!("background: radial-gradient(circle, {} 0%, transparent 70%); animation: float 7s ease-in-out 1s infinite;", c.accent);
    rsx! {
        div { class: "fixed inset-0 pointer-events-none overflow-hidden", style: "z-index: -1;",
            div { class: "absolute -top-32 -left-32 w-96 h-96 rounded-full opacity-20", style: "{b1}" }
            div { class: "absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full opacity-20", style: "{b2}" }
            div { class: "absolute top-1/3 -right-20 w-64 h-64 rounded-full opacity-10", style: "{b3}" }
        }
    }
}
