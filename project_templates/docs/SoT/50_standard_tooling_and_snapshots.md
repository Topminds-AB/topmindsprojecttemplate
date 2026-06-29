# SoT — 50 Standard Tooling & Snapshots

> **Purpose:** Define protected standard helper files, snapshot locations, local backup folders, and codebase packaging rules.
> **Rule:** Do not delete standard helper files unless the owner confirms that the specific repo does not use them.

---

## 1) Protected standard folders

These folders are part of the standard repo model and must not be treated as accidental clutter:

- `.codebasebackup/`
- `.dbbackup/`
- `.dockerlogs/`
- `manifest/`

### `.codebasebackup/`

Purpose:

- stores local codebase snapshots,
- stores snapshot-related support files,
- stores Windows ZIP handling documentation.

Required file:

```text
.codebasebackup/unzip.windows.md
```

`unzip.windows.md` must remain available because Windows-created ZIP snapshots can contain backslash paths and require careful handling.

### `.dbbackup/`

Purpose:

- stores local database dumps and backup artifacts.

Rules:

- Do not commit secrets.
- Do not include production dumps unless explicitly approved.
- Document dump handling in `docs/SoT/10_runtime_and_config.md` and `docs/SoT/00_index.md` when relevant.

### `.dockerlogs/`

Purpose:

- stores Docker log exports produced by local helper scripts.

Rules:

- Logs may contain sensitive runtime information.
- Review before sharing externally.
- Generated logs should normally be gitignored unless OA explicitly requests evidence to be committed.

### `manifest/`

Purpose:

- stores generated or phase-specific manifests, summaries, LOC reports, and snapshot metadata.

Common files:

- `manifest/change_summary.md`
- `manifest/loc_report.txt`
- `manifest/snapshot_manifest.txt`

---

## 2) Protected standard root scripts

These files are protected standard helpers:

- `create_codebase.bat`
- `create_codebase.ps1`
- `create_codebase.md`
- `homey_finished.ps1`
- `dockerlogs.bat`
- `delete_nul_script.ps1`

Do not remove them from the standard repo without explicit owner approval.

---

## 3) `create_codebase` files

The `create_codebase` tooling is used often and must live at repo root.

Required files:

```text
create_codebase.bat
create_codebase.ps1
create_codebase.md
```

Responsibilities:

- `create_codebase.bat` starts the snapshot workflow from Windows.
- `create_codebase.ps1` is the thin repo-root PowerShell entrypoint.
- `scripts/create_codebase_lib.ps1` contains the main snapshot implementation.
- `create_codebase.md` documents exactly how the snapshot tool is configured for this repo.

Related helpers now expected in the template:

- `scripts/template_runtime.ps1`
- `scripts/dbbackup_full.ps1`
- `scripts/collect_docker_logs.ps1`

---

## 4) Required `create_codebase.md` content

Each repo must update `create_codebase.md` when the snapshot rules differ from the template.

The file must document:

1. repo name,
2. snapshot destination,
3. included folders,
4. excluded folders,
5. excluded file patterns,
6. secret handling,
7. database dump handling,
8. Docker log handling,
9. Obsidian-related handling,
10. verification steps after snapshot creation.

The instructions must be exact enough that an agent can modify `create_codebase.bat` and `create_codebase.ps1` for the repo without guessing.

For the shared template specifically, `create_codebase.md` must also document:

- the canonical DB backup contract,
- multi-target failure behavior,
- launcher pause behavior,
- whether Docker collection is PowerShell-native or Python-based.

---

## 5) Snapshot exclusion policy

Snapshots must exclude:

- `.env`
- secret files
- private keys
- API tokens
- credentials
- `node_modules/`
- `.venv/`
- `vendor/` unless explicitly needed and approved
- build outputs unless explicitly needed and approved
- cache folders
- transient logs unless collected as explicit evidence

Snapshots may include:

- `.env.example`
- source code
- repo-local documentation
- migration files
- test files
- approved manifests
- approved evidence files
- `.codebasebackup/unzip.windows.md`

---

## 6) Windows ZIP handling

Before opening or analyzing a Windows-created ZIP snapshot, read:

```text
.codebasebackup/unzip.windows.md
```

This rule applies to humans and agents working directly with repo snapshots.

---

## 7) Notification helper

`homey_finished.ps1` is a protected local helper used to send a completion message when work is done.

Do not remove it as clutter. If it is unused in a specific repo, document the reason before removing it.

---

## 8) Docker log helper

`dockerlogs.bat` is a protected helper used to collect Docker logs into `.dockerlogs/`.

In the shared template, the primary implementation is `scripts/collect_docker_logs.ps1`. Python collectors may remain only as legacy compatibility helpers during rollout.

Do not remove it as clutter. If the repo does not use Docker, document the reason before removing it.

---

## 9) NUL cleanup helper

`delete_nul_script.ps1` is a protected helper used to clean invalid `NUL` filesystem entries on Windows.

Do not remove it as clutter. If it is unused in a specific repo, document the reason before removing it.

---

## 10) Template material

Reusable templates that apply to many repos belong in Obsidian:

```text
<OBSIDIAN_VAULT_PATH>/templates/
```

Examples:

- `deploy_loopia.bat.template`
- reusable PRD templates
- reusable HLD templates
- reusable agent prompts
- reusable Wiki.js publishing templates

A repo may keep a local copy only when the template is modified for that repo or must travel with the code.
