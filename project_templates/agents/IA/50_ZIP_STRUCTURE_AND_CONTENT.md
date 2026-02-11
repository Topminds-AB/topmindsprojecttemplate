# Audit ZIP — Required Structure & Content

## ZIP must be produced by repo-root `create_codebase.bat`
No alternative packaging is accepted unless explicitly approved by AO.

## Top-level folders (some conditional)
- `/code/` (MANDATORY)
- `/manifest/` (MANDATORY)
- `/dbbackup/` (MANDATORY if a DB exists)
- `/dockerlogs/` (MANDATORY if Docker is used)
- `/logs/` (OPTIONAL; only if meaningful)
- `/vectordbdump/` (OPTIONAL; only if a vector DB exists)

## `/code/` must include
Everything needed to review behavior/implementation:
- source code
- schema definitions + migrations
- docker compose files, Dockerfiles
- documentation (PRD/SoT/architecture/runbooks)
- test suites (unit/integration/e2e)
- helper scripts invoked by `create_codebase.bat`

### Safe-to-exclude (always)
- `.git/`
- `node_modules/`
- `dist/`, `build/`, `out/` (unless intentionally committed and justified)
- `.next/`, `.cache/`, `tmp/`, `temp/`
- `__pycache__/`, `*.pyc`
- `venv/`, `.venv/`
- `.pytest_cache/`, `.mypy_cache/`
- `.idea/`, `.vscode/` (except shared policy settings; justify)
- OS noise: `Thumbs.db`, `Desktop.ini`

## `/dbbackup/` (if DB exists)
- Prefer full DB dump via `dbbackup_full.bat` if present.
- Must include schema + data OR schema-only + clearly labeled seed dataset used for tests.
- Must NOT include credentials.

## `/dockerlogs/` (if Docker used)
- Follow repo-root `dockerlogs.bat` if present.
- Must include:
  - compose logs (all services)
  - container status snapshot (`docker ps`) if available

## `/logs/` (optional)
Include only meaningful logs not already in dockerlogs:
- API smoke logs
- migration logs
- other diagnostic logs required for verification

## `/vectordbdump/` (optional)
- Include dump/export sufficient to inspect collections/indexes and sample records.
- If huge: include metadata/schema + minimal sample; explain in manifest.
