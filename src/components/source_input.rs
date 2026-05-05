use dioxus::prelude::*;
use crate::components::types::{SourceType, SceneMode};
use crate::components::constants::{get_source_types, get_placeholder};
#[component]
pub fn SourceInput(source: String, source_type: SourceType, scene_mode: SceneMode, on_change: EventHandler<String>, on_type_change: EventHandler<SourceType>) -> Element {
    let placeholder = get_placeholder(source_type, scene_mode);
    let source_types = get_source_types();
    rsx! {
        div { class: "mb-8 rounded-2xl p-6 animate-fade-up", style: "background: #ffffff; border: 1px solid #f0e6d8; box-shadow: 0 1px 3px rgba(45,45,45,0.04);",
            div { class: "flex gap-2 mb-4 flex-wrap",
                for st in source_types {
                    button {
                        key: "{st.as_str()}", class: "flex items-center gap-1.5 px-4 py-2 text-sm font-medium",
                        style: if source_type == st {
                            "background: linear-gradient(135deg, #ff6b6b, #ffa07a, #a78bfa); color: #ffffff; border: none; border-radius: 50px; box-shadow: 0 2px 8px rgba(255, 107, 107, 0.25);"
                        } else { "background: #fef9f0; color: #5f5f5d; border: 1px solid #f0e6d8; border-radius: 50px;" },
                        onclick: move |_| on_type_change.call(st),
                        span { "{st.icon()}" } span { "{st.label()}" }
                    }
                }
            }
            textarea { value: "{source}", class: "w-full h-36 p-4 rounded-xl text-base leading-relaxed resize-none", style: "background: #fef9f0; border: 1px solid #f0e6d8; color: #2d2d2d; outline: none; font-family: inherit;", placeholder: "{placeholder}", oninput: move |e| on_change.call(e.value()) }
        }
    }
}
