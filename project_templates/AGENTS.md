# AGENTS.md

This repository is developed using the **PO ↔ OA ↔ IA** workflow.

## Sources of truth
- **PRD:** `docs/PRD/PRD.md`
- **SoT (index):** `docs/SoT/00_index.md`
- **Repo rails (anti-monolith):** `docs/SoT/20_repo_layout.md`
- **Implementation Plan:** `docs/implementation/PLAN.md`

## `/agents` — agent library
All generic rules and prompt templates live in:
- **IA (Implementation Agent):** `agents/IA/`
- **OA (Orchestration Agent):** `agents/OA/`

Entry points:
- `agents/IA/01_IA_PROMPT_GENERIC.md`
- `agents/IA/02_IA_PROMPT_TEMPLATE.md`
- `agents/OA/00_AO_MASTER_PROMPT.md`

## File size limits (anti-monolith)
See `docs/SoT/20_repo_layout.md`.
- **SOFT limit:** 600 lines per source file  
- **HARD limit:** 900 lines per source file (must be split)

## After each phase (mandatory)
When a phase is complete, run:
1. `create_codebase.bat`

If Loopia deployment is used:
2. `deploy_loopia.bat`

## Snapshot & audit
Snapshots are produced via `create_codebase.bat` and are used by OA to audit against PRD/SoT/HLD/Plan.
