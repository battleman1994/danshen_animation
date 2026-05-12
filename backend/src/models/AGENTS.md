<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# models

## Purpose
Pydantic data models and enums shared across the backend. Defines the canonical types for source content, animation requests, tasks, characters, emotions, and user authentication. Used by routes for request validation and by pipeline for structured data exchange.

## Key Files
| File | Description |
|------|-------------|
| `__init__.py` | All model definitions — SourceType, TaskStatus, Character, Emotion, ContentInput, AnimationRequest, AnimationTask, CharacterPreset |
| `user.py` | User models — UserInfo, LoginRequest, OAuthLoginRequest, SMSLoginRequest, AuthResponse, in-memory user/token stores, auth helper functions |

## For AI Agents

### Working In This Directory
- Models use pydantic v2 with `BaseModel` and `Field` validators
- Enums inherit from `str` and `Enum` for JSON serialization
- User models in `user.py` include in-memory stores (`_user_store`, `_token_store`, etc.) marked for DB replacement
- When adding new pipeline stages, add corresponding status values to `TaskStatus`
- Character and Emotion enums are referenced by both routes and pipeline
- Keep models focused on data shape — business logic belongs in pipeline or routes

### Testing Requirements
- Test pydantic validation (required fields, patterns, ranges)
- Test enum serialization/deserialization
- Test auth helper functions (token generation, SMS code verification)

### Common Patterns
- `str, Enum` for API-facing enums (auto-serializes to string in JSON)
- `Field(default_factory=...)` for dynamic defaults (datetime.now)
- `Field(ge=1, le=5)` for numeric constraints
- `Field(pattern=r"...")` for string format validation
- In-memory dicts as placeholder stores with `# 生产环境替换为数据库` comments

## Dependencies

### Internal
- Used by `backend/src/routes/` for request/response types
- Used by `backend/src/pipeline/` for structured data

### External
- pydantic v2 — data validation and serialization

<!-- MANUAL: -->
