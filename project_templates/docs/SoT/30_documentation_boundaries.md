# SoT — 30 Documentation Boundaries

> **Purpose:** Define what belongs in this repository and what belongs in Obsidian.
> **Rule:** Repo-local documentation travels with code. Cross-repo and durable operational knowledge lives in Obsidian.

---

## 1) Repository-local documentation

Keep documentation in this repo only when it is required to build, test, deploy, audit, or understand this specific codebase at the current commit.

Repo-local examples:

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `docs/SoT/`
- `docs/PRD/PRD.md`
- `docs/HLD/HLD.md`
- `docs/implementation/PLAN.md`
- `docs/implementation/evidence/`
- `docs/ADR/`
- repo-specific deployment notes
- repo-specific migration notes that must travel with code
- repo-specific test evidence
- repo-specific generated manifests under `manifest/`

---

## 2) Obsidian-global documentation

Store cross-repo, reusable, durable, or operational knowledge in Obsidian.

Obsidian examples:

- shared agent rules
- shared skills
- shared templates
- global runbooks
- Wiki.js documentation
- Cloudflare documentation
- Traefik documentation
- Loopia documentation
- DOCKERHOST1 documentation
- shared deployment patterns
- canonical durable worklogs
- cross-repo decisions
- long-lived meeting-derived project knowledge
- reusable prompt libraries

---

## 3) Obsidian folder model

Use this layout inside the vault:

```text
<OBSIDIAN_VAULT_PATH>/
  _system/
    agent-rules/
    runbooks/
      <system>/
  skills/
  templates/
  wiki/
    systems/
      <system>/
  projects/
  dev-projects/
    <repo-name>/
      repo-profile.md
      worklogs/
      plans/
      sot/
      decisions/
      evidence/
  raw/
```

The environment variable `OBSIDIAN_VAULT_PATH` is documented in `docs/SoT/10_runtime_and_config.md`.

### 3.1 System documentation split

Use this split for systems that are used across many repos or operators:

- `wiki/systems/<system>/`:
  - canonical system overview
  - architecture
  - concepts
  - durable decisions
  - long-lived system notes
- `_system/runbooks/<system>/`:
  - step-by-step routines
  - troubleshooting guides
  - recurring operator procedures
  - FAQ-style operational notes

Do not leave reusable operational knowledge only in worklogs when it belongs in one of these system locations.

---

## 4) Canonical worklog location

Canonical durable worklogs are stored in Obsidian:

```text
<OBSIDIAN_VAULT_PATH>/dev-projects/<repo-name>/worklogs/
```

`docs/worklogs/` is allowed only as:

1. a fallback when Obsidian is unavailable,
2. a local staging area before content is moved to Obsidian, or
3. project-specific evidence when OA explicitly requires repo-local worklog material.

When `docs/worklogs/` is used as fallback or staging, the reason must be documented in the entry.

---

## 5) Shared skills and templates

Shared skills and reusable templates should not be duplicated into every repo.

Canonical locations:

```text
<OBSIDIAN_VAULT_PATH>/skills/
<OBSIDIAN_VAULT_PATH>/templates/
<OBSIDIAN_VAULT_PATH>/_system/agent-rules/
```

Repo-local copies are allowed only when the repo must be self-contained for a specific reason. That reason must be documented in `docs/ADR/` or `docs/SoT/00_index.md`.

---

## 6) Wiki.js and platform documentation

Wiki.js, Cloudflare, Traefik, Loopia, DOCKERHOST1, and other shared platform documentation belong in Obsidian unless a repo needs a small, code-coupled deployment note.

Repo-local platform notes must be short and must link to the canonical Obsidian page when one exists.

Recommended canonical targets:

- system knowledge: `wiki/systems/<system>/`
- routines and FAQ: `_system/runbooks/<system>/`

---

## 7) Decision rule

Use this rule when deciding where documentation belongs:

- If the document is needed to understand this exact commit, keep it in repo.
- If the document applies to many repos, keep it in Obsidian.
- If the document is a reusable template, keep it in Obsidian.
- If the document is a durable worklog, keep it in Obsidian.
- If the document is generated, store it under the documented generated-output location and do not treat it as canonical source material.
