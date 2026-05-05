use dioxus::prelude::*;
use crate::components::constants::get_styles;
#[component]
pub fn StyleSelector(style: String, on_change: EventHandler<String>) -> Element {
    let styles = get_styles();
    rsx! {
        div { class: "mb-8 animate-fade-up",
            h3 { class: "text-xs font-semibold uppercase tracking-[0.1em] mb-3", style: "color: #8a8a86;", "选择风格" }
            div { class: "flex gap-2",
                {styles.iter().map(|s| {
                    let sid = s.id.to_string(); let is_sel = style == s.id;
                    rsx! {
                        button {
                            key: "{s.id}", class: "px-5 py-2.5 text-sm font-medium",
                            style: if is_sel { "background: linear-gradient(135deg, #ff6b6b, #ffa07a); color: #ffffff; border: none; border-radius: 50px; cursor: pointer;" } else { "background: #ffffff; color: #5f5f5d; border: 1px solid #f0e6d8; border-radius: 50px; cursor: pointer;" },
                            onclick: move |_| on_change.call(sid.clone()), "{s.label}"
                        }
                    }
                })}
            }
        }
    }
}
