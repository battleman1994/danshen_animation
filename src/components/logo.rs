use dioxus::prelude::*;
use crate::styles::theme::use_theme;

#[component]
pub fn Logo() -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();

    let gradient = format!(
        "linear-gradient(135deg, {} 0%, {} 100%)",
        c.accent, c.accent_hover
    );

    rsx! {
        div {
            class: "w-9 h-9 flex items-center justify-center flex-shrink-0",
            style: "background: {gradient}; border-radius: 10px;",
            svg {
                view_box: "0 0 36 36",
                width: "32",
                height: "32",
                xmlns: "http://www.w3.org/2000/svg",
                // Crown
                path {
                    d: "M12 9 L9 3.5 L14 6.5 L18 1.5 L22 6.5 L27 3.5 L24 9 Z",
                    fill: "#FFD700",
                    stroke: "#E6BE00",
                    stroke_width: "0.3",
                }
                // Crown jewel
                circle {
                    cx: "18",
                    cy: "5.5",
                    r: "1",
                    fill: "#FF6B6B",
                }
                // Egg body
                ellipse {
                    cx: "18",
                    cy: "21.5",
                    rx: "9.5",
                    ry: "10.5",
                    fill: "#FFFDF5",
                }
                // Eye whites
                ellipse {
                    cx: "14",
                    cy: "20",
                    rx: "3.5",
                    ry: "4",
                    fill: "#FFFFFF",
                    stroke: "#E0DDD0",
                    stroke_width: "0.3",
                }
                ellipse {
                    cx: "22",
                    cy: "20",
                    rx: "3.5",
                    ry: "4",
                    fill: "#FFFFFF",
                    stroke: "#E0DDD0",
                    stroke_width: "0.3",
                }
                // Pupils
                circle {
                    cx: "14.5",
                    cy: "20.5",
                    r: "2",
                    fill: "#3D3D3D",
                }
                circle {
                    cx: "22.5",
                    cy: "20.5",
                    r: "2",
                    fill: "#3D3D3D",
                }
                // Eye highlights
                circle {
                    cx: "15.3",
                    cy: "19.3",
                    r: "0.8",
                    fill: "#FFFFFF",
                }
                circle {
                    cx: "23.3",
                    cy: "19.3",
                    r: "0.8",
                    fill: "#FFFFFF",
                }
                // Blush
                ellipse {
                    cx: "11",
                    cy: "23",
                    rx: "2.2",
                    ry: "1.3",
                    fill: "#FFB5B5",
                    opacity: "0.45",
                }
                ellipse {
                    cx: "25",
                    cy: "23",
                    rx: "2.2",
                    ry: "1.3",
                    fill: "#FFB5B5",
                    opacity: "0.45",
                }
                // Mouth (cute smile)
                path {
                    d: "M15 25.5 Q18 28 21 25.5",
                    stroke: "#3D3D3D",
                    stroke_width: "0.7",
                    fill: "none",
                    stroke_linecap: "round",
                }
            }
        }
    }
}
