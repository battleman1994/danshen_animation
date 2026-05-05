use dioxus::prelude::*;
use crate::components::types::{SourceType, SceneMode};
use crate::components::constants::{get_source_types, get_placeholder};
use crate::styles::theme::use_theme;

#[component]
pub fn SourceInput(source: String, source_type: SourceType, scene_mode: SceneMode, on_change: EventHandler<String>, on_type_change: EventHandler<SourceType>) -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let placeholder = get_placeholder(source_type, scene_mode);
    let source_types = get_source_types();
    let card_s = format!("background: {}; border: 1px solid {}; border-radius: {};", c.bg_card, c.border, c.radius_lg);
    let ta_s = format!("background: {}; border: 1px solid {}; color: {}; outline: none; font-family: inherit; border-radius: {};", c.bg_input, c.border, c.text_primary, c.radius_sm);

    // 预计算按钮
    let pills: Vec<_> = source_types.iter().map(|&st| {
        let is_active = source_type == st;
        let pill_s = if is_active {
            format!("background: {}; color: {}; border: none; border-radius: {}; cursor: pointer;", c.pill_active_bg, c.pill_active_text, c.radius_pill)
        } else {
            format!("background: {}; color: {}; border: 1px solid {}; border-radius: {}; cursor: pointer;", c.pill_bg, c.pill_text, c.pill_border, c.radius_pill)
        };
        rsx! {
            button {
                key: "{st.as_str()}",
                class: "flex items-center gap-1.5 px-4 py-2 text-sm font-medium",
                style: "{pill_s}",
                onclick: move |_| on_type_change.call(st),
                span { "{st.icon()}" } span { "{st.label()}" }
            }
        }
    }).collect();

    rsx! {
        div { class: "mb-8 p-6", style: "{card_s}",
            div { class: "flex gap-2 mb-4 flex-wrap",
                {pills.into_iter()}
            }
            textarea {
                value: "{source}", class: "w-full h-36 p-4 text-base leading-relaxed resize-none",
                style: "{ta_s}",
                placeholder: "{placeholder}",
                oninput: move |e| on_change.call(e.value())
            }
        }
    }
}
