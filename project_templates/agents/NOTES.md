# Notes on Corrections (v1)

## What was corrected
- Updated `/agents/README.md` to reference actual files in this package (removed stale `v6_short` references).
- Split the library into `agents/IA/` and `agents/OA/`:
  - OA-only: Windows ZIP handling + OA master prompt + governance.
  - IA-only: implementation rules, packaging, testing, fail conditions, prompt templates.
- Renamed `99_IA_PROMPT_TEMPLATE.md` → `agents/IA/02_IA_PROMPT_TEMPLATE.md` for clearer ordering.
- Rewrote the agent instruction governance doc to align with the Team Topminds playbook.

## Intentionally not included
- Repo-root files like `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` belong at repo root (governed by OA).
