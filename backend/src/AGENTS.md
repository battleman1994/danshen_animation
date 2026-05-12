<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# backend/src

## Purpose
Core application source for the FastAPI backend. Contains the API entry point, configuration, data models, route handlers, pipeline logic, Celery worker, and utility functions.

## Key Files
| File | Description |
|------|-------------|
| `main.py` | FastAPI app factory — lifespan, CORS, static files mount, router registration |
| `config.py` | pydantic-settings configuration — env vars with `DANSHEN_` prefix |
| `worker.py` | Celery worker entry — task definitions for async pipeline execution |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `pipeline/` | AI video generation pipeline (5 stages) (see `pipeline/AGENTS.md`) |
| `routes/` | API route handlers (see `routes/AGENTS.md`) |
| `models/` | pydantic data models (see `models/AGENTS.md`) |
| `utils/` | Shared utility functions (see `utils/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- All imports use relative paths (e.g., `from .config import settings`)
- Config is loaded once via `config.py` and imported by all modules
- New routes must be registered in `main.py` via `app.include_router()`
- Pipeline stages should be added to `pipeline/__init__.py` exports
- Worker tasks are defined in `worker.py` and imported by routes that need async processing

### Testing Requirements
- Tests in `backend/tests/` mirror the source structure
- Test config settings in `conftest.py`

### Common Patterns
- FastAPI routers use `APIRouter(prefix=..., tags=[...])`
- pydantic v2 models with `model_config = ConfigDict(...)` 
- Async endpoint handlers for I/O-bound operations
- Celery tasks for CPU-bound pipeline work

## Dependencies

### Internal
- `config.py` — required by nearly all modules
- `pipeline/` — used by worker.py and animate route

### External
- FastAPI — web framework
- Celery — task queue
- pydantic / pydantic-settings — data validation and config

<!-- MANUAL: -->
