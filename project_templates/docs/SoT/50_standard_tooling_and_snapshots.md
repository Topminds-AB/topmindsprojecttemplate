# SoT — 50 Standard Tooling and Backups

> **Purpose:** Define standard helper files for notifications, database backups, Docker logs, and local cleanup.

---

## 1) Database backups

The standard database backup tools are:

- `scripts/dbbackup_full.bat`
- `scripts/dbbackup_full.ps1`

They write database dumps and metadata to the repo-root `.dbbackup/` directory by default. Keep `.dbbackup/` unchanged as a local backup location; do not commit secrets or production dumps unless explicitly approved. See `docs/SoT/10_runtime_and_config.md` for configuration and retention behavior.

## 2) Docker log helper

`dockerlogs.bat` collects Docker logs into `.dockerlogs/` using `scripts/collect_docker_logs.ps1`. Python collectors may remain only as legacy compatibility helpers during rollout.

Logs may contain sensitive runtime information. Review them before sharing externally; generated logs should normally be gitignored unless explicitly requested as evidence.

## 3) Notification helper

`homey_finished.ps1` is a local helper used to send a completion message. Do not remove it as clutter. If unused in a specific repo, document the reason before removing it.

## 4) NUL cleanup helper

`delete_nul_script.ps1` cleans invalid `NUL` filesystem entries on Windows. Do not remove it as clutter. If unused in a specific repo, document the reason before removing it.

## 5) Reusable template material

Reusable templates that apply to many repos belong in Obsidian:

```text
<OBSIDIAN_VAULT_PATH>/templates/
```

Examples include `deploy_loopia.bat.template`, reusable PRD and HLD templates, agent prompts, and Wiki.js publishing templates. A repo may keep a local copy only when it is modified for that repo or must travel with the code.
