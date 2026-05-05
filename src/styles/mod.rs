/// Styles module — CSS is embedded via include_str! for desktop builds
pub mod theme;
pub const STYLE_CSS: &str = include_str!("tailwind.css");
