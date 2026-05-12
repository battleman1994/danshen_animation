<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# hooks

## Purpose
Custom Dioxus hooks for shared, reusable state logic. The primary hook manages the full animation submission lifecycle — form state, API call, progress tracking, and result handling.

## Key Files
| File | Description |
|------|-------------|
| `mod.rs` | Module declaration |
| `use_animation.rs` | Main animation hook — form state, submission, polling, result management |

## For AI Agents

### Working In This Directory
- Hooks follow the `use_` naming convention (Dioxus convention matching React patterns)
- Hooks should be pure state management — no direct DOM manipulation
- State is exposed via Dioxus `Signal` types for reactive updates
- New shared logic that spans multiple components belongs here

### Testing Requirements
- `cargo test` verifies compilation
- Complex state transitions should have unit tests

### Common Patterns
- Builder pattern for constructing API requests from form state
- State machine pattern for animation lifecycle (idle → submitting → processing → done → error)
- `use_signal` + `use_effect` for reactive state changes

## Dependencies

### Internal
- `src/api/` — API client for backend calls
- `src/components/types.rs` — shared type definitions

### External
- Dioxus 0.5 — hooks, signals

<!-- MANUAL: -->
