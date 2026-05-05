use dioxus::prelude::*;
#[component]
pub fn ResultCard(video_url: Option<String>, on_reset: EventHandler<()>) -> Element {
    let url = match video_url { Some(u) => u, None => return rsx! {} };
    rsx! {
        div { class: "mb-8 rounded-2xl p-6 animate-fade-up", style: "background: #ffffff; border: 1px solid #f0e6d8;",
            h3 { class: "text-base font-semibold mb-4", style: "color: #2d2d2d;", "🎬 生成结果" }
            div { class: "rounded-xl overflow-hidden mb-4", style: "background: #fef9f0; border: 1px solid #f0e6d8;",
                video { controls: true, class: "w-full", style: "display: block; max-height: 400px;",
                    source { src: "{url}" }
                }
            }
            div { class: "flex gap-3",
                a { class: "btn-gradient text-sm px-6 py-2.5", href: "{url}", target: "_blank", "📥 下载视频" }
                button { class: "px-6 py-2.5 text-sm font-medium rounded-xl", style: "background: #fef9f0; color: #5f5f5d; border: 1px solid #f0e6d8; cursor: pointer;", onclick: move |_| on_reset.call(()), "🔄 重新生成" }
            }
        }
    }
}
