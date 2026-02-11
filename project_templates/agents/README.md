# /agents — Agent Library (Topminds)

This folder contains the canonical instructions and templates for the **OA/IA workflow**.

## Structure
- `agents/IA/` — Instructions the **Implementation Agent (IA)** must follow during implementation.
- `agents/OA/` — Instructions the **Orchestration Agent (OA)** uses for audit, snapshot reading, and governance.

## Entry points
### For IA
- `agents/IA/01_IA_PROMPT_GENERIC.md` — baseline prompt to paste at the start of each IA session.
- `agents/IA/02_IA_PROMPT_TEMPLATE.md` — mandatory template for OA→IA prompts (phase prompts).

### For OA
- `agents/OA/00_AO_MASTER_PROMPT.md` — OA executive operating prompt.
- `agents/OA/10_ZIP_READING_WINDOWS.md` + `agents/OA/15_WINDOWS_ZIP_HANDLING_RULES.md` — Windows ZIP handling rules for audits (OA only).

## Policy
- IA should **not** read or follow OA ZIP-handling docs. OA handles ZIP review and any platform-specific unpacking rules.
- Repo-level agent instruction files (e.g. `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) are governed by `agents/OA/20_AGENT_INSTRUCTION_FILES_GOVERNANCE.md`.
