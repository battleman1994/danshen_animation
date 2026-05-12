<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# routes

## Purpose
FastAPI route handlers organized by domain. Each module defines its own `APIRouter` with prefix and tags. Routers are registered in `main.py` via `app.include_router()`.

## Key Files
| File | Description |
|------|-------------|
| `__init__.py` | Module re-exports — animate, tasks, auth, admin |
| `animate.py` | POST `/api/v1/animate` — submit animation request, background task processing, provider/model listing |
| `tasks.py` | GET `/api/v1/tasks/{task_id}` — poll task status, progress, and results |
| `auth.py` | OAuth and SMS authentication endpoints — login, callback, token verification |
| `admin.py` | Admin dashboard endpoints — model management, system config, health (skeleton) |

## For AI Agents

### Working In This Directory
- Each route file uses `APIRouter(prefix=..., tags=[...])` for self-contained routing
- New route modules must be imported in `__init__.py` and registered in `main.py`
- The animate route submits work via `BackgroundTasks` (not Celery in the current implementation)
- Task state is stored in-memory (`_task_store` dict) — production should use Redis/DB
- Request validation uses pydantic models with `Field` constraints (patterns, min/max)
- Auth routes currently use demo/mock implementations — real OAuth requires provider secrets
- Admin routes are skeleton/placeholder for future management features

### Testing Requirements
- Test HTTP status codes, response shapes, and error cases
- Mock pipeline calls in animate tests
- Test auth flow: request code → login → token verification

### Common Patterns
- `router = APIRouter(prefix="/...", tags=["..."])` at module level
- `@router.get/post` decorators for endpoint handlers
- Response models via pydantic `BaseModel`
- Background task processing via FastAPI `BackgroundTasks`

## Dependencies

### Internal
- `backend/src/pipeline/` — core processing invoked by animate route
- `backend/src/models/` — shared types and enums
- `backend/src/config.py` — settings access

### External
- FastAPI — router, background tasks, HTTP exception handling

<!-- MANUAL: -->
