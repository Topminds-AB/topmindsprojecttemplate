# AI_INSTRUCTION_Worklog.md

> **Audience:** An AI developer-assistant writing and maintaining a daily rolling worklog inside an Obsidian vault.
> **Objective:** Produce accurate, append-only Obsidian worklog entries with traceability (commit ↔ files ↔ tests ↔ docs), minimal friction for humans, and durable repo-specific knowledge storage.

---

# 1. Purpose

The agent must write a worklog entry after every completed work session.

The worklog must be stored in the user's Obsidian vault, under the repository-specific folder:

dev-projects/<repo-name>/worklogs/YYYY/YY-MM-DD_Worklog.md

The repository folder must be created automatically if it does not exist.

The original repository files must not be used as the primary worklog location unless the Obsidian vault cannot be found. If the vault cannot be found, the agent must fail safely and clearly report that the worklog could not be written to Obsidian.

2. Golden Rules
Obsidian-first: The canonical worklog location is the Obsidian vault, not the source repository.
Repository-specific folder: Each repository gets its own folder under dev-projects/<repo-name>/.
Create missing structure: If the repo folder, worklog folder, yearly folder, or daily worklog file does not exist, create it.
Newest-first: Insert the latest entry at the top of section ## 4) Rolling Log (Newest First).
Central parameters mandatory: Each entry must include: time, title, change type, scope, taskmaster id, branch, commit(s), commands, result summary, exact files changed with line ranges and functions/classes, diffs (minimal), tests executed, system documentation updated, artifacts, and next action.
Exactness over brevity: Prefer precise file paths, SHAs, and line ranges. If code is removed, it must be commented in code and justified in the worklog.
Traceability: Keep ## 13) Stats & Traceability consistent with entries. Maintain Ticket ↔ Commit ↔ Test mapping.
No secrets: Redact secrets from env files, logs, terminal output, screenshots, and generated summaries. Never paste tokens, passwords, cookies, private keys, connection strings, or credentials.
Idempotent behavior: Do not reformat unrelated parts of the worklog file. Only insert the new entry, update the Daily Index, update stats/traceability, and update relevant Obsidian index links.
No unrelated vault edits: Do not modify unrelated Obsidian pages.
Session completion gate: Before giving the final response to the user, the agent must write or attempt to write the worklog entry.
3. Obsidian Vault Discovery

The agent must locate the Obsidian vault using this order:

Environment variable:
OBSIDIAN_VAULT_PATH
Repository-local config file:
.agent/obsidian_vault_path.txt
Repository-local config file:
.ai/obsidian_vault_path.txt
Repository-local config file:
OBSIDIAN_VAULT_PATH.txt
Current directory or parent directory containing:
.obsidian/

If multiple candidates exist, use the first valid path in the order above.

A valid Obsidian vault path is a directory that exists and either:

contains .obsidian/, or
contains one or more of these expected vault folders:
raw/
wiki/
templates/
skills/
projects/
dev-projects/

If no valid vault is found, do not silently write the canonical worklog inside the repository. Instead:

Create a pending fallback entry in:
.worklog_pending_obsidian/YYYY/YY-MM-DD_Worklog.md
Clearly state in the final response:
Obsidian vault not found. Worklog was written to pending fallback path and must be moved after OBSIDIAN_VAULT_PATH is configured.
4. Repository Name Resolution

The repo name must be derived automatically.

Use this order:

Git repository root folder name:
git rev-parse --show-toplevel

Then use the basename of that path.

If Git is unavailable, use the current working directory basename.

Normalize the repo folder name for Obsidian paths:

Keep letters, numbers, hyphen, underscore, and dot.
Replace spaces with hyphens.
Remove characters that are invalid or unsafe in file paths.
Preserve the original repo name in frontmatter and page content.

Example:

Repository root: E:\projects\docpilot-desktop-recorder
Repo folder: dev-projects/docpilot-desktop-recorder/
5. Canonical Obsidian Folder Structure

For each repository, the agent must maintain this structure:

dev-projects/
  _index.md
  <repo-name>/
    index.md
    worklogs/
      index.md
      YYYY/
        YY-MM-DD_Worklog.md
    artifacts.md
    decisions.md
    open-questions.md

Only create files that are missing.

Do not overwrite existing files.

6. Where to Log

The daily worklog file is named:

YY-MM-DD_Worklog.md

The date must use local time Europe/Stockholm.

The canonical daily worklog path is:

