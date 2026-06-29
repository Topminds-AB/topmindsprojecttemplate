# TEST-STRATEGY

## Canonical rule

This repo follows the canonical Obsidian standard:

`<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md`

## Local paths

- Strategy: `docs/TESTING/TEST-STRATEGY.md`
- Catalog: `docs/TESTING/TEST-CATALOG.md`
- Log: `docs/TESTING/TEST-LOG.md`
- Repo-local adapter: `docs/SoT/70_test_governance.md`

## Required governance

- Tests must be defined before implementation.
- New governed tests must be registered in `TEST-CATALOG.md` before implementation.
- The first qualifying run for new behavior must be red when the behavior is not yet correct.
- The red run must be recorded in `TEST-LOG.md`.
- Automated tests must not use mocks, stubs, fixtures, fake integrations, or synthetic business data unless an ADR-approved deviation exists.

## Project categories

Use the relevant subset of:

- `frontend-ui`
- `frontend-component`
- `api-contract`
- `backend-unit`
- `backend-integration`
- `database-migration`
- `smoke-runtime`
- `e2e-browser`
- `security-config`
- `import-data`
- `ai-provider-boundary`
- `human-validation`

## Commands

- Primary test command(s):
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\template_backup_standardization_smoke.ps1`
- Smoke command(s):
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dbbackup_full.ps1 -SkipIfUnconfigured`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\collect_docker_logs.ps1`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\create_codebase.ps1`
- Browser E2E command(s), if relevant:
  -

## Runtime targets

- Authoritative runtime for verification:
  - `E:\projects\teamtopminds\project_templates`
- Allowed local fallback, if any:
  - `cmd /c create_codebase.bat -SkipDb -SkipDocker`

## Human validation boundary

- Human-only checks:
  -
