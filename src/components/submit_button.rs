use dioxus::prelude::*;
#[component]
pub fn SubmitButton(loading: bool, can_submit: bool, on_submit: EventHandler<()>) -> Element {
    rsx! {
        div { class: "text-center mb-8 animate-fade-up",
            button {
                class: "btn-gradient text-base font-semibold px-10 py-3.5",
                disabled: !can_submit || loading,
                style: if can_submit && !loading { "box-shadow: var(--shadow-button);" } else { "" },
                onclick: move |_| on_submit.call(()),
                if loading { span { "⏳ 正在生成..." } } else { span { "✨ 开始生成" } }
            }
        }
    }
}
