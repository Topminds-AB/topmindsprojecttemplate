# SoT — 20 Repository Layout

> **Purpose:** Define the standard repository layout, stable root files, hygiene rules, and boundaries that keep projects maintainable.
> **Owner:** OA owns the layout standard. IA keeps this file current when implementation changes the actual structure.

---

## 1) Repo hygiene

- `.env` must not be committed.
- `.env.example` must exist at repo root and must contain example values only.
- `.gitignore` must exclude generated dependencies, build outputs, caches, logs, and local secret files.
- Large binaries must not be committed unless the reason is documented in `docs/ADR/`.
- Generated folders must be clearly separated from source-controlled documentation and source code.

Minimum `.gitignore` coverage:

```text
node_modules/
dist/
build/
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
coverage/
*.log
.env
```

---

## 2) Stable root files

These files must exist at repo root in a standard repo:

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.env.example`
- `create_codebase.bat`
- `create_codebase.ps1`
- `create_codebase.md`

Optional but protected root tools:

- `homey_finished.ps1` — local notification helper used to message when work is complete.
- `dockerlogs.bat` — local Docker log collection helper.
- `delete_nul_script.ps1` — local cleanup helper for invalid `NUL` filesystem entries.

Do not delete protected root tools unless the owner has explicitly confirmed that the specific repo no longer uses them.

---

## 3) Standard root folders

These folders are allowed in the standard repo model:

- `.codebasebackup/` — local codebase snapshots and Windows ZIP handling rules.
- `.dbbackup/` — local database backups.
- `.dockerlogs/` — local Docker log output.
- `manifest/` — generated or phase-specific manifests, summaries, and reports.
- `docs/` — repo-local documentation.
- `agents/` — repo-local agent material only.
- `scripts/` — automation and helper scripts.
- `services/` — backend or service components when used.
- `apps/` — frontend or app components when used.
- `packages/` or `libs/` — shared libraries when used.
- `infra/` — infrastructure and deployment definitions when used.
- `database/` — schema, migrations, and database tooling when used.
- `tests/` — automated tests when used.
- `storage/` — local runtime storage, normally gitignored.

Avoid creating unused folders in project repos. The template may document optional folders, but a real repo should keep only what it uses.

---

## 4) Required docs structure

A standard repo must contain:

```text
docs/
  HLD/
    HLD.md
  PRD/
    PRD.md
  SoT/
    00_index.md
    10_runtime_and_config.md
    20_repo_layout.md
    30_documentation_boundaries.md
    40_agent_workflow.md
    50_standard_tooling_and_snapshots.md
    70_test_governance.md
  TESTING/
    TEST-STRATEGY.md
    TEST-CATALOG.md
    TEST-LOG.md
  implementation/
    PLAN.md
  ADR/
```

`docs/worklogs/` may exist only as a fallback or local staging area. Canonical durable worklogs belong in Obsidian, as defined in `docs/SoT/30_documentation_boundaries.md`.

---

## 5) Component boundaries

Use component boundaries only when the repo has multiple components.

- `/apps/*` may import from `/libs/*`, `/packages/*`, and its own local code only.
- `/services/*` may import from `/libs/*`, `/packages/*`, and its own local code only.
- `/libs/*` and `/packages/*` must not import from `/apps/*` or `/services/*`.
- Cross-app imports are forbidden unless explicitly documented in `docs/ADR/`.
- Each component should define a public API surface:
  - TypeScript/JavaScript: `/<component>/src/index.ts`
  - Python: `/<component>/__init__.py`
- Internal code should live under `src/internal/` or an equivalent folder and must not be imported across component boundaries.

---

## 6) Modularity and file-size rails

- `MAX_LINES_PER_SOURCE_FILE_SOFT = 600`
- `MAX_LINES_PER_SOURCE_FILE_HARD = 900`

Applies to source files such as `.py`, `.php`, `.ts`, `.js`, `.sh`, `.ps1`, `.go`, `.cs`, and similar implementation files.

Rules:

- A source file above the soft limit requires a short justification in `manifest/change_summary.md` and a split plan.
- A source file above the hard limit must be treated as not approved until split or explicitly accepted by OA/PO.

Exemptions:

- Worklogs and audit evidence.
- Snapshot manifests.
- Generated lockfiles such as `composer.lock`, `package-lock.json`, `yarn.lock`, and equivalent package manager files.
- Generated files that are explicitly documented as generated.

---

## 7) LOC measurement

Enforced when the delivery profile is `STANDARD` or `AUDIT_STRICT`, or when OA explicitly requests it.

- LOC must be measured by a deterministic script in `scripts/` or by an approved repo-local command.
- Reports must exclude generated, build, vendor, dependency, and virtual environment folders.
- Phase snapshots should include `manifest/loc_report.txt` when LOC measurement is required.

---

## 8) Change budget

Enforced when the delivery profile is `STANDARD` or `AUDIT_STRICT`, or when OA explicitly requests it.

Default guidance:

- `MAX_CHANGED_FILES = 10`, excluding migrations and tests-only tasks.
- `MAX_DIFF_LOC = 800`.

If a phase exceeds the budget, OA should call it out and PO decides whether the phase should continue or be split.

---

## 9) Architecture decisions

Record cross-cutting architectural decisions in `docs/ADR/`.

Filename format:

```text
ADR-YYYYMMDD-<short-title>.md
```

Each ADR should include:

- Decision.
- Context.
- Alternatives considered.
- Consequences.
- Links to related PRD, HLD, PLAN, issues, or commits.
