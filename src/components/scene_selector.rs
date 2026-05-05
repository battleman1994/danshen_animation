use dioxus::prelude::*;
use crate::components::types::SceneMode;
use crate::components::constants::get_scene_modes;
use crate::styles::theme::use_theme;

#[component]
pub fn SceneSelector(scene_mode: SceneMode, on_change: EventHandler<SceneMode>) -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let modes = get_scene_modes();
    let label_s = format!("color: {};", c.text_muted);
    let desc_s = format!("color: {};", c.text_muted);

    // 预计算所有按钮样式，避免 rsx! 内 let 问题
    let buttons: Vec<_> = modes.iter().map(|&mode| {
        let is_active = scene_mode == mode;
        let card_s = if is_active {
            format!("background: {}; border: 1.5px solid {}; border-radius: {}; cursor: pointer;", c.scene_active_bg, c.scene_active_border, c.radius_lg)
        } else {
            format!("background: {}; border: 1px solid {}; border-radius: {}; cursor: pointer;", c.scene_card_bg, c.scene_card_border, c.radius_lg)
        };
        let icon_s = if is_active { format!("color: {};", c.accent) } else { format!("color: {};", c.text_muted) };
        let name_s = if is_active { format!("color: {};", c.text_primary) } else { format!("color: {};", c.text_secondary) };
        let m = mode;
        rsx! {
            button {
                key: "{m.as_str()}",
                class: "p-4 text-center",
                style: "{card_s}",
                onclick: move |_| on_change.call(m),
                div { class: "text-xl mb-1.5", style: "{icon_s}", "{m.icon()}" }
                div { class: "font-semibold text-sm", style: "{name_s}", "{m.name()}" }
                div { class: "text-xs mt-0.5", style: "{desc_s}", "{m.desc()}" }
            }
        }
    }).collect();

    rsx! {
        div { class: "mb-8 animate-fade-up",
            h3 { class: "text-xs font-semibold uppercase tracking-[0.1em] mb-3", style: "{label_s}", "选择场景" }
            div { class: "grid grid-cols-3 gap-3",
                {buttons.into_iter()}
            }
        }
    }
}
