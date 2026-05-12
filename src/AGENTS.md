<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# src (Rust Frontend)

## Purpose
Cross-platform desktop/web client built with Rust and Dioxus 0.5. Provides the UI for submitting animation requests — source input, character selection, style picking — and displays results. Supports dual themes (dark Linear-style / warm Claude-style) and compiles to native macOS/Windows or WebAssembly.

## Key Files
| File | Description |
|------|-------------|
| `main.rs` | Entry point — initializes logger, configures window, launches App component |
| `app.rs` | Root App component — theme switching, layout, and top-level state |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `api/` | Backend API client (see `api/AGENTS.md`) |
| `components/` | UI component library (see `components/AGENTS.md`) |
| `config/` | Local configuration management (see `config/AGENTS.md`) |
| `hooks/` | Custom Dioxus hooks for shared state (see `hooks/AGENTS.md`) |
| `styles/` | Theme system and CSS utilities (see `styles/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- Rust edition 2021, Dioxus 0.5
- Build: `cargo build`
- Run desktop: `cargo run` (default feature "desktop")
- Run web: `cargo run --features web`
- Lint: `cargo clippy`
- The `desktop` feature enables native windowing; `web` targets wasm32
- Release builds optimize for size (`opt-level = "z"`, `lto = true`)

### Testing Requirements
- `cargo test` from project root
- Both desktop and web feature configurations must compile

### Common Patterns
- Dioxus components use the `#[component]` macro with `rsx!` macro for markup
- State management via Dioxus `use_signal` and custom hooks
- Theme system uses Rust enums for type-safe theme variants
- Components are organized as individual `.rs` files with a `mod.rs` barrel

## Dependencies

### Internal
- `api/` — depends on backend API availability
- `components/` — consumed by `app.rs`
- `hooks/` — used by components for shared state
- `styles/` — consumed by all visual components

### External
- Dioxus 0.5 — reactive UI framework
- reqwest — HTTP client for API calls
- serde / serde_json — serialization
- tokio — async runtime (desktop only)

<!-- MANUAL: -->
