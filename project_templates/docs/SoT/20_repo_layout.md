# Repository Layout (SoT)

This document defines repo hygiene, component boundaries, and anti-monolith rails.
It is intentionally practical and meant to reduce long-term maintenance cost.

---

## 1) Repo Hygiene (MANDATORY)
- `.gitignore` MUST exclude: `node_modules/`, `dist/`, `build/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `coverage/`, `*.log`
- `.env` MUST NOT be committed. Provide `.env.example` at repo root.
- No large binaries in git. If unavoidable, document in `/docs/ADR/`.

---

## 2) Component Boundaries (MANDATORY)
Use component boundaries only if the repo actually has multiple components. If the repo is small, keep it simple.

- `/apps/*` MAY import from `/libs/*` and its own local code only.
- `/services/*` MAY import from `/libs/*` and its own local code only.
- `/libs/*` MUST NOT import from `/apps` or `/services` (libs are dependency-bottom).
- Cross-app imports are forbidden.
- Each component SHOULD define a "public API surface":
  - TS/JS: `/<component>/src/index.ts` exports only allowed entrypoints.
  - Python: `/<component>/__init__.py` exports only allowed entrypoints.
- Internal code SHOULD live under `src/internal/` (or equivalent) and must not be imported cross-component.

---

## 3) Repo Root (MANDATORY: stable names)
These files MUST exist at repo root. Names must remain stable:

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.env.example`

Snapshot tooling:
- `create_codebase.bat` (Windows wrapper)
- `create_codebase.ps1` (PowerShell engine)

Docker wrappers (RECOMMENDED if the repo uses Docker Compose):
- `docker-compose.yml`
- `docker_compose_up.bat`
- `docker_compose_build_pull.bat`
- `docker_compose_build_nocache.bat`

If the repo does not use Docker, omit the Docker wrappers and document local run commands in `docs/SoT/00_index.md`.

---

## 4) Recommended Directories
Use what fits the project. Avoid creating folders that are not used.

- `/docs/`
  - `/docs/HLD/`
  - `/docs/PRD/`
  - `/docs/SoT/`
  - `/docs/implementation/`
  - `/docs/worklogs/`
  - `/docs/ADR/` (recommended when architecture decisions appear)
- `/database/`
  - `/database/migrations/` (if applicable)
- `/services/` (if applicable)
- `/apps/` (if applicable)
- `/libs/` (if applicable)
- `/tests/` (if applicable)
- `/scripts/`

---

## 5) Modularity / File Size Rail (MANDATORY)
- MAX_LINES_PER_SOURCE_FILE_SOFT = 600
- MAX_LINES_PER_SOURCE_FILE_HARD = 900
- Applies to all source files: `.py`, `.ts`, `.js`, `.sh`, etc.

Rules:
- Any file > SOFT:
  - Requires: brief justification in `manifest/change_summary.md`
  - Requires: split plan (what modules will be extracted and when)
- Any file > HARD:
  - Verdict MUST be NOT APPROVED until split into smaller modules.

---

## 6) LOC Measurement (PROFILE-BASED)
This is enforced only when the delivery profile is **STANDARD** or **AUDIT_STRICT**, or when OA explicitly requests it for a phase.

- LOC must be measured by a deterministic script in `/scripts/` (e.g. `scripts/loc_report.*`).
- The report MUST exclude generated/build/vendor dirs (`node_modules`, `dist`, `build`, `.venv`, etc.).
- Phase snapshot should include: `/manifest/loc_report.txt` listing per-file line counts + totals.

---

## 7) Change Budget (PROFILE-BASED)
This is enforced only when the delivery profile is **STANDARD** or **AUDIT_STRICT**, or when OA explicitly requests it for a phase.

Default budget (guideline, not a blocker in MVP_FAST):
- MAX_CHANGED_FILES = 10 (excluding migrations/tests-only tasks)
- MAX_DIFF_LOC = 800

If a phase exceeds the budget:
- OA should call it out
- PO decides if it's acceptable or if the phase should be split

---

## 8) Architecture Decisions (RECOMMENDED)
Record any cross-cutting architectural change in `/docs/ADR/`:
- `ADR-YYYYMMDD-<short-title>.md` (decision, alternatives, consequences)
