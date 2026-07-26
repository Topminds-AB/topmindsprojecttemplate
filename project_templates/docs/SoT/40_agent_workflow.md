# SoT — 40 Agent Workflow

> **Purpose:** Define the repo-local agent workflow and how agents find shared rules.
> **Rule:** `AGENTS.md` is the only canonical repo-level agent entrypoint. Other root agent files are short adapters.

---

## 1) Root instruction model

- `AGENTS.md` is the canonical repo-level agent entrypoint.
- `CLAUDE.md` must stay short and point to `AGENTS.md`.
- `GEMINI.md` must stay short and point to `AGENTS.md`.
- Do not duplicate long instructions across all three files.

This avoids wasting context and prevents instruction drift.

---

## 2) Source order for repo work

For normal repo work, read in this order:

1. `AGENTS.md`
2. `docs/SoT/00_index.md`
3. `docs/SoT/10_runtime_and_config.md`
4. `docs/SoT/20_repo_layout.md`
5. `docs/SoT/30_documentation_boundaries.md`
6. `docs/SoT/40_agent_workflow.md`
7. `docs/SoT/50_standard_tooling_and_snapshots.md`
8. `docs/SoT/70_test_governance.md`
9. `docs/TESTING/TEST-STRATEGY.md`
10. `docs/TESTING/TEST-CATALOG.md`
11. `docs/TESTING/TEST-LOG.md`
12. `docs/PRD/PRD.md`
13. `docs/HLD/HLD.md`
14. `docs/implementation/PLAN.md`

Read additional repo files only when the task requires them.

---

## 3) Shared rules and skills

Resolve shared material from Obsidian:

```text
<OBSIDIAN_VAULT_PATH>/_system/agent-rules/
<OBSIDIAN_VAULT_PATH>/_system/dev-standards/
<OBSIDIAN_VAULT_PATH>/_system/runbooks/
<OBSIDIAN_VAULT_PATH>/skills/
<OBSIDIAN_VAULT_PATH>/templates/
<OBSIDIAN_VAULT_PATH>/wiki/systems/
```

`OBSIDIAN_VAULT_PATH` is documented in `docs/SoT/10_runtime_and_config.md` and must be present in `.env.example` when Obsidian integration is used.

When the task concerns a shared system such as Cloudflare, Traefik, Wiki.js, DOCKERHOST1, or another reused platform:

1. read `wiki/systems/<system>/` for canonical system knowledge,
2. read `_system/runbooks/<system>/` for routines, troubleshooting, and FAQ,
3. then read repo-specific worklogs or plans only when needed for local context.

---

## 4) Worklog behavior

Canonical durable worklogs are written to Obsidian:

```text
<OBSIDIAN_VAULT_PATH>/dev-projects/<repo-name>/worklogs/
```

`docs/worklogs/` may be used only as fallback, staging, or explicit repo-local evidence as defined in `docs/SoT/30_documentation_boundaries.md`.

---

## 5) Agent roles

- **OA:** Defines scope, phase, acceptance criteria, and documentation boundaries.
- **IA:** Implements scoped changes and updates repo-local documentation that changed because of the implementation.
- **TA:** Validates behavior, tests, documentation links, and evidence.

The role names are workflow conventions. They do not override repo instructions or owner decisions.

---

## 6) Before changing files

An agent must identify:

- the current phase,
- the files that are in scope,
- the files that must not be touched,
- the relevant SoT files,
- the relevant test governance files,
- whether Obsidian contains shared rules that apply to the task.
- whether the task creates reusable system knowledge that must be crystallized into `wiki/systems/<system>/` or `_system/runbooks/<system>/`.
- whether the task requires a new or updated `TEST-CATALOG.md` entry before implementation starts.
- whether the first qualifying run must be captured as a red baseline before implementation.

---

## 7) After changing files

An agent must report:

- files changed,
- tests or validation performed,
- test catalog entries added or updated,
- test log entries added or updated,
- documentation updated,
- worklog location used,
- remaining risks or follow-up actions.
