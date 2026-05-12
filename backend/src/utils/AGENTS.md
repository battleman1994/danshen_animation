<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# utils

## Purpose
Small, pure utility functions with no internal dependencies. Provides hashing, text cleaning, filesystem helpers, and duration formatting. These functions are used across the backend but have no business logic of their own.

## Key Files
| File | Description |
|------|-------------|
| `__init__.py` | All utilities — hash_source, clean_text, ensure_dir, format_duration |

## For AI Agents

### Working In This Directory
- Keep functions pure and side-effect-free where possible
- `hash_source` uses MD5 (acceptable for cache keys, not for security)
- `ensure_dir` is the filesystem exception — idempotent directory creation
- New utilities should be small (<20 lines) and genuinely shared across modules
- If a function is only used by one module, keep it there — don't prematurely extract to utils

### Testing Requirements
- Test edge cases: empty strings, special characters, missing directories
- Test `hash_source` determinism
- Test `format_duration` for sub-minute, exact-minute, and hour+ durations

### Common Patterns
- Pure functions with type hints
- No class definitions — just functions
- `Optional` return types where appropriate

## Dependencies

### Internal
- None (this is the leaf module)

### External
- Only Python stdlib (hashlib, re, pathlib)

<!-- MANUAL: -->
