<!-- Parent: ../src/AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# backend/tests

## Purpose
Pytest test suite for the backend. Tests cover configuration, pipeline stages, and API routes with async support via pytest-asyncio.

## Key Files
| File | Description |
|------|-------------|
| `__init__.py` | Package marker |
| `conftest.py` | Shared pytest fixtures and configuration |
| `test_config.py` | Configuration loading tests |
| `test_adapter_v2.py` | Script adapter pipeline stage tests |
| `test_dialogue_analyzer.py` | Dialogue analysis unit tests |
| `test_news_analyzer.py` | News content analysis unit tests |
| `test_prompt_builder.py` | LLM prompt construction tests |
| `test_storyboard.py` | Storyboard generation tests |

## For AI Agents

### Working In This Directory
- Run all tests: `pytest` from `backend/`
- Run single file: `pytest tests/test_config.py`
- Async tests use `pytest-asyncio` with `asyncio_mode = "auto"` configured in pyproject.toml
- Fixtures go in `conftest.py` at this level
- Test file naming: `test_<module>.py` matching the source module under test

### Testing Requirements
- All new pipeline features must have corresponding tests
- Mock external APIs (OpenAI, Whisper, etc.) — do not call real services
- Test both happy path and error cases

### Common Patterns
- pytest fixtures for shared test data
- `@pytest.mark.asyncio` for async tests (though asyncio_mode=auto handles this)
- Mock via `unittest.mock` or pytest-mock

## Dependencies

### Internal
- Tests `backend/src/` modules directly

### External
- pytest, pytest-asyncio, pytest-cov

<!-- MANUAL: -->
