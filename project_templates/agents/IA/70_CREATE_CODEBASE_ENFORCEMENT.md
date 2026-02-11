# create_codebase.bat Enforcement (Mandatory)

## Absolute rule: ZIP delivery is non-negotiable
If a ZIP snapshot is not created by running repo-root `create_codebase.bat`, the delivery is an automatic **FAIL**.

## Requirements
- Repo must contain a repo-root `create_codebase.bat`.
- If missing:
  - search for existing create_codebase variants
  - create/align behavior deterministically to match repo needs
- `create_codebase.bat` must produce:
  - correct top-level folder structure
  - required manifests and inventories
  - required logs/DB dumps/docker logs when applicable
  - exclusions (including mandatory exclusion of `.zip` under `test-results/`)
  - no secrets

## Execution evidence
`manifest/manifest.md` must include:
- the exact command used to run `create_codebase.bat`
- any additional scripts invoked (dbbackup/dockerlogs/etc.)
