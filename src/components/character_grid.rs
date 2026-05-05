use dioxus::prelude::*;
use crate::components::types::SceneMode;
use crate::components::constants::get_characters;
#[component]
pub fn CharacterGrid(character: String, character_count: u32, scene_mode: SceneMode, on_character_change: EventHandler<String>, on_count_change: EventHandler<u32>) -> Element {
    let characters = get_characters();
    let show_count = scene_mode == SceneMode::Dialogue;
    rsx! {
        div { class: "rounded-2xl p-6", style: "background: #ffffff; border: 1px solid #f0e6d8; box-shadow: 0 1px 3px rgba(45,45,45,0.04);",
            div { class: "flex items-center justify-between mb-5",
                h3 { class: "text-base font-semibold", style: "color: #2d2d2d;", "🎭 选择角色" }
                if show_count {
                    div { class: "flex items-center gap-2",
                        span { class: "text-sm", style: "color: #8a8a86;", "角色数" }
                        for n in [1u32, 2, 3] {
                            button {
                                key: "count-{n}", class: "w-8 h-8 text-sm font-bold",
                                style: if character_count == n { "background: linear-gradient(135deg, #ff6b6b, #ffa07a); color: #ffffff; border: none; border-radius: 50px; cursor: pointer;" } else { "background: #fef9f0; color: #8a8a86; border: 1px solid #f0e6d8; border-radius: 50px; cursor: pointer;" },
                                onclick: move |_| on_count_change.call(n), "{n}"
                            }
                        }
                    }
                }
            }
            div { class: "grid grid-cols-4 sm:grid-cols-5 gap-3",
                {characters.iter().map(|char| {
                    let char_id = char.id.to_string();
                    let is_sel = character == char.id;
                    rsx! {
                        button {
                            key: "{char.id}", class: "relative p-3 rounded-2xl text-center card-selectable",
                            style: if is_sel { "background: linear-gradient(135deg, rgba(255,107,107,0.06), rgba(167,139,250,0.08)); border: 2px solid #a78bfa; box-shadow: 0 0 0 4px rgba(167,139,250,0.1);" } else { "background: #fef9f0; border: 1px solid #f0e6d8;" },
                            onclick: move |_| on_character_change.call(char_id.clone()),
                            div { class: "text-3xl mb-1", "{char.emoji}" }
                            div { class: "text-xs font-semibold", style: if is_sel { "color: #2d2d2d;" } else { "color: #5f5f5d;" }, "{char.name}" }
                            div { class: "text-[10px] mt-0.5", style: "color: #8a8a86;", "{char.style}" }
                            if is_sel { div { class: "absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full flex items-center justify-center text-white text-[10px]", style: "background: linear-gradient(135deg, #ff6b6b, #a78bfa);", "✓" } }
                        }
                    }
                })}
            }
        }
    }
}
