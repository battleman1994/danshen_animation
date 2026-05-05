use dioxus::prelude::*;
use crate::components::constants::get_styles;
use crate::styles::theme::use_theme;

#[component]
pub fn StyleSelector(style: String, on_change: EventHandler<String>) -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let styles = get_styles();
    let label_s = format!("color: {};", c.text_muted);

    rsx! {
        div { class: "mb-8 animate-fade-up",
            h3 { class: "text-xs font-semibold uppercase tracking-[0.1em] mb-3", style: "{label_s}", "选择风格" }
            div { class: "flex gap-2 flex-wrap",
                {styles.iter().map(|s| {
                    let sid = s.id.to_string(); let is_sel = style == s.id;
                    let btn_s = if is_sel {
                        format!("background: {}; color: {}; border: none; border-radius: {}; cursor: pointer;", c.accent, c.btn_text, c.radius_pill)
                    } else {
                        format!("background: {}; color: {}; border: 1px solid {}; border-radius: {}; cursor: pointer;", c.bg_card, c.pill_text, c.border, c.radius_pill)
                    };
                    rsx! {
                        button {
                            key: "{s.id}", class: "px-5 py-2.5 text-sm font-medium",
                            style: "{btn_s}",
                            onclick: move |_| on_change.call(sid.clone()), "{s.label}"
                        }
                    }
                })}
            }
        }
    }
}
