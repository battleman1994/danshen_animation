use dioxus::prelude::*;
use crate::components::types::UserInfo;

/// 用户登录状态
#[derive(Clone, Copy)]
pub struct UseUser {
    pub token: Signal<String>,
    pub user: Signal<Option<UserInfo>>,
    pub show_login: Signal<bool>,
}

impl UseUser {
    /// 是否已登录
    pub fn is_logged_in(&self) -> bool {
        !self.token.read().is_empty() && self.user.read().is_some()
    }

    /// 当前登录用户信息
    pub fn user_info(&self) -> Option<UserInfo> {
        self.user.read().clone()
    }

    /// 设置登录状态
    pub fn set_logged_in(&mut self, token: String, user: UserInfo) {
        self.token.set(token);
        self.user.set(Some(user));
    }

    /// 退出登录
    pub fn logout(&mut self) {
        self.token.set(String::new());
        self.user.set(None);
    }

    /// 显示登录弹窗
    pub fn open_login(&mut self) {
        self.show_login.set(true);
    }

    /// 隐藏登录弹窗
    pub fn close_login(&mut self) {
        self.show_login.set(false);
    }
}

pub fn use_user_provider() -> UseUser {
    let ctx = UseUser {
        token: use_signal(String::new),
        user: use_signal(|| None::<UserInfo>),
        show_login: use_signal(|| false),
    };
    use_context_provider(|| ctx);
    ctx
}

pub fn use_user() -> UseUser {
    use_context::<UseUser>()
}
