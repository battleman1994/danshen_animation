use dioxus::prelude::*;
#[component]
pub fn DecorativeBlobs() -> Element {
    rsx! {
        div { class: "fixed inset-0 pointer-events-none overflow-hidden", style: "z-index: -1;",
            div { class: "absolute -top-32 -left-32 w-96 h-96 rounded-full opacity-20", style: "background: radial-gradient(circle, #ff6b6b 0%, transparent 70%); animation: float 6s ease-in-out infinite;" }
            div { class: "absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full opacity-20", style: "background: radial-gradient(circle, #a78bfa 0%, transparent 70%); animation: float 8s ease-in-out 2s infinite;" }
            div { class: "absolute top-1/3 -right-20 w-64 h-64 rounded-full opacity-10", style: "background: radial-gradient(circle, #ffa07a 0%, transparent 70%); animation: float 7s ease-in-out 1s infinite;" }
        }
    }
}
