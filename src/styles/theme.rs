use dioxus::prelude::*;

/// 扩展只需新增变体 + 对应的 ThemeValues
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Theme {
    LinearDark,
    ClaudeWarm,
}

impl Theme {
    pub fn label(&self) -> &'static str {
        match self { Self::LinearDark => "暗色极简", Self::ClaudeWarm => "暖色编辑" }
    }
    pub fn icon(&self) -> &'static str {
        match self { Self::LinearDark => "🌙", Self::ClaudeWarm => "☀️" }
    }
    pub fn next(self) -> Self {
        match self { Self::LinearDark => Self::ClaudeWarm, Self::ClaudeWarm => Self::LinearDark }
    }
}

/// 主题所有颜色值 — 组件直接引用这些字段
#[allow(dead_code)]
pub struct ThemeColors {
    /* Background */
    pub bg_page: &'static str,
    pub bg_card: &'static str,
    pub bg_input: &'static str,
    pub bg_elevated: &'static str,
    /* Text */
    pub text_primary: &'static str,
    pub text_secondary: &'static str,
    pub text_muted: &'static str,
    pub text_subtle: &'static str,
    /* Accent */
    pub accent: &'static str,
    pub accent_hover: &'static str,
    pub accent_subtle: &'static str,
    pub accent_border: &'static str,
    /* Borders */
    pub border: &'static str,
    pub border_subtle: &'static str,
    /* Header badge */
    pub badge_bg: &'static str,
    pub badge_text: &'static str,
    pub badge_border: &'static str,
    /* Pills */
    pub pill_bg: &'static str,
    pub pill_text: &'static str,
    pub pill_border: &'static str,
    pub pill_active_bg: &'static str,
    pub pill_active_text: &'static str,
    /* Scene cards */
    pub scene_card_bg: &'static str,
    pub scene_card_border: &'static str,
    pub scene_active_bg: &'static str,
    pub scene_active_border: &'static str,
    /* Buttons */
    pub btn_bg: &'static str,
    pub btn_text: &'static str,
    pub btn_hover: &'static str,
    pub btn_loading_bg: &'static str,
    pub btn_loading_text: &'static str,
    /* Progress */
    pub progress_track: &'static str,
    pub progress_fill: &'static str,
    pub progress_text: &'static str,
    /* Result */
    pub result_bg: &'static str,
    pub result_border: &'static str,
    /* misc */
    pub footer_border: &'static str,
    pub hint_bg: &'static str,
    pub hint_border: &'static str,
    pub hint_text: &'static str,
    pub count_btn_bg: &'static str,
    pub count_btn_text: &'static str,
    /* Radius */
    pub radius_sm: &'static str,
    pub radius_md: &'static str,
    pub radius_lg: &'static str,
    pub radius_pill: &'static str,
    /* Title gradient */
    pub title_gradient: &'static str,
}

/// 获取主题对应的颜色值
pub fn get_theme_colors(theme: Theme) -> &'static ThemeColors {
    match theme {
        Theme::LinearDark => &LINEAR_DARK,
        Theme::ClaudeWarm => &CLAUDE_WARM,
    }
}

