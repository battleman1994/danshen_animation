use dioxus::prelude::*;
use crate::api::client;
use crate::components::types::*;
use crate::components::user::user_state::use_user;
use crate::styles::theme::use_theme;

/// 登录模态框 — 支持 QQ、微信、支付宝、手机验证码登录
#[component]
pub fn LoginModal() -> Element {
    let mut user_ctx = use_user();
    let theme_ctx = use_theme();
    let c = theme_ctx.colors();

    // 如果已登录或弹窗关闭，不显示
    if !*user_ctx.show_login.read() {
        return rsx! {};
    }

    // 当前选中的登录方式：qq, wechat, alipay, sms
    let mut active_tab = use_signal(|| "qq".to_string());

    // SMS 登录状态
    let mut phone = use_signal(String::new);
    let mut sms_code = use_signal(String::new);
    let mut countdown = use_signal(|| 0u32);

    // 加载状态
    let mut loading = use_signal(|| false);
    let mut error_msg = use_signal(String::new);

    // 模拟回调 — 直接调用 OAuth callback API
    let do_oauth_login = move |provider: &str| {
        let provider_clone = provider.to_string();
        let mut l = loading.clone();
        let mut err = error_msg.clone();
        let mut u_ctx = user_ctx.clone();
        spawn(async move {
            l.set(true);
            err.set(String::new());
            match client::oauth_callback(&provider_clone).await {
                Ok(resp) => {
                    if resp.success {
                        if let Some(user) = resp.user {
                            u_ctx.set_logged_in(resp.token, user);
                            u_ctx.close_login();
                        }
                    } else {
                        err.set(resp.message);
                    }
                }
                Err(e) => err.set(e),
            }
            l.set(false);
        });
    };

    let do_sms_login = move || {
        let p = phone.read().clone();
        let c = sms_code.read().clone();
        let mut l = loading.clone();
        let mut err = error_msg.clone();
        let mut u_ctx = user_ctx.clone();
        let mut count = countdown.clone();
        spawn(async move {
            l.set(true);
            err.set(String::new());
            match client::sms_login(&p, &c).await {
                Ok(resp) => {
                    if resp.success {
                        if let Some(user) = resp.user {
                            u_ctx.set_logged_in(resp.token, user);
                            u_ctx.close_login();
                        }
                    } else {
                        err.set(resp.message);
                    }
                }
                Err(e) => err.set(e),
            }
            l.set(false);
        });
    };

    let send_sms = move || {
        let p = phone.read().clone();
        let mut count = countdown.clone();
        let mut err = error_msg.clone();
        if p.len() != 11 || !p.starts_with('1') {
            err.set("请输入正确的手机号".to_string());
            return;
        }
        spawn(async move {
            count.set(60u32);
            match client::send_sms_code(&p).await {
                Ok(resp) => {
                    err.set(format!("{}（调试码：{}）", resp.message, resp.debug_code.unwrap_or_default()));
                }
                Err(e) => err.set(e),
            }
        });
    };

    // 倒计时效果
    {
        let mut count = countdown.clone();
        use_effect(move || {
            let c = count();
            if c > 0 {
                let mut cnt = count.clone();
                spawn(async move {
                    tokio::time::sleep(std::time::Duration::from_secs(1)).await;
                    let cur = *cnt.read();
                    if cur > 0 {
                        cnt.set(cur - 1);
                    }
                });
            }
        });
    }

    let overlay_style = format!(
        "position: fixed; inset: 0; z-index: 50;\
         background: rgba(0,0,0,0.5); backdrop-filter: blur(4px);\
         display: flex; align-items: center; justify-content: center;"
    );
    let modal_style = format!(
        "background: {}; border-radius: 16px; border: 1px solid {};\
         width: 400px; max-width: 90vw; padding: 32px;\
         position: relative; animation: fadeUp 0.3s ease-out;",
        c.bg_elevated, c.border
    );
    let tab_style = |active: bool| {
        format!(
            "padding: 8px 16px; border-radius: 8px; border: none;\
             cursor: pointer; font-size: 14px; font-weight: 500;\
             background: {}; color: {};\
             transition: all 0.2s;",
            if active { c.accent } else { "transparent" },
            if active { "#ffffff" } else { c.text_secondary },
        )
    };
    let btn_style = format!(
        "width: 100%; padding: 12px; border: none; border-radius: 10px;\
         font-size: 15px; font-weight: 600; cursor: pointer;\
         background: {}; color: {};\
         transition: all 0.2s;",
        c.accent, c.btn_text
    );
    let input_style = format!(
        "width: 100%; padding: 12px 14px; border-radius: 10px;\
         border: 1px solid {}; background: {}; color: {};\
         font-size: 15px; outline: none; transition: border 0.2s;",
        c.border, c.bg_input, c.text_primary
    );
    let provider_btn = |name: &str, icon: &str, color: &str| {
        format!(
            "flex: 1; padding: 16px 8px; border: none; border-radius: 12px;\
             cursor: pointer; font-size: 14px; font-weight: 500;\
             background: {}; color: #ffffff;\
             display: flex; flex-direction: column; align-items: center; gap: 8px;\
             transition: all 0.2s;",
            color
        )
    };
    let close_btn_style = format!(
        "position: absolute; top: 12px; right: 16px; border: none;\
         background: none; color: {}; font-size: 20px; cursor: pointer;",
        c.text_muted
    );

    rsx! {
        div {
            style: "{overlay_style}",
            onclick: move |_| user_ctx.close_login(),
            div {
                style: "{modal_style}",
                onclick: move |e| e.stop_propagation(),

                // 关闭按钮
                button {
                    style: "{close_btn_style}",
                    onclick: move |_| user_ctx.close_login(),
                    "✕"
                }

                // 标题
                div { style: "text-align: center; margin-bottom: 24px;",
                    div { style: format!("font-size: 32px; margin-bottom: 8px;"), "🔐" }
                    h2 { style: format!("font-size: 20px; font-weight: 700; color: {}; margin: 0;", c.text_primary), "登录 / 注册" }
                    p { style: format!("font-size: 13px; color: {}; margin-top: 4px;", c.text_muted), "登录后可同步创作记录，体验更多功能" }
                }

                // 错误提示
                if !error_msg.read().is_empty() {
                    div { style: format!("padding: 10px 14px; border-radius: 8px; margin-bottom: 16px;\
                                        background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2);\
                                        font-size: 13px; color: #ef4444;"),
                        "{error_msg}"
                    }
                }

                // 标签栏
                div { style: format!("display: flex; gap: 8px; margin-bottom: 24px; background: {};\
                                    padding: 4px; border-radius: 12px;", c.bg_card),
                    button { style: "{tab_style(active_tab() == \"qq\")}",
                        onclick: move |_| active_tab.set("qq".to_string()),
                        "QQ"
                    }
                    button { style: "{tab_style(active_tab() == \"wechat\")}",
                        onclick: move |_| active_tab.set("wechat".to_string()),
                        "微信"
                    }
                    button { style: "{tab_style(active_tab() == \"alipay\")}",
                        onclick: move |_| active_tab.set("alipay".to_string()),
                        "支付宝"
                    }
                    button { style: "{tab_style(active_tab() == \"sms\")}",
                        onclick: move |_| active_tab.set("sms".to_string()),
                        "手机号"
                    }
                }

                // QQ/微信/支付宝 登录
                if active_tab() == "qq" {
                    div { style: "text-align: center;",
                        div { style: "display: flex; justify-content: center; align-items: center;\
                                     width: 80px; height: 80px; border-radius: 20px;\
                                     background: #12B7F5; margin: 0 auto 16px; font-size: 36px;",
                            "💬"
                        }
                        p { style: format!("font-size: 13px; color: {}; margin-bottom: 20px;", c.text_muted),
                            "点击下方按钮，使用 QQ 账号快速登录"
                        }
                        button {
                            style: "{provider_btn(\"QQ\", \"💬\", \"#12B7F5\")}",
                            disabled: *loading.read(),
                            onclick: move |_| do_oauth_login("qq"),
                            span { style: "font-size: 24px;", "💬" }
                            span { if *loading.read() { "登录中..." } else { "QQ 登录" } }
                        }
                    }
                } else if active_tab() == "wechat" {
                    div { style: "text-align: center;",
                        div { style: "display: flex; justify-content: center; align-items: center;\
                                     width: 80px; height: 80px; border-radius: 20px;\
                                     background: #07C160; margin: 0 auto 16px; font-size: 36px;",
                            "💚"
                        }
                        p { style: format!("font-size: 13px; color: {}; margin-bottom: 20px;", c.text_muted),
                            "点击下方按钮，使用微信账号快速登录"
                        }
                        button {
                            style: "{provider_btn(\"微信\", \"💚\", \"#07C160\")}",
                            disabled: *loading.read(),
                            onclick: move |_| do_oauth_login("wechat"),
                            span { style: "font-size: 24px;", "💚" }
                            span { if *loading.read() { "登录中..." } else { "微信登录" } }
                        }
                    }
                } else if active_tab() == "alipay" {
                    div { style: "text-align: center;",
                        div { style: "display: flex; justify-content: center; align-items: center;\
                                     width: 80px; height: 80px; border-radius: 20px;\
                                     background: #1677FF; margin: 0 auto 16px; font-size: 36px;",
                            "🔵"
                        }
                        p { style: format!("font-size: 13px; color: {}; margin-bottom: 20px;", c.text_muted),
                            "点击下方按钮，使用支付宝账号快速登录"
                        }
                        button {
                            style: "{provider_btn(\"支付宝\", \"🔵\", \"#1677FF\")}",
                            disabled: *loading.read(),
                            onclick: move |_| do_oauth_login("alipay"),
                            span { style: "font-size: 24px;", "🔵" }
                            span { if *loading.read() { "登录中..." } else { "支付宝登录" } }
                        }
                    }
                } else {
                    // SMS 手机号登录
                    div { style: "display: flex; flex-direction: column; gap: 14px;",
                        div { style: "display: flex; gap: 10px; align-items: center;",
                            span { style: format!("font-size: 16px; color: {}; padding: 12px 0;", c.text_secondary), "+86" }
                            input {
                                style: "{input_style}",
                                placeholder: "手机号码",
                                value: "{phone}",
                                maxlength: "11",
                                r#type: "tel",
                                oninput: move |e| phone.set(e.value()),
                            }
                        }
                        div { style: "display: flex; gap: 10px;",
                            input {
                                style: "{input_style}",
                                placeholder: "验证码",
                                value: "{sms_code}",
                                maxlength: "6",
                                r#type: "text",
                                oninput: move |e| sms_code.set(e.value()),
                            }
                            button {
                                style: format!(
                                    "padding: 12px 16px; border-radius: 10px; border: 1px solid {};\
                                     background: {}; color: {}; font-size: 14px; font-weight: 500;\
                                     cursor: {}; white-space: nowrap; transition: all 0.2s;",
                                    c.accent_border,
                                    if countdown() > 0 { c.bg_input } else { c.accent_subtle },
                                    if countdown() > 0 { c.text_muted } else { c.accent },
                                    if countdown() > 0 { "default" } else { "pointer" },
                                ),
                                disabled: countdown() > 0,
                                onclick: move |_| send_sms(),
                                if countdown() > 0 {
                                    "{countdown}s"
                                } else {
                                    "获取验证码"
                                }
                            }
                        }
                        button {
                            style: "{btn_style} margin-top: 4px;",
                            disabled: *loading.read() || phone.read().len() != 11 || sms_code.read().len() < 4,
                            onclick: move |_| do_sms_login(),
                            if *loading.read() { "登录中..." } else { "登录" }
                        }
                    }
                }

                // 底部说明
                div { style: format!("text-align: center; margin-top: 20px; font-size: 12px; color: {};", c.text_subtle),
                    "登录即表示同意", " ",
                    a { href: "#", style: format!("color: {};", c.accent), "服务条款" },
                    " 和 ",
                    a { href: "#", style: format!("color: {};", c.accent), "隐私政策" },
                }
            }
        }
    }
}
