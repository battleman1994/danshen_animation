<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# danshen_animation — 蛋神动画

## Purpose
AI-powered anime-style video generator. Users submit content (video URLs, text, images, news links) and the system produces anime-style videos featuring cute animal characters with dubbed voiceovers. Cross-platform desktop app (Rust/Dioxus) with a Python/FastAPI backend pipeline.

## Key Files
| File | Description |
|------|-------------|
| `Cargo.toml` | Rust workspace manifest — Dioxus 0.5 desktop/web app |
| `README.md` | Project overview with architecture diagrams and quickstart |
| `Dockerfile` | Container build for the backend service |
| `docker-compose.yml` | Multi-service orchestration (backend, Redis, MinIO) |
| `index.html` | Web entry point for the Dioxus web build |
| `.gitignore` | Git ignore rules |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `src/` | Rust + Dioxus desktop client (see `src/AGENTS.md`) |
| `backend/` | Python FastAPI backend + AI pipeline (see `backend/AGENTS.md`) |
| `docs/` | Architecture, design, and planning documents (see `docs/AGENTS.md`) |
| `sketches/` | UI design mockups in HTML (see `sketches/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- This is a dual-language project: Rust (frontend) and Python (backend)
- Frontend: `cargo build`, `cargo run`, `cargo test`, `cargo clippy`
- Backend: `cd backend && pip install -e ".[dev]" && uvicorn src.main:app`
- The two halves are independent — changes to one rarely affect the other
- The `.gstack/` directory is gstack browser automation state (ignore)

### Testing Requirements
- Frontend: `cargo test` from project root
- Backend: `cd backend && pytest` 
- Both must pass before merging

### Common Patterns
- Rust frontend uses Dioxus 0.5 hooks and signals for state management
- Python backend uses FastAPI with async endpoints and Celery for background tasks
- Dual theme system: dark Linear-style and warm Claude-style

## Dependencies

### External
- Rust: Dioxus 0.5, reqwest, serde, tokio
- Python: FastAPI, Celery+Redis, OpenAI, faster-whisper, yt-dlp, edge-tts, MoviePy, boto3

<!-- MANUAL: -->
