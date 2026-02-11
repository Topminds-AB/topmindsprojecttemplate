# Agent Instruction Files Governance (OA-owned)

This document defines how repo-level agent instruction files are governed.

## Scope
Repo-level instruction files typically include:
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- any additional agent-specific instruction files used by the team

## Ownership
- **OA owns governance**: OA must keep these files aligned with the current **HLD / PRD / SoT / Implementation Plan**.
- **IA may update these files only when explicitly instructed by OA** in a phase prompt.

## Update rules
- Keep them **short, actionable, and repo-specific**.
- Avoid duplicating `/agents` content; instead link to the canonical documents in `/agents`.
- If implementation changes significantly alter workflows, dependencies, or required steps, OA should request updates in the next phase.

## Minimum recommended content per file
- `AGENTS.md`: entrypoints, where to find PRD/SoT/Plan, snapshot command.
- `CLAUDE.md` / `GEMINI.md`: model-specific constraints, how to run tests, local commands, and repo quirks.
