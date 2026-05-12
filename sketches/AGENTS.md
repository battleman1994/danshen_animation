<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# sketches

## Purpose
Static HTML/CSS UI design mockups for previewing and validating visual design before implementation. Two complete design systems represented as standalone HTML previews.

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `001-linear-dark/` | Dark theme inspired by Linear.app — black background, indigo-purple accents, tech-minimal aesthetic |
| `002-claude-warm/` | Warm theme inspired by Claude AI — parchment background, terracotta accents, warm and human feel |

## For AI Agents

### Working In This Directory
- These are static HTML previews only — not part of the application build
- Used as visual reference when implementing the Rust/Dioxus theme system in `src/styles/`
- The desktop app defaults to the dark Linear theme; warm Claude theme is available via toggle
- Do not modify these files directly — they are design artifacts; implement changes in the Rust theme system instead

### Testing Requirements
- No automated tests apply

### Common Patterns
- Each sketch is a self-contained HTML file with inline CSS
- No JavaScript frameworks — pure HTML+CSS for maximum portability
- Both sketches should render the same content with different visual treatments for comparison

<!-- MANUAL: -->
