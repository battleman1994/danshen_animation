use dioxus::prelude::*;
use crate::styles::theme::use_theme;

#[component]
pub fn ProgressBar(progress: f64, status_text: String) -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let text_s = format!("color: {};", c.progress_text);
    let track_s = format!("height: 8px; background: {}; border-radius: {};", c.progress_track, c.radius_pill);
    let fill_s = format!("width: {}%; height: 100%; background: {}; border-radius: {}; transition: width 0.3s ease;", progress, c.progress_fill, c.radius_pill);

    rsx! {
        div { class: "mb-8 animate-fade-up",
            div { class: "text-sm mb-2", style: "{text_s}", "{status_text}" }
            div { class: "w-full rounded-full overflow-hidden", style: "{track_s}",
                div { style: "{fill_s}", }
            }
        }
    }
}
