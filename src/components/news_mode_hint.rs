use dioxus::prelude::*;
use crate::styles::theme::use_theme;

#[component]
pub fn NewsModeHint() -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let hint_s = format!("background: {}; border: 1px solid {}; border-radius: {};", c.hint_bg, c.hint_border, c.radius_lg);
    let tag_s = format!("background: {}; color: {}; border-radius: {};", c.accent_subtle, c.accent, c.radius_pill);

    rsx! {
        div { class: "mb-8 p-5 animate-fade-up", style: "{hint_s}",
            div { class: "flex items-start gap-3",
                span { class: "text-xl", "📢" }
                div {
                    h4 { class: "font-semibold text-sm mb-1", style: format!("color: {};", c.text_primary), "新闻播报模式" }
                    p { class: "text-xs leading-relaxed", style: format!("color: {};", c.hint_text), "输入新闻内容或链接，AI 将自动提取关键信息，选择合适的动物主播进行动漫风格新闻播报。" }
                    div { class: "mt-3 flex gap-2",
                        span { class: "px-2.5 py-1 text-[11px] font-medium", style: "{tag_s}", "🐻 棕熊 — 严肃新闻" }
                        span { class: "px-2.5 py-1 text-[11px] font-medium", style: "{tag_s}", "🦉 猫头鹰 — 知识科普" }
                    }
                }
            }
        }
    }
}