<Obsidian vault>/dev-projects/<repo-name>/worklogs/YYYY/YY-MM-DD_Worklog.md

Example:

D:/ObsidianVault/dev-projects/docpilot-desktop-recorder/worklogs/2026/26-05-03_Worklog.md

The repo landing page is:

<Obsidian vault>/dev-projects/<repo-name>/index.md

The repo worklog index is:

<Obsidian vault>/dev-projects/<repo-name>/worklogs/index.md

The global dev-project index is:

<Obsidian vault>/dev-projects/_index.md
7. Required Repo Index Page

If missing, create:

dev-projects/<repo-name>/index.md

Use this structure:

---
title: "<repo-name>"
type: dev-project
repo_name: "<original repo name>"
created_by: agent
tags:
  - dev-project
  - repository
---

# <repo-name>

## Summary

Repository-specific notes, worklogs, decisions, artifacts, and follow-up items.

## Links

- [[dev-projects/<repo-name>/worklogs/index|Worklogs]]
- [[dev-projects/<repo-name>/decisions|Decisions]]
- [[dev-projects/<repo-name>/open-questions|Open Questions]]
- [[dev-projects/<repo-name>/artifacts|Artifacts]]

## Latest Worklog

<!-- WORKLOG_LATEST_START -->
No worklog entries yet.
<!-- WORKLOG_LATEST_END -->

## Repository Metadata

- **Repository name:** `<original repo name>`
- **Obsidian folder:** `dev-projects/<repo-name>/`

When adding a new daily worklog, update only the section between:

<!-- WORKLOG_LATEST_START -->
<!-- WORKLOG_LATEST_END -->
8. Required Worklog Index Page

If missing, create:

dev-projects/<repo-name>/worklogs/index.md

Use this structure:

---
title: "<repo-name> Worklogs"
type: worklog-index
repo_name: "<original repo name>"
created_by: agent
tags:
  - worklog
  - dev-project
---

# <repo-name> Worklogs

## Daily Worklogs

<!-- DAILY_WORKLOG_INDEX_START -->
No worklogs yet.
<!-- DAILY_WORKLOG_INDEX_END -->

## Notes

Newest daily worklog links are inserted at the top.

When adding a new daily worklog, insert or update one link at the top of the section between:

<!-- DAILY_WORKLOG_INDEX_START -->
<!-- DAILY_WORKLOG_INDEX_END -->

Example link:

- [[dev-projects/docpilot-desktop-recorder/worklogs/2026/26-05-03_Worklog|26-05-03 Worklog]]
9. Required Global Dev-Projects Index

If missing, create:

dev-projects/_index.md

Use this structure:

---
title: "Development Projects"
type: dev-project-index
created_by: agent
tags:
  - dev-project
  - index
---

# Development Projects

<!-- DEV_PROJECT_INDEX_START -->
No repositories indexed yet.
<!-- DEV_PROJECT_INDEX_END -->

When creating or using a repo folder, ensure the repo is listed once between:

<!-- DEV_PROJECT_INDEX_START -->
<!-- DEV_PROJECT_INDEX_END -->

Example:

- [[dev-projects/docpilot-desktop-recorder/index|docpilot-desktop-recorder]]

Do not duplicate links.

10. Daily Worklog Template

If the daily worklog file does not exist, create it with this structure:

---
title: "YY-MM-DD Worklog"
type: worklog
repo_name: "<original repo name>"
repo_folder: "dev-projects/<repo-name>"
date: "YYYY-MM-DD"
timezone: "Europe/Stockholm"
created_by: agent
tags:
  - worklog
  - dev-project
---

# YY-MM-DD Worklog — <repo-name>

## 1) Daily Index

| Time | Title | Type | Scope | Ticket/Task | Commit | Files |
|---|---|---|---|---|---|---|

## 2) Session Context

- **Repository:** `<original repo name>`
- **Repo folder:** `dev-projects/<repo-name>/`
- **Date:** `YYYY-MM-DD`
- **Timezone:** Europe/Stockholm

## 3) Entry Template

Place your first real entry under section 4.

## 4) Rolling Log (Newest First)

<!-- ROLLING_LOG_START -->
<!-- ROLLING_LOG_END -->

## 5) Decisions

## 6) Database & Migrations

## 7) Tests & Evidence

## 8) Artifacts

## 9) Performance & Benchmarks

## 10) Documentation Updated

## 11) Open Questions

## 12) Next Actions

## 13) Stats & Traceability

