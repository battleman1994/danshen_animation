<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# pipeline

## Purpose
The core AI video generation pipeline. Takes raw content (text, video URLs, news links) and transforms it through multiple stages into an anime-style video with animal characters. Exports all major classes and providers through `__init__.py`.

## Key Files
| File | Description |
|------|-------------|
| `__init__.py` | Barrel exports — PromptBuilder, VideoGenProvider variants, ContentExtractor, NewsAnalyzer, DialogueAnalyzer |
| `extractor.py` | Content extraction — downloads videos (yt-dlp), transcribes audio (Whisper), scrapes web pages, OCR images |
| `adapter.py` | Script adaptation — rewrites extracted content into anime-character dialogue scripts |
| `character.py` | Character generation — LLM-designed animal characters, ComfyUI/SD image generation, expression mapping |
| `voice.py` | Voice synthesis — emotion detection, voice selection, TTS generation, audio post-processing |
| `composer.py` | Video composition — scene planning, lip-sync, background gen, subtitle overlay, FFmpeg encoding |
| `prompt_builder.py` | LLM prompt construction — builds structured prompts for video generation from content + character + style |
| `video_gen.py` | Video generation providers — MockProvider, KlingProvider, RunwayProvider, JimengProvider, HailuoProvider |
| `storyboard.py` | Storyboard/scene planning — breaks scripts into visual scenes |
| `dialogue_analyzer.py` | Dialogue-specific analysis — speaker identification, emotion mapping, turn-taking |
| `news_analyzer.py` | News content analysis — severity classification, animal anchor selection, news-style adaptation |

## For AI Agents

### Working In This Directory
- This is the heart of the application — changes here affect video output quality
- All new pipeline stages must be exported in `__init__.py`
- Pipeline stages are chained: extractor → adapter/storyboard → character → voice → composer
- `prompt_builder.py` + `video_gen.py` form a newer, simplified path: content → LLM prompt → video API
- Each stage has its own LLM calls and can fail independently — handle errors gracefully
- External API calls (OpenAI, Whisper, TTS) must have timeouts and retry logic
- The `video_gen.py` providers follow a plugin pattern with `register()` and `get_provider()`

### Testing Requirements
- Tests in `backend/tests/` — `test_adapter_v2.py`, `test_prompt_builder.py`, `test_storyboard.py`, etc.
- Mock all external API calls in tests
- Test prompt templates for correctness and parameterization
- Test provider registry and fallback behavior

### Common Patterns
- Async methods for I/O-bound operations (API calls, downloads)
- Provider pattern for swappable backends (video generation, LLM)
- Enum-based configuration (characters, emotions, styles, scenes)
- Pydantic models for structured outputs from each pipeline stage

## Dependencies

### Internal
- `backend/src/config.py` — API keys, model selections, output paths
- `backend/src/models/` — shared enums (Character, Emotion, SourceType, TaskStatus)

### External
- OpenAI SDK — LLM prompting
- faster-whisper — speech-to-text
- yt-dlp — video downloading
- edge-tts — text-to-speech
- MoviePy + Pillow — media processing
- trafilatura — web scraping

<!-- MANUAL: -->
