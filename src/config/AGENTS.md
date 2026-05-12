<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# config

## Purpose
Local configuration management for the Rust desktop client. Handles persisting and loading user settings (API endpoint, theme preference, default options) to local storage.

## Key Files
| File | Description |
|------|-------------|
| `mod.rs` | Module declaration |
| `local_config.rs` | Config struct, load/save to local storage, default values |

## For AI Agents

### Working In This Directory
- Config is persisted to the platform's local storage (not env vars — that's the backend pattern)
- Use `serde` for serialization of config values
- New config fields should have sensible defaults
- Config changes should propagate to components via Dioxus signals or context

### Testing Requirements
- `cargo test` verifies compilation
- Test default config values and serialization round-trips

### Common Patterns
- Struct with derived `Serialize, Deserialize, Clone`
- `Default` trait implementation for fallback values
- Load on app startup, save on change

## Dependencies

### External
- serde — serialization
- web-sys / wasm-bindgen — local storage access (web target)

<!-- MANUAL: -->
