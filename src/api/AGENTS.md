<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# api

## Purpose
Rust HTTP client layer for communicating with the backend FastAPI service. Handles API request construction, serialization, and response parsing.

## Key Files
| File | Description |
|------|-------------|
| `mod.rs` | Module declaration |
| `client.rs` | API client — HTTP methods for animate, task polling, and health endpoints |

## For AI Agents

### Working In This Directory
- Uses `reqwest` for HTTP requests with JSON serialization via `serde`
- API base URL should be configurable (not hardcoded)
- Add new endpoints as methods on the client struct
- Error handling should return typed errors, not raw strings

### Testing Requirements
- `cargo test` compiles and runs unit tests
- Consider mocking the HTTP layer in tests

### Common Patterns
- async functions returning `Result<T, E>` 
- `reqwest::Client` with JSON feature for request/response serialization
- Shared client instance rather than creating new ones per request

## Dependencies

### External
- reqwest 0.12 — HTTP client
- serde / serde_json — serialization

<!-- MANUAL: -->
