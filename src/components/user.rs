use dioxus::prelude::*;
use crate::styles::theme::use_theme;

/// 登录方式
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LoginMethod {
    QQ,
    WeChat,
    Alipay,
    Phone,
}

impl LoginMethod {
    pub fn label(&self) -> &'static str {
        match self {
            Self::QQ => "QQ",
            Self::WeChat => "微信",
            Self::Alipay => "支付宝",
            Self::Phone => "手机号",
        }
    }
    pub fn icon(&self) -> &'static str {
        match self {
            Self::QQ => "🐧",
            Self::WeChat => "💬",
            Self::Alipay => "💳",
            Self::Phone => "📱",
        }
    }
    pub fn color(&self) -> &'static str {
        match self {
            Self::QQ => "#12b7f5",
            Self::WeChat => "#07c160",
            Self::Alipay => "#1677ff",
            Self::Phone => "#8b5cf6",
        }
    }
}

// ── 子模块导出（必须在任何 pub use 之前） ──
pub mod user_state;
pub mod login_modal;

// ── 重新导出方便外部引用 ──
pub use user_state::{UseUser, use_user_provider, use_user};
pub use login_modal::LoginModal;

/// 默认头像占位（根据登录方式显示图标）
fn default_avatar_emoji(method: Option<LoginMethod>) -> &'static str {
    match method {
        Some(LoginMethod::QQ) => "🐧",
        Some(LoginMethod::WeChat) => "💬",
        Some(LoginMethod::Alipay) => "💳",
        Some(LoginMethod::Phone) => "📱",
        None => "👤",
    }
}

/// ============================================================
/// 用户头像显示组件
/// ============================================================
#[component]
pub fn UserDisplay() -> Element {
    let mut user_ctx = use_user();
    let c = use_theme().colors();
    let logged_in = user_ctx.is_logged_in();

    if !logged_in {
        return rsx! {};
    }

    let info = user_ctx.user_info().unwrap();
    let method = match info.provider.as_str() {
        "qq" => LoginMethod::QQ,
        "wechat" => LoginMethod::WeChat,
        "alipay" => LoginMethod::Alipay,
        _ => LoginMethod::Phone,
    };

    rsx! {
        div {
            style: "display: flex; align-items: center; gap: 8px; position: relative;",

            // 头像
            div {
                style: "width: 32px; height: 32px; border-radius: 9999px; \
                        display: flex; align-items: center; justify-content: center; \
                        font-size: 14px; overflow: hidden; \
                        background: {c.badge_bg}; border: 1px solid {c.border};",
                if info.avatar_url.is_empty() {
                    span { "{default_avatar_emoji(Some(method))}" }
                } else {
                    img {
                        src: "{info.avatar_url}",
                        style: "width: 100%; height: 100%; object-fit: cover;",
                        alt: "avatar"
                    }
                }
            }

            // 昵称 + 登录方式
            div { style: "text-align: left;",
                div { style: "font-size: 14px; font-weight: 500; color: {c.text_primary};", "{info.nickname}" }
                div { style: "font-size: 10px; color: {c.text_muted};", "{method.label()} 登录" }
            }

            // 退出按钮
            button {
                style: "position: absolute; top: -4px; right: -4px; width: 16px; height: 16px; \
                        border-radius: 9999px; display: flex; align-items: center; \
                        justify-content: center; font-size: 10px; opacity: 0; \
                        background: {c.accent}; color: #fff; cursor: pointer; border: none;",
                onclick: move |_| {
                    let mut ctx = user_ctx;
                    ctx.logout();
                },
                title: "退出登录",
                "×"
            }
        }
    }
}

/// ============================================================
/// 登录/用户状态栏（挂在 Header 区域顶部）
/// ============================================================
#[component]
pub fn AuthBar() -> Element {
    let mut user_ctx = use_user();
    let c = use_theme().colors();

    let badge_s = format!(
        "background: {}; color: {}; border: 1px solid {}; border-radius: {}; \
         cursor: pointer; display: inline-flex; align-items: center; gap: 6px; \
         padding: 6px 12px; font-size: 14px; font-weight: 500;",
        c.badge_bg, c.badge_text, c.badge_border, c.radius_pill,
    );

    rsx! {
        div { style: "display: flex; align-items: center; gap: 8px;",
            if user_ctx.is_logged_in() {
                UserDisplay {}
            } else {
                button {
                    style: "{badge_s}",
                    onclick: move |_| user_ctx.open_login(),
                    span { "👤" }
                    span { "登录" }
                }
            }
        }

        // 登录模态框
        LoginModal {}
    }
}
