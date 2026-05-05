use dioxus::prelude::*;
#[component]
pub fn NewsModeHint() -> Element {
    rsx! {
        div { class: "mb-8 p-5 rounded-2xl animate-fade-up", style: "background: linear-gradient(135deg, rgba(255,107,107,0.04), rgba(167,139,250,0.06)); border: 1px solid rgba(167,139,250,0.15);",
            div { class: "flex items-start gap-3",
                span { class: "text-xl", "📢" }
                div {
                    h4 { class: "font-semibold text-sm mb-1", style: "color: #2d2d2d;", "新闻播报模式" }
                    p { class: "text-xs leading-relaxed", style: "color: #5f5f5d;", "输入新闻内容或链接，AI 将自动提取关键信息，选择合适的动物主播进行动漫风格新闻播报。" }
                    div { class: "mt-3 flex gap-2",
                        span { class: "px-2.5 py-1 rounded-pill text-[11px] font-medium", style: "background: rgba(167,139,250,0.1); color: #a78bfa;", "🐻 棕熊 — 严肃新闻" }
                        span { class: "px-2.5 py-1 rounded-pill text-[11px] font-medium", style: "background: rgba(255,107,107,0.08); color: #ff6b6b;", "🦉 猫头鹰 — 知识科普" }
                    }
                }
            }
        }
    }
}
