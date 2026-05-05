use dioxus::prelude::*;
use crate::components::types::SceneMode;
use crate::components::constants::get_scene_modes;
#[component]
pub fn SceneSelector(scene_mode: SceneMode, on_change: EventHandler<SceneMode>) -> Element {
    let modes = get_scene_modes();
    rsx! {
        div { class: "mb-8 animate-fade-up",
            h3 { class: "text-xs font-semibold uppercase tracking-[0.1em] mb-3", style: "color: #8a8a86;", "选择场景" }
            div { class: "grid grid-cols-3 gap-3",
                for mode in modes {
                    button {
                        key: "{mode.as_str()}", class: "card-selectable p-4 rounded-2xl text-center",
                        style: if scene_mode == mode {
                            "background: linear-gradient(135deg, rgba(255, 107, 107, 0.08), rgba(167, 139, 250, 0.1)); border: 1.5px solid rgba(167, 139, 250, 0.4); box-shadow: 0 2px 12px rgba(167, 139, 250, 0.1);"
                        } else { "background: #ffffff; border: 1px solid #f0e6d8; box-shadow: 0 1px 3px rgba(45,45,45,0.03);" },
                        onclick: move |_| on_change.call(mode),
                        div { class: "text-xl mb-1.5", style: if scene_mode == mode { "color: #a78bfa;" } else { "color: #8a8a86;" }, "{mode.icon()}" }
                        div { class: "font-semibold text-sm", style: if scene_mode == mode { "color: #2d2d2d;" } else { "color: #5f5f5d;" }, "{mode.name()}" }
                        div { class: "text-xs mt-0.5", style: "color: #8a8a86;", "{mode.desc()}" }
                    }
                }
            }
        }
    }
}