static LINEAR_DARK: ThemeColors = ThemeColors {
    bg_page: "#08090a",
    bg_card: "rgba(255,255,255,0.02)",
    bg_input: "rgba(255,255,255,0.02)",
    bg_elevated: "#0f1011",
    text_primary: "#f7f8f8",
    text_secondary: "#d0d6e0",
    text_muted: "#8a8f98",
    text_subtle: "#62666d",
    accent: "#5e6ad2",
    accent_hover: "#7170ff",
    accent_subtle: "rgba(94,106,210,0.08)",
    accent_border: "#5e6ad2",
    border: "rgba(255,255,255,0.08)",
    border_subtle: "rgba(255,255,255,0.05)",
    badge_bg: "rgba(255,255,255,0.04)",
    badge_text: "#8a8f98",
    badge_border: "rgba(255,255,255,0.08)",
    pill_bg: "rgba(255,255,255,0.03)",
    pill_text: "#8a8f98",
    pill_border: "rgba(255,255,255,0.08)",
    pill_active_bg: "#5e6ad2",
    pill_active_text: "#ffffff",
    scene_card_bg: "rgba(255,255,255,0.02)",
    scene_card_border: "rgba(255,255,255,0.08)",
    scene_active_bg: "rgba(94,106,210,0.08)",
    scene_active_border: "#5e6ad2",
    btn_bg: "#5e6ad2",
    btn_text: "#ffffff",
    btn_hover: "#7170ff",
    btn_loading_bg: "rgba(255,255,255,0.05)",
    btn_loading_text: "#8a8f98",
    progress_track: "rgba(255,255,255,0.06)",
    progress_fill: "#5e6ad2",
    progress_text: "#62666d",
    result_bg: "rgba(255,255,255,0.02)",
    result_border: "rgba(255,255,255,0.08)",
    footer_border: "rgba(255,255,255,0.05)",
    hint_bg: "rgba(94,106,210,0.06)",
    hint_border: "rgba(94,106,210,0.15)",
    hint_text: "#8a8f98",
    count_btn_bg: "rgba(255,255,255,0.03)",
    count_btn_text: "#d0d6e0",
    radius_sm: "6px",
    radius_md: "8px",
    radius_lg: "12px",
    radius_pill: "9999px",
    title_gradient: "linear-gradient(135deg, #f7f8f8 0%, #8a8f98 100%)",
};

static CLAUDE_WARM: ThemeColors = ThemeColors {
    bg_page: "#f5f4ed",
    bg_card: "#faf9f5",
    bg_input: "#faf9f5",
    bg_elevated: "#ffffff",
    text_primary: "#141413",
    text_secondary: "#5e5d59",
    text_muted: "#87867f",
    text_subtle: "#b0aea5",
    accent: "#c96442",
    accent_hover: "#d97757",
    accent_subtle: "rgba(201,100,66,0.06)",
    accent_border: "#c96442",
    border: "#f0eee6",
    border_subtle: "#e8e6dc",
    badge_bg: "#e8e6dc",
    badge_text: "#5e5d59",
    badge_border: "transparent",
    pill_bg: "#e8e6dc",
    pill_text: "#4d4c48",
    pill_border: "transparent",
    pill_active_bg: "#c96442",
    pill_active_text: "#faf9f5",
    scene_card_bg: "#faf9f5",
    scene_card_border: "#f0eee6",
    scene_active_bg: "#ffffff",
    scene_active_border: "#c96442",
    btn_bg: "#c96442",
    btn_text: "#faf9f5",
    btn_hover: "#d97757",
    btn_loading_bg: "#e8e6dc",
    btn_loading_text: "#87867f",
    progress_track: "#e8e6dc",
    progress_fill: "#c96442",
    progress_text: "#87867f",
    result_bg: "#faf9f5",
    result_border: "#e8e6dc",
    footer_border: "#e8e6dc",
    hint_bg: "#faf9f5",
    hint_border: "#e8e6dc",
    hint_text: "#5e5d59",
    count_btn_bg: "#e8e6dc",
    count_btn_text: "#4d4c48",
    radius_sm: "8px",
    radius_md: "10px",
    radius_lg: "12px",
    radius_pill: "9999px",
    title_gradient: "linear-gradient(135deg, #141413 0%, #5e5d59 100%)",
};

/// 主题 Context
#[derive(Clone, Copy)]
pub struct ThemeCtx {
    pub theme: Signal<Theme>,
}

impl ThemeCtx {
    pub fn toggle(&mut self) {
        let current = *self.theme.read();
        self.theme.set(current.next());
    }
    pub fn colors(&self) -> &'static ThemeColors {
        get_theme_colors(*self.theme.read())
    }
}

pub fn use_theme_provider() -> ThemeCtx {
    let ctx = ThemeCtx { theme: use_signal(|| Theme::LinearDark) };
    use_context_provider(|| ctx);
    ctx
}

pub fn use_theme() -> ThemeCtx {
    use_context::<ThemeCtx>()
}
