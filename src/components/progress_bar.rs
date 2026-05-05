use dioxus::prelude::*;
#[component]
pub fn ProgressBar(progress: f64, status_text: String) -> Element {
    rsx! {
        div { class: "mb-8 animate-fade-up",
            div { class: "text-sm mb-2", style: "color: #5f5f5d;", "{status_text}" }
            div { class: "w-full rounded-full overflow-hidden", style: "height: 8px; background: #f0e6d8;",
                div { class: "progress-gradient", style: "width: {progress}%;" }
            }
        }
    }
}
