use dioxus::prelude::*;
use crate::styles::theme::use_theme;
use crate::components::user::AuthBar;

#[component]
pub fn Header() -> Element {
    let mut theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let t = *theme_ctx.theme.read();

    let badge_s = format!(
        "background: {}; color: {}; border: 1px solid {}; border-radius: {};",
        c.badge_bg, c.badge_text, c.badge_border, c.radius_pill,
    );
    let title_s = format!(
        "background: {}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;",
        c.title_gradient,
    );
    let sub_s = format!("color: {}; max-width: 420px; margin: 0 auto;", c.text_muted);

    rsx! {
        div { class: "text-center mb-12 animate-fade-up",
            // 顶部栏：Logo + 主题切换 + 登录
            div { class: "flex items-center justify-between mb-5",
                // Logo 区域
                div { class: "flex items-center gap-2",
                    div {
                        class: "w-9 h-9 rounded-xl flex items-center justify-center text-lg font-bold",
                        style: "background: linear-gradient(135deg, {c.accent} 0%, {c.accent_hover} 100%); color: #fff;",
                        "蛋"
                    }
                    span { class: "font-bold text-lg hidden sm:inline", style: "color: {c.text_primary};",
                        "蛋神动画"
                    }
                }

                // 右侧：主题切换 + 登录
                div { class: "flex items-center gap-2",
                    // 主题切换按钮
                    button {
                        class: "inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium",
                        style: "{badge_s} cursor: pointer;",
                        onclick: move |_| theme_ctx.toggle(),
                        title: "切换主题 — 当前：{t.label()}",
                        span { "{t.icon()}" }
                        span { class: "hidden sm:inline", "{t.label()}" }
                    }

                    // 用户登录/AuthBar
                    AuthBar {}
                }
            }

            // 标题区域
            h1 {
                class: "text-5xl md:text-6xl font-bold mb-4",
                style: "{title_s}",
                "🔥 蛋神动画"
            }
            p { class: "text-lg", style: "{sub_s}",
                "输入热点话题，AI 为你生成可爱动物主演的动漫视频"
            }

            // 认证提示条（未登录时显示）
            // (AuthBar 已经内嵌在顶部栏了)
        }
    }
}
