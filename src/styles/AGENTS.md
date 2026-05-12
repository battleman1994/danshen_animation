<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# styles

## Purpose
Theme system and CSS utilities for the Dioxus desktop app. Defines two complete visual themes (dark Linear-style and warm Claude-style) with type-safe Rust enums, plus Tailwind-like utility CSS classes for layout and typography.

## Key Files
| File | Description |
|------|-------------|
| `mod.rs` | Module declaration |
| `theme.rs` | Dual theme system — Rust enums for colors, typography, spacing; theme context provider |
| `tailwind.css` | Utility CSS classes — layout, flex, spacing, typography helpers |

## For AI Agents

### Working In This Directory
- Theme values are Rust constants/enums, not CSS variables — they're applied as inline styles
- Both themes must be kept visually consistent: adding a color to one theme requires the equivalent in the other
- `tailwind.css` provides layout utilities only, not colors (colors come from the Rust theme)
- Theme switching is handled in `app.rs` via a signal
- When adding new UI elements, use theme values rather than hardcoded colors

### Testing Requirements
- `cargo test` verifies compilation
- Visual verification: run `cargo run` and toggle themes

### Common Patterns
- `Theme` enum with `Dark` and `Warm` variants
- Theme structs contain palette, typography scale, spacing scale
- Components access theme via Dioxus context or prop drilling
- CSS file is minimal — most styling is programmatic via Rust

## Dependencies

### Internal
- Used by all components in `src/components/`
- Theme switch controlled by `src/app.rs`

### External
- Dioxus 0.5 — style attribute support

<!-- MANUAL: -->
