<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-12 | Updated: 2026-05-12 -->

# docs

## Purpose
Project documentation covering architecture, design system, and development plans. These documents define the technical vision and implementation roadmap.

## Key Files
| File | Description |
|------|-------------|
| `architecture.md` | System architecture — architecture diagrams, data flow, API design, tech stack rationale |
| `design.md` | UI/UX design system — colors, typography, spacing, component specs for both themes |
| `plan.md` | Development roadmap with phased milestones and feature checklist |

## For AI Agents

### Working In This Directory
- These are reference documents, not executable code
- When implementing features, cross-reference architecture.md for API contracts and pipeline design
- design.md defines the visual language — use it when building UI components
- plan.md tracks project milestones — update when phases complete

### Testing Requirements
- No tests apply to documentation files

### Common Patterns
- Documents use Chinese (primary) with English technical terms
- Architecture diagrams use ASCII box-drawing characters

## Dependencies

### Internal
- Mirrors `backend/src/` structure described in architecture.md
- References UI components in `src/components/`

<!-- MANUAL: -->
