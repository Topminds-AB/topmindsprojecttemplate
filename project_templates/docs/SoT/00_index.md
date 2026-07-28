# SoT — 00 Index

> **Purpose:** A 2–5 minute map of this repo. Keep it short, current, and practical.
> **Owner:** PO owns content, OA owns structure, IA keeps it current when implementing changes.

---

## 1) What this system is

- **Product:**
- **Primary users:**
- **Core outcome:**
- **Non-goals:**

---

## 2) Delivery profile

- **Current profile:** `MVP_FAST | STANDARD | AUDIT_STRICT`
- **Notes:**

---

## 3) Quickstart

### Local run

- **Prerequisites:**
- **Command(s):**
  -
- **Local URL(s):**
  -
- **Default dev credentials:** Only non-secret values may be documented here.

### Tests

- **Command(s):**
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\template_backup_standardization_smoke.ps1`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\codex_startup_distribution_smoke.ps1`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\create_codebase.ps1`
- **Expected result:**
  - smoke checks pass
  - a fresh verified ZIP appears in `.codebasebackup\`
- **Governed test docs:**
  - `docs/SoT/70_test_governance.md`
  - `docs/TESTING/TEST-STRATEGY.md`
  - `docs/TESTING/TEST-CATALOG.md`
  - `docs/TESTING/TEST-LOG.md`

---

## 4) Source of Truth files

Read these files before making structural, runtime, documentation, or agent-workflow changes:

1. `docs/SoT/00_index.md` — repo map and canonical links.
2. `docs/SoT/10_runtime_and_config.md` — runtime, environment variables, ports, endpoints, and config rules.
3. `docs/SoT/20_repo_layout.md` — repo layout, stable root files, standard tooling, and repo hygiene.
4. `docs/SoT/30_documentation_boundaries.md` — what belongs in repo and what belongs in Obsidian.
5. `docs/SoT/40_agent_workflow.md` — repo-local agent workflow and source order.
6. `docs/SoT/50_standard_tooling_and_snapshots.md` — snapshot tooling, backup folders, logs, and standard helper scripts.
7. `docs/SoT/70_test_governance.md` — repo-local test governance adapter and links to the canonical Obsidian rule.

---

## 5) Repo map

Keep this aligned with the actual repository.

- `README.md` → human entrypoint.
- `AGENTS.md` → only canonical repo-level agent entrypoint.
- `CLAUDE.md` → short adapter pointing to `AGENTS.md`.
- `GEMINI.md` → short adapter pointing to `AGENTS.md`.
- `.env.example` → committed example configuration; secrets must not be included.
- `scripts/purge-cloudflare.ps1` and `scripts/purge-cloudflare.sh` → Cloudflare cache purge helpers that read repo config from `.env`.
- `.codebasebackup/` → local snapshot storage and Windows ZIP handling rules.
- `.dbbackup/` → local database backup storage.
- `.dockerlogs/` → local Docker log output.
- `manifest/` → generated or phase-specific manifests and summaries.
- `docs/HLD/` → high-level design.
- `docs/PRD/` → product requirements.
- `docs/SoT/` → repo-local source of truth.
- `docs/TESTING/` → governed test strategy, catalog, and execution log.
- `docs/implementation/` → implementation plans and evidence.
- `docs/ADR/` → architecture decisions when needed.
- `docs/worklogs/` → fallback or local worklog notes only when the Obsidian rule allows it.
- `agents/` → repo-local agent material only.
- `scripts/` → automation, helpers, and supporting scripts.
- `services/` → backend or service components when used.
- `apps/` → frontend or app components when used.
- `packages/` or `libs/` → shared code when used.
- `infra/` → infrastructure and deployment definitions when used.
- `tests/` → automated tests when used.
- `storage/` → local runtime storage, normally gitignored.

---

## 6) Architecture

Link to `docs/HLD/HLD.md` for details.

- **Components:**
  -
- **Data flow:**
  -
- **External dependencies:**
  -
- **Hosting/runtime:**
  -

---

## 7) Data stores

- **Primary DB engine:**
- **Migrations/schema source:**
- **Dumps:** Document where dumps live, how they are created, and whether they are included in snapshots.
- **Vector store:**

---

## 8) Configuration

The canonical configuration inventory lives in `docs/SoT/10_runtime_and_config.md`.

- **Config entrypoints:**
- **Secrets policy:** `.env` is gitignored. `.env.example` is committed and must contain example keys only.
- **Obsidian vault variable:** `OBSIDIAN_VAULT_PATH` must exist in `.env.example` when agents or tooling need shared Obsidian documentation.

---

## 9) Key flows

1. Purge Cloudflare cache after HTML or routing changes when repo config points to a Cloudflare-fronted hostname.
2.
3.

---

## 10) Known risks and tech debt

-
-

---

## 11) Canonical links

- **Runtime and config:** `docs/SoT/10_runtime_and_config.md`
- **Repo layout:** `docs/SoT/20_repo_layout.md`
- **Documentation boundaries:** `docs/SoT/30_documentation_boundaries.md`
- **Agent workflow:** `docs/SoT/40_agent_workflow.md`
- **Standard tooling and snapshots:** `docs/SoT/50_standard_tooling_and_snapshots.md`
- **Test governance:** `docs/SoT/70_test_governance.md`
- **Test strategy:** `docs/TESTING/TEST-STRATEGY.md`
- **Test catalog:** `docs/TESTING/TEST-CATALOG.md`
- **Test log:** `docs/TESTING/TEST-LOG.md`
- **HLD:** `docs/HLD/HLD.md`
- **PRD:** `docs/PRD/PRD.md`
- **Implementation plan:** `docs/implementation/PLAN.md`
- **ADR folder:** `docs/ADR/`
- **Obsidian project folder:** `<OBSIDIAN_VAULT_PATH>/dev-projects/<repo-name>/`
- **Obsidian system pages:** `<OBSIDIAN_VAULT_PATH>/wiki/systems/<system>/`
- **Obsidian runbooks and FAQ:** `<OBSIDIAN_VAULT_PATH>/_system/runbooks/<system>/`
