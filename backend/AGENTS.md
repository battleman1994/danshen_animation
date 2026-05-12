<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# backend

## Purpose
Python FastAPI backend service that powers the AI video generation pipeline. Accepts animation requests via REST API, processes them through a 5-stage pipeline (extract → adapt → character → voice → compose) using Celery+Redis for async task execution, and serves output videos via static files.

## Key Files
| File | Description |
|------|-------------|
| `pyproject.toml` | Python project manifest with dependencies and tool config (ruff, pytest) |
| `Dockerfile` | Container build inherited from root |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `src/` | Application source code (see `src/AGENTS.md`) |
| `tests/` | Test suite — pytest with asyncio (see `tests/AGENTS.md`) |
| `output/` | Runtime output directory — generated audio, frames, characters, backgrounds, videos |

## For AI Agents

### Working In This Directory
- Python 3.10+ required
- Install: `pip install -e ".[dev]"`
- Run dev server: `uvicorn src.main:app --reload`
- Lint: `ruff check src/`
- Type check: `mypy src/`
- Format: `ruff format src/`
- Config at `src/config.py` uses pydantic-settings (env vars with `DANSHEN_` prefix)

### Testing Requirements
- `pytest` from this directory
- Async tests use `pytest-asyncio` with `asyncio_mode = "auto"`
- Test coverage via `pytest-cov`

### Common Patterns
- FastAPI apps use lifespan context managers
- pydantic v2 models for request/response schemas
- Celery tasks for async pipeline execution
- Route modules registered via `app.include_router()`

## Dependencies

### Internal
- `src/config.py` — configuration loaded by all modules
- `src/pipeline/` — core AI pipeline logic
- `src/routes/` — API endpoint handlers
- `src/models/` — pydantic data models

### External
- FastAPI + uvicorn — web framework
- Celery + Redis — async task queue
- OpenAI SDK — LLM access
- faster-whisper — speech recognition
- yt-dlp — video downloading
- edge-tts — text-to-speech
- MoviePy + Pillow — video/image processing
- boto3 — S3-compatible storage

<!-- MANUAL: -->