### Ticket ↔ Commit ↔ Test Mapping

| Ticket/Task | Commit | Tests | Result |
|---|---|---|---|

### Changed Files Summary

| File | Lines | Symbols | Entry Time |
|---|---|---|---|

## 14) Rollback Notes
11. Required Entry Schema

Represent mentally like this.

Do not add YAML to the individual worklog entry.

entry:
  time: "HH:MM"
  title: "Short Title"
  change_type: [feat|fix|chore|docs|perf|refactor|test|ops]
  scope: "<component/module>"
  tickets: ["ABC-123", "PR#45"]
  branch: "feature/x"
  commits: ["a1b2c3d", "e4f5g6h"]
  environment: "docker:compose-profileX"
  commands: ["pytest -q", "playwright test --reporter=list"]
  result_summary: "1–3 lines outcome"
  files_changed:
    - path: "src/x.py"
      lines: "L42–L67"
      symbols: ["func_a", "ClassB.method_c"]
    - path: "docs/arch/overview.md"
      lines: "L10–L25"
      symbols: []
        diff: "minimal unified diff"
        tests_executed: "pytest ... / playwright ... results"
        perf_note: "p95 220ms → 180ms"
        docs_updated: ["docs/arch/overview.md: updated sequence diagram"]
        artifacts: ["artifacts/pytest.html", "screenshots/2025-08-19/test.png"]
        next_action: "Open PR and request review"
12. How to Collect Data

Use only local tooling.

Do not fetch remote secrets.

Git & Files

Branch:

git rev-parse --abbrev-ref HEAD

Latest commit short SHA:

git rev-parse --short HEAD

Repository root:

git rev-parse --show-toplevel

Changed files in working tree:

git diff --name-only

Changed files staged:

git diff --cached --name-only

Last commit files:

git diff --name-only HEAD~1..HEAD

Minimal diff for working tree:

git diff -U3

Per-file diff:

git diff -U3 -- <relative/path>
Line Ranges & Symbols

When editing files, record approximate line spans and function/class names touched.

If line ranges are uncertain:

Open the file.
Locate the changed function/class/section.
Record the relevant line span directly.
Documentation Files

Treat these as system documentation:

docs/
documentation/
doc/
README.md
CLAUDE.md
AGENTS.md
GEMINI.md

If any are changed, list them under:

System documentation updated

with a short note.

Tests & Evidence

Run relevant available tests.

Common examples:

pytest -q
pytest --maxfail=1 -q --cov=.
playwright test --reporter=list

Save artifacts, HTML reports, screenshots, and logs into predictable repo paths where applicable, for example:

artifacts/
screenshots/
test-results/
playwright-report/

Reference artifact paths in the worklog entry.

Performance

If performance-sensitive code changed, gather before/after metrics with the smallest representative benchmark available.

Include:

p95
CPU delta
Memory delta
Benchmark command
Benchmark result
Database & Migrations

If schema changes occurred:

Reference migration files.
Provide forward migration summary.
Provide rollback summary.
List SQL snippets only when they are safe and non-secret.
13. Daily Index Update

Add one row at the top of the Daily Index table.

Format:

| HH:MM | <Short Title> | <change_type> | `<scope>` | ABC-123 | `a1b2c3d` | path1, path2 |

Keep the table header intact.

Only insert one new row per completed session.

14. Rolling Log Insertion Algorithm
Resolve the Obsidian vault.
Resolve the repo name.
Ensure this folder exists:
dev-projects/<repo-name>/worklogs/YYYY/
Ensure these files exist:
dev-projects/_index.md
dev-projects/<repo-name>/index.md
dev-projects/<repo-name>/worklogs/index.md
dev-projects/<repo-name>/worklogs/YYYY/YY-MM-DD_Worklog.md
Read YY-MM-DD_Worklog.md into memory.
Find:
## 4) Rolling Log (Newest First)
Insert the new entry directly after:
<!-- ROLLING_LOG_START -->
Update the Daily Index table by inserting a single row directly below the header.
Update ## 13) Stats & Traceability.
Update dev-projects/<repo-name>/worklogs/index.md.
Update dev-projects/<repo-name>/index.md.
Update dev-projects/_index.md.
Do not modify unrelated sections.
15. Entry Format

Use this format for every real entry:

#### [HH:MM] <Change type>: <Short Title>

