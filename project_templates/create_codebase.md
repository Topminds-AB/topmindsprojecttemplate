# create_codebase.md - Portable snapshot workflow

## Quick start

1. Run `create_codebase.bat`
2. Optional: run `create_codebase.bat --interactive` if you want the window to stay open
3. Find the ZIP in `.codebasebackup\`

## What the workflow does

The template snapshot flow now derives repo identity and runtime context from the repo folder plus `.env`.

It creates:

```text
/code/       source tree with secret redaction
/dbbackup/   repo-root .dbbackup artifacts and metadata
/dockerlogs/ compose logs when the repo uses Docker
/logs/       git evidence plus common runtime logs
/manifest/   manifest, file inventory, change summary, agent notes
```

ZIP naming:

```text
<REPO_PREFIX>_codebase_YYYY-MM-DD_HH-mm.zip
```

## Defaults and detection

- Repo name and ZIP prefix are derived from the repo folder name and optional `APP_NAME`.
- `.env` is resolved in this order:
  1. explicit path when a script switch provides one
  2. repo-root `.env`
  3. `infra\.env`
  4. script-local `.env`
- Docker is auto-detected from `docker-compose*.yml`, `docker-compose*.yaml`, `compose*.yml`, or `compose*.yaml` at repo root.
- Database dumps are delegated to `scripts\dbbackup_full.ps1`, which writes to repo-root `.dbbackup\`.

## Database dump contract

Canonical backup contract:

```text
DB_ENGINE + (DB_URL or DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD)
```

Supported engines:

- `mysql`
- `mariadb`
- `postgres`
- `sqlite`

Compatibility aliases are still supported for rollout, including Laravel-style `DB_DATABASE` / `DB_USERNAME`, `MYSQL_*`, and `POSTGRES_*`.

When a repo exposes multiple viable database targets, the backup script fails closed and requires:

```text
DB_BACKUP_PROFILE=<name>
```

with matching profile keys such as:

```text
DB_BACKUP_<NAME>_ENGINE
DB_BACKUP_<NAME>_URL
DB_BACKUP_<NAME>_HOST
DB_BACKUP_<NAME>_PORT
DB_BACKUP_<NAME>_NAME
DB_BACKUP_<NAME>_USER
DB_BACKUP_<NAME>_PASSWORD
DB_BACKUP_<NAME>_PATH
```

## Portable launchers

- `create_codebase.bat` is non-blocking by default. It pauses only when called with `--interactive`.
- `dockerlogs.bat` now launches the PowerShell collector `scripts\collect_docker_logs.ps1`.
- `scripts\dbbackup_full.bat` is a stable scheduler-friendly launcher for `scripts\dbbackup_full.ps1`.

## Snapshot exclusions

The workflow excludes:

- `.env`
- `.codebasebackup\`
- `.dbbackup\`
- `.dockerlogs\`
- dependency caches and build outputs
- private keys and known credential files

It then performs a text-file secret scan on copied source material and rewrites matches to `[REDACTED]`.

## Verification steps

Minimum verification after changes to the snapshot pipeline:

1. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\template_backup_standardization_smoke.ps1`
2. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\create_codebase.ps1 -SkipDb -SkipDocker` when the template repo has no live DB/Docker runtime
3. Confirm a fresh non-empty ZIP exists in `.codebasebackup\`

## Related files

- `create_codebase.bat`
- `create_codebase.ps1`
- `scripts\create_codebase_lib.ps1`
- `scripts\template_runtime.ps1`
- `scripts\dbbackup_full.ps1`
- `scripts\collect_docker_logs.ps1`
