use dioxus::prelude::*;
#[component]
pub fn Header() -> Element {
    rsx! {
        div { class: "text-center mb-12 animate-fade-up",
            div { class: "inline-flex items-center gap-2 px-4 py-1.5 mb-5 text-sm font-medium", style: "background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(167, 139, 250, 0.1)); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.15); border-radius: 50px;", "✨ AI 动漫视频生成器" }
            h1 { class: "text-5xl md:text-6xl font-bold mb-4", style: "background: linear-gradient(135deg, #ff6b6b 0%, #ffa07a 50%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;", "🔥 蛋生动画" }
            p { class: "text-lg", style: "color: #5f5f5d; max-width: 420px; margin: 0 auto;", "输入热点话题，AI 为你生成可爱动物主演的动漫视频" }
        }
    }
}
