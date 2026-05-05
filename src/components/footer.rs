use dioxus::prelude::*;
#[component]
pub fn Footer() -> Element {
    rsx! {
        div { class: "text-center pb-8",
            p { class: "text-xs", style: "color: #8a8a86;", "🔥 蛋生动画 · AI 驱动的动漫风格视频生成器" }
        }
    }
}
