//! Danshen Animation — macOS + Windows + Web cross-platform app (Dioxus 0.5)
#![cfg_attr(feature = "desktop", windows_subsystem = "windows")]

mod app;
mod api;
mod components;
mod config;
mod hooks;
mod styles;

use app::App;
use dioxus::prelude::LaunchBuilder;

fn main() {
    dioxus_logger::init(dioxus_logger::tracing::Level::INFO).expect("failed to init logger");

    #[cfg(feature = "desktop")]
    {
        use dioxus::desktop::{Config, LogicalSize, WindowBuilder};
        let window = WindowBuilder::new()
            .with_title("🔥 蛋神动画 — Danshen Animation")
            .with_min_inner_size(LogicalSize::new(600.0, 700.0))
            .with_inner_size(LogicalSize::new(800.0, 900.0));
        LaunchBuilder::desktop().with_cfg(Config::new().with_window(window)).launch(App);
    }

    #[cfg(feature = "web")]
    {
        LaunchBuilder::web().launch(App);
    }
}
