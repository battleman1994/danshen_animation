use dioxus::prelude::*;
use crate::styles::theme::use_theme;

#[component]
pub fn ResultCard(video_url: Option<String>, on_reset: EventHandler<()>) -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let url = match video_url { Some(u) => u, None => return rsx! {} };
    let card_s = format!("background: {}; border: 1px solid {}; border-radius: {};", c.result_bg, c.result_border, c.radius_lg);
    let video_s = format!("background: {}; border: 1px solid {}; border-radius: {};", c.bg_page, c.border, c.radius_lg);
    let download_s = format!("background: {}; color: {}; border: none; border-radius: {};", c.btn_bg, c.btn_text, c.radius_md);
    let reset_s = format!("background: {}; color: {}; border: 1px solid {}; border-radius: {};", c.pill_bg, c.pill_text, c.pill_border, c.radius_md);

    rsx! {
        div { class: "mb-8 p-6 animate-fade-up", style: "{card_s}",
            h3 { class: "text-base font-semibold mb-4", style: format!("color: {};", c.text_primary), "🎬 生成结果" }
            div { class: "overflow-hidden mb-4", style: "{video_s}",
                video { controls: true, class: "w-full", style: "display: block; max-height: 400px;",
                    source { src: "{url}" }
                }
            }
            div { class: "flex gap-3",
                a { class: "text-sm px-6 py-2.5", style: "{download_s} text-decoration: none; cursor: pointer; display: inline-flex; align-items: center;", href: "{url}", target: "_blank", "📥 下载视频" }
                button { class: "text-sm px-6 py-2.5", style: "{reset_s} cursor: pointer;", onclick: move |_| on_reset.call(()), "🔄 重新生成" }
            }
        }
    }
}
