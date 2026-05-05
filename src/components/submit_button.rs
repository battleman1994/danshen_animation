use dioxus::prelude::*;
use crate::styles::theme::use_theme;

#[component]
pub fn SubmitButton(loading: bool, can_submit: bool, on_submit: EventHandler<()>) -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();
    let btn_s = if loading {
        format!("background: {}; color: {}; border: 1px solid {}; border-radius: {}; cursor: not-allowed;",
            c.btn_loading_bg, c.btn_loading_text, c.border, c.radius_md)
    } else {
        format!("background: {}; color: {}; border: none; border-radius: {}; cursor: pointer;",
            c.btn_bg, c.btn_text, c.radius_md)
    };

    rsx! {
        div { class: "text-center mb-8 animate-fade-up",
            button {
                class: "text-base font-semibold px-10 py-3.5",
                disabled: !can_submit || loading,
                style: "{btn_s}",
                onclick: move |_| on_submit.call(()),
                if loading { span { "⏳ 正在生成..." } } else { span { "✨ 开始生成" } }
            }
        }
    }
}
