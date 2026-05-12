<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# components

## Purpose
Dioxus UI component library. Each component handles a specific part of the animation submission UI — source input, character selection, style picking, progress tracking, and result display. Also includes the logo, header, footer, and user authentication modals.

## Key Files
| File | Description |
|------|-------------|
| `mod.rs` | Module declarations and re-exports |
| `types.rs` | Shared component types, enums, and prop structures |
| `constants.rs` | UI constants — labels, default values, character options |
| `source_input.rs` | URL/text input field for content submission |
| `scene_selector.rs` | Scene type picker (dialogue, news, meme, etc.) |
| `character_grid.rs` | Character selection grid — animal avatar picker |
| `style_selector.rs` | Animation style selector (funny, serious, cute, etc.) |
| `submit_button.rs` | Submit button with loading state |
| `progress_bar.rs` | Progress indicator during animation generation |
| `result_card.rs` | Completed animation result display with video player |
| `news_mode_hint.rs` | Contextual hint shown when news scene is selected |
| `config_modal.rs` | Configuration/settings modal |
| `logo.rs` | Anime-style SVG logo component |
| `header.rs` | App header with title and navigation |
| `footer.rs` | App footer |
| `decorative_blobs.rs` | Decorative background elements |
| `user.rs` | User profile display and menu |
| `user/` | User auth subcomponents — login modal, user state |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `user/` | User authentication UI — login modal, user state management |

## For AI Agents

### Working In This Directory
- All components use `#[component]` macro from Dioxus 0.5
- Markup is written in `rsx! {}` macro
- New components must be declared in `mod.rs`
- Shared types and props go in `types.rs`, not duplicated across components
- UI constants (character names, style labels, etc.) belong in `constants.rs`
- Components should be self-contained — one component per file
- Props are passed as Rust struct fields with `#[props]` attributes

### Testing Requirements
- `cargo test` compiles all component code
- Visual testing is manual — run `cargo run` to verify UI

### Common Patterns
- `use_signal` for local component state
- `use_effect` for side effects (API calls, timers)
- Inline styles via Dioxus `style` attribute with Rust values from `styles/theme.rs`
- Conditional rendering with `if` expressions inside `rsx!`

## Dependencies

### Internal
- `src/styles/` — theme colors, typography, spacing
- `src/hooks/` — shared animation state hook
- `src/api/` — backend communication

### External
- Dioxus 0.5 — component framework (html, macro, hooks, signals features)

<!-- MANUAL: -->
