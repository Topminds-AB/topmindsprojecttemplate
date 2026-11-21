# SoT — 40 Agent Workflow

<!-- NEXUS:GLOBAL-TEMPLATE:START:SOT-40 -->
> **Managed block.** The text between the markers is updated centrally through Nexus and must not be edited in this repo. Write project-specific agent notes **below** the block.

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
10. `docs/PRD/PRD.md`
11. `docs/HLD/HLD.md`
12. `docs/implementation/PLAN.md` (or the canonical plan named in `docs/SoT/00_index.md`)

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

- **Director:** owns planning, scope, acceptance criteria, test selection, integration and delivery.
- **Executor:** implements one scoped assignment and updates the repo-local documentation that changed because of it.
- **Independent review:** `devlab-test-guru` reviews test evidence and Sentinel reviews the phase gate. Nobody approves their own work.
- **Mattias:** makes decisions and gives human acceptance.

The role names are workflow conventions. They do not override repo instructions or owner decisions.

---

## 6) Before changing files

An agent must identify:

- the current phase,
- the files that are in scope,
- the files that must not be touched,
- the relevant SoT files,
- the relevant test governance files,
- whether Obsidian contains shared rules that apply to the task,
- whether the task creates reusable system knowledge that must be crystallized into `wiki/systems/<system>/` or `_system/runbooks/<system>/`,
- the file class of each file to be changed (`.nexus/file-classes.json` when present): `LOCKED` and `NEXUS_GENERATED` files are never edited, and in `MANAGED_BLOCK` files only the project part outside the markers is edited,
- the acceptance criteria and mandatory test packages recorded in the canonical plan.

---

## 7) After changing files

An agent must report:

- files changed,
- tests or validation performed,
- the test result line written in the canonical plan (command, version, pass/fail counts),
- documentation updated,
- worklog location used,
- remaining risks or follow-up actions.
<!-- NEXUS:GLOBAL-TEMPLATE:END:SOT-40 -->

## Project-specific agent notes

Verified, repo-specific additions only (for example extra consultant sessions, local tooling or flows). None recorded yet.