- **Change type:** <feat|fix|chore|docs|perf|refactor|test|ops>
- **Scope (component/module):** `<scope>`
- **Tickets/PRs/Taskmaster:** <ticket ids or N/A>
- **Branch:** `<branch>`
- **Commit(s):** `<short-sha>` or `N/A`
- **Environment:** <environment or N/A>
- **Commands run:**
  ```bash
  <command>

- **Result summary:** <1–3 lines>
- **Files changed (exact):**
  - `<path>` — <line range> — functions/classes: `<symbols>`
- **Unified diff (minimal, per file or consolidated):**
  ```diff
  <minimal diff>
  ```
- **Tests executed:** <commands and results>
- **Performance note:** <metrics or N/A>
- **System documentation updated:**
  - `<path>` — <summary>
- **Artifacts:** <paths or N/A>
- **Obsidian worklog path:** `dev-projects/<repo-name>/worklogs/YYYY/YY-MM-DD_Worklog.md`
- **Next action:** <next action>
16. Stats & Traceability Update

For every entry, update:

## 13) Stats & Traceability

Maintain:

### Ticket ↔ Commit ↔ Test Mapping

| Ticket/Task | Commit | Tests | Result |
|---|---|---|---|

Add one row per ticket/task when available.

Maintain:

### Changed Files Summary

| File | Lines | Symbols | Entry Time |
|---|---|---|---|

Add changed files from the latest session.

Do not duplicate identical rows from the same session.

17. Obsidian Link Rules

Use Obsidian-style links for vault-internal references.

Examples:

[[dev-projects/<repo-name>/index|Repo Index]]
[[dev-projects/<repo-name>/worklogs/index|Worklogs]]
[[dev-projects/<repo-name>/worklogs/YYYY/YY-MM-DD_Worklog|YY-MM-DD Worklog]]

Do not use absolute local disk paths inside normal wiki links.

Absolute paths may only be used in diagnostic text when needed.

18. Artifacts

Do not move large artifacts into Obsidian automatically.

Instead:

Keep test reports, screenshots, logs, and build artifacts in their repository artifact folders.
Reference them from the Obsidian worklog using relative repo paths.
If a small human-readable artifact is important as durable knowledge, summarize it in the worklog.
19. Failure Handling

If Git commands fail:

State that explicitly in the entry.
Continue with manual details.
Use N/A where exact Git data is unavailable.

If tests are flaky:

Mark them as flaky.
Include command output summary.
Do not delete or suppress failures silently.

If Obsidian vault discovery fails:

Create fallback path:
.worklog_pending_obsidian/YYYY/YY-MM-DD_Worklog.md
Write the entry there.
Report this in the final answer.
Do not claim that the canonical Obsidian worklog was updated.

If the worklog file cannot be edited safely:

Do not rewrite the entire file.
Create a pending entry file:
.worklog_pending_obsidian/YYYY/HHMM_pending_entry.md
Report the exact reason.
20. Final Response Requirement

Before the final response, the agent must complete the worklog step.

The final response must include:

## Worklog
- Obsidian vault: <resolved vault path or not found>
- Repo folder: `dev-projects/<repo-name>/`
- Worklog file: `dev-projects/<repo-name>/worklogs/YYYY/YY-MM-DD_Worklog.md`
- Entry time: HH:MM
- Status: written | pending fallback | failed

If the status is not written, explain exactly what prevented the Obsidian write.

21. Completion Checklist

Before finalizing, verify:

The Obsidian vault was resolved.
The repo name was resolved.
The repo folder exists under dev-projects/.
The daily worklog exists.
The new entry was inserted newest-first.
The Daily Index row was inserted at the top.
Stats & Traceability were updated.
The repo worklog index was updated.
The repo index latest worklog link was updated.
The global dev-projects/_index.md contains the repo link.
No unrelated Obsidian files were modified.
No secrets were written.

End of AI instruction.xxxxxxxxxx ## Included Helper Scripts- `tools/add_worklog_entry.ps1` — PowerShell helper that **generates an entry block** (to console and `.worklog_generated/`) using Git data.- `tools/add_worklog_entry.sh` — Bash helper that does the same on Linux/macOS/WSL.> These scripts **do not edit files automatically**; they produce an entry block for you to paste at the top of the Rolling Log and add a row to the Daily Index. This keeps edits deliberate and avoids unintended formatting changes.## Failure Handling- If Git commands fail, state that explicitly in the entry (e.g., "Git unavailable"), and proceed with manual details.- If tests are flaky, mark them as flaky and provide a link/ID. Do not delete or suppress failures silently.---**End of AI instruction.**
