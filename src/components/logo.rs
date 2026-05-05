//! 🥚 动漫风格 Logo 组件 — 破壳动物脸
//! 蛋壳裂开，探出萌萌的动漫小猫脸，呼应"蛋神"和动物角色主题
use dioxus::prelude::*;
use crate::styles::theme::use_theme;

#[component]
pub fn Logo() -> Element {
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();

    rsx! {
        div { class: "flex items-center justify-center",
            style: "width: 36px; height: 36px;",
            svg {
                view_box: "0 0 100 100",
                xmlns: "http://www.w3.org/2000/svg",
                // 动画 style
                style: "transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);",
                onmouseenter: |_| {},
                // 星星 1 — 左上
                g { transform: "translate(20, 20) scale(1.2)",
                    path {
                        d: "M0,-6 C1,-2 2,-1 6,0 C2,1 1,2 0,6 C-1,2 -2,1 -6,0 C-2,-1 -1,-2 0,-6Z",
                        fill: "{c.accent}",
                        opacity: "0.6",
                    }
                }
                // 星星 2 — 右上
                g { transform: "translate(80, 24) scale(0.9)",
                    path {
                        d: "M0,-6 C1,-2 2,-1 6,0 C2,1 1,2 0,6 C-1,2 -2,1 -6,0 C-2,-1 -1,-2 0,-6Z",
                        fill: "{c.accent}",
                        opacity: "0.5",
                    }
                }
                // 星星 3 — 左中
                g { transform: "translate(16, 52) scale(0.7)",
                    path {
                        d: "M0,-6 C1,-2 2,-1 6,0 C2,1 1,2 0,6 C-1,2 -2,1 -6,0 C-2,-1 -1,-2 0,-6Z",
                        fill: "{c.accent}",
                        opacity: "0.35",
                    }
                }
                // 闪光 sparkle 1
                g { transform: "translate(82, 52)",
                    path {
                        d: "M0,-4 L1,-1 L4,0 L1,1 L0,4 L-1,1 L-4,0 L-1,-1Z",
                        fill: "{c.accent}",
                        opacity: "0.45",
                    }
                }
                // 闪光 sparkle 2
                g { transform: "translate(24, 76) scale(0.8)",
                    path {
                        d: "M0,-4 L1,-1 L4,0 L1,1 L0,4 L-1,1 L-4,0 L-1,-1Z",
                        fill: "{c.accent}",
                        opacity: "0.3",
                    }
                }

                // === 蛋壳 ===
                // 蛋壳主体（下半部）
                path {
                    d: "M50,30 C28,30 24,44 24,58 C24,76 36,88 50,88 C64,88 76,76 76,58 C76,44 72,30 50,30Z",
                    fill: "none",
                    stroke: "{c.accent}",
                    stroke_width: "2.5",
                    opacity: "0.85",
                }
                // 蛋壳内部底色
                path {
                    d: "M50,33 C32,33 28,46 28,58 C28,74 38,84 50,84 C62,84 72,74 72,58 C72,46 68,33 50,33Z",
                    fill: "{c.accent}",
                    opacity: "0.08",
                }
                // 蛋壳高光
                path {
                    d: "M36,52 C36,44 42,40 46,38",
                    fill: "none",
                    stroke: "{c.accent}",
                    stroke_width: "1.5",
                    stroke_linecap: "round",
                    opacity: "0.25",
                }
                // 蛋壳裂口（心形裂痕）
                path {
                    d: "M50,30 C50,30 44,40 38,44 C34,46 34,52 38,54 C42,56 46,54 50,48 C54,54 58,56 62,54 C66,52 66,46 62,44 C56,40 50,30 50,30Z",
                    fill: "{c.bg_card}",
                    stroke: "{c.accent}",
                    stroke_width: "1.5",
                    opacity: "0.9",
                }

                // === 蛋壳内部（裂口透出的暖色背景）===
                path {
                    d: "M50,32 C50,32 44,41 39,44 C36,46 36,50 39,52 C42,54 46,52 50,47 C54,52 58,54 61,52 C64,50 64,46 61,44 C56,41 50,32 50,32Z",
                    fill: "{c.accent}",
                    opacity: "0.12",
                }

                // === 猫脸 ===
                // 猫脸底色（在裂口位置）
                g { transform: "translate(0, 0)",
                    // 猫脸轮廓
                    ellipse {
                        cx: "50",
                        cy: "39",
                        rx: "10",
                        ry: "8",
                        fill: "{c.text_primary}",
                        opacity: "0.9",
                    }
                    // 左耳
                    path {
                        d: "M43,34 L42,28 L47,32Z",
                        fill: "{c.accent}",
                        opacity: "0.8",
                    }
                    path {
                        d: "M43,34 L42,28 L47,32Z",
                        fill: "{c.text_primary}",
                        transform: "scale(0.6) translate(29, 20)",
                        opacity: "0.5",
                    }
                    // 右耳
                    path {
                        d: "M57,34 L58,28 L53,32Z",
                        fill: "{c.accent}",
                        opacity: "0.8",
                    }
                    path {
                        d: "M57,34 L58,28 L53,32Z",
                        fill: "{c.text_primary}",
                        transform: "scale(0.6) translate(36, 20)",
                        opacity: "0.5",
                    }
                    // 左眼（大眼 anime 风格）
                    ellipse {
                        cx: "46",
                        cy: "38",
                        rx: "2.5",
                        ry: "3",
                        fill: "{c.bg_page}",
                    }
                    circle {
                        cx: "46.5",
                        cy: "37.5",
                        r: "1.2",
                        fill: "{c.text_primary}",
                    }
                    // 右眼
                    ellipse {
                        cx: "54",
                        cy: "38",
                        rx: "2.5",
                        ry: "3",
                        fill: "{c.bg_page}",
                    }
                    circle {
                        cx: "54.5",
                        cy: "37.5",
                        r: "1.2",
                        fill: "{c.text_primary}",
                    }
                    // 眼睛高光
                    circle {
                        cx: "47.2",
                        cy: "36.8",
                        r: "0.6",
                        fill: "{c.bg_page}",
                        opacity: "0.8",
                    }
                    circle {
                        cx: "55.2",
                        cy: "36.8",
                        r: "0.6",
                        fill: "{c.bg_page}",
                        opacity: "0.8",
                    }
                    // 小鼻子（倒心形）
                    path {
                        d: "M49,41 L50,42 L51,41Z",
                        fill: "{c.accent}",
                        opacity: "0.7",
                    }
                    // 嘴巴
                    path {
                        d: "M48,42.5 Q50,44 52,42.5",
                        fill: "none",
                        stroke: "{c.accent}",
                        stroke_width: "0.8",
                        opacity: "0.5",
                    }
                    // 胡须
                    line {
                        x1: "42",
                        y1: "39",
                        x2: "36",
                        y2: "38",
                        stroke: "{c.accent}",
                        stroke_width: "0.6",
                        opacity: "0.3",
                    }
                    line {
                        x1: "42",
                        y1: "40.5",
                        x2: "35",
                        y2: "41",
                        stroke: "{c.accent}",
                        stroke_width: "0.6",
                        opacity: "0.3",
                    }
                    line {
                        x1: "58",
                        y1: "39",
                        x2: "64",
                        y2: "38",
                        stroke: "{c.accent}",
                        stroke_width: "0.6",
                        opacity: "0.3",
                    }
                    line {
                        x1: "58",
                        y1: "40.5",
                        x2: "65",
                        y2: "41",
                        stroke: "{c.accent}",
                        stroke_width: "0.6",
                        opacity: "0.3",
                    }
                }
            }
        }
    }
}
