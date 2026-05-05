use dioxus::prelude::*;
use crate::components::types::SceneMode;
use crate::components::constants::get_characters;
use crate::styles::theme::use_theme;

#[component]
pub fn CharacterGrid(character: String, character_count: u32, scene_mode: SceneMode, on_character_change: EventHandler<String>, on_count_change: EventHandler<u32>) -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let characters = get_characters();
    let show_count = scene_mode == SceneMode::Dialogue;
    let card_s = format!("background: {}; border: 1px solid {}; border-radius: {};", c.bg_card, c.border, c.radius_lg);
    let title_s = format!("color: {};", c.text_primary);
    let muted_s = format!("color: {};", c.text_muted);

    rsx! {
        div { class: "p-6", style: "{card_s}",
            div { class: "flex items-center justify-between mb-5",
                h3 { class: "text-base font-semibold", style: "{title_s}", "🎭 选择角色" }
                if show_count {
                    div { class: "flex items-center gap-2",
                        span { class: "text-sm", style: "{muted_s}", "角色数" }
                        {[1u32, 2, 3].iter().map(|&n| {
                            let btn_s = if character_count == n {
                                format!("background: {}; color: {}; border: none; border-radius: {}; cursor: pointer;", c.accent, c.btn_text, c.radius_pill)
                            } else {
                                format!("background: {}; color: {}; border: 1px solid {}; border-radius: {}; cursor: pointer;", c.count_btn_bg, c.count_btn_text, c.border, c.radius_pill)
                            };
                            rsx! {
                                button {
                                    key: "count-{n}",
                                    class: "w-8 h-8 text-sm font-bold",
                                    style: "{btn_s}",
                                    onclick: move |_| on_count_change.call(n),
                                    "{n}"
                                }
                            }
                        })}
                    }
                }
            }
            div { class: "grid grid-cols-4 sm:grid-cols-5 gap-3",
                {characters.iter().map(|char| {
                    let char_id = char.id.to_string();
                    let is_sel = character == char.id;
                    let char_s = if is_sel {
                        format!("background: {}; border: 2px solid {}; border-radius: {}; cursor: pointer;", c.accent_subtle, c.accent_border, c.radius_lg)
                    } else {
                        format!("background: {}; border: 1px solid {}; border-radius: {}; cursor: pointer;", c.scene_card_bg, c.scene_card_border, c.radius_lg)
                    };
                    let name_s = if is_sel { format!("color: {};", c.text_primary) } else { format!("color: {};", c.text_secondary) };
                    rsx! {
                        button {
                            key: "{char.id}",
                            class: "relative p-3 text-center",
                            style: "{char_s}",
                            onclick: move |_| on_character_change.call(char_id.clone()),
                            div { class: "text-3xl mb-1", "{char.emoji}" }
                            div { class: "text-xs font-semibold", style: "{name_s}", "{char.name}" }
                            div { class: "text-[10px] mt-0.5", style: "{muted_s}", "{char.style}" }
                            if is_sel {
                                div { class: "absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full flex items-center justify-center text-white text-[10px]", style: format!("background: {};", c.accent), "✓" }
                            }
                        }
                    }
                })}
            }
        }
    }
}
