# TEST-CATALOG

Register each governed test before implementation starts.

## Required fields

Every test entry must include:

- `test_id`
- `title`
- `category`
- `level`
- `goal_or_requirement`
- `feature_or_behavior`
- `created_at`
- `created_by`
- `created_before_implementation`
- `first_run_command`
- `first_run_at`
- `first_run_result`
- `current_status`
- `runtime_or_dependencies`
- `forbidden_shortcuts`
- `test_file`
- `linked_sources`

## Entry template

```md
### <TEST-ID> - <Title>

- `test_id`:
- `title`:
- `category`:
- `level`:
- `goal_or_requirement`:
- `feature_or_behavior`:
- `created_at`:
- `created_by`:
- `created_before_implementation`: yes
- `first_run_command`:
- `first_run_at`:
- `first_run_result`: red
- `current_status`: planned
- `runtime_or_dependencies`:
- `forbidden_shortcuts`:
- `test_file`:
- `linked_sources`:
```

### T-BTPL-001 - Portable template backup entrypoints

- `test_id`: `T-BTPL-001`
- `title`: `Portable template backup entrypoints`
- `category`: `smoke-runtime`
- `level`: `repo-template`
- `goal_or_requirement`: `Template backup helpers must run in repos without repo-specific code edits.`
- `feature_or_behavior`: `Shared helper, non-blocking launchers, and portable docker log entrypoint exist and replace hardcoded template-specific assumptions.`
- `created_at`: `2026-06-29 16:24`
- `created_by`: `Codex`
- `created_before_implementation`: yes
- `first_run_command`: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\template_backup_standardization_smoke.ps1`
- `first_run_at`: `2026-06-29 16:24`
- `first_run_result`: `red`
- `current_status`: `green`
- `runtime_or_dependencies`: `PowerShell 5.1+, repo root files under project_templates`
- `forbidden_shortcuts`: `Do not bypass the launcher files, do not hand-edit test output, do not treat hardcoded repo identity as acceptable.`
- `test_file`: `tests/template_backup_standardization_smoke.ps1`
- `linked_sources`: `create_codebase.ps1`, `create_codebase.bat`, `dockerlogs.bat`, `scripts/dbbackup_full.bat`, `scripts/dbbackup_full.ps1`, `scripts/template_runtime.ps1`

### T-BTPL-002 - Universal dbbackup contract

- `test_id`: `T-BTPL-002`
- `title`: `Universal dbbackup contract`
- `category`: `smoke-runtime`
- `level`: `repo-template`
- `goal_or_requirement`: `Template db backup flow must support canonical DB contract plus compatibility aliases across engines.`
- `feature_or_behavior`: `dbbackup entrypoint delegates to a PowerShell engine that supports mysql, mariadb, postgres, and sqlite with repo-root output and retention metadata.`
- `created_at`: `2026-06-29 16:24`
- `created_by`: `Codex`
- `created_before_implementation`: yes
- `first_run_command`: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\template_backup_standardization_smoke.ps1`
- `first_run_at`: `2026-06-29 16:24`
- `first_run_result`: `red`
- `current_status`: `green`
- `runtime_or_dependencies`: `PowerShell 5.1+, repo root template files`
- `forbidden_shortcuts`: `Do not keep MySQL-only batch logic, do not write dumps under scripts\.dbbackup, do not silently guess among multiple DB targets.`
- `test_file`: `tests/template_backup_standardization_smoke.ps1`
- `linked_sources`: `scripts/dbbackup_full.bat`, `scripts/dbbackup_full.ps1`, `.env.example`, `docs/SoT/10_runtime_and_config.md`

### T-BTPL-003 - Portable create_codebase workflow

- `test_id`: `T-BTPL-003`
- `title`: `Portable create_codebase workflow`
- `category`: `smoke-runtime`
- `level`: `repo-template`
- `goal_or_requirement`: `Template snapshot tooling must derive repo identity and DB/Docker behavior from repo truth instead of hardcoded template config.`
- `feature_or_behavior`: `create_codebase uses shared helper, avoids hardcoded DPDR identity, keeps file size within the repo soft limit by moving helper logic out.`
- `created_at`: `2026-06-29 16:24`
- `created_by`: `Codex`
- `created_before_implementation`: yes
- `first_run_command`: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\template_backup_standardization_smoke.ps1`
- `first_run_at`: `2026-06-29 16:24`
- `first_run_result`: `red`
- `current_status`: `green`
- `runtime_or_dependencies`: `PowerShell 5.1+, repo root template files`
- `forbidden_shortcuts`: `Do not keep hardcoded repo identity, do not keep unconditional pause, do not leave create_codebase.ps1 above the soft file-size limit.`
- `test_file`: `tests/template_backup_standardization_smoke.ps1`
- `linked_sources`: `create_codebase.ps1`, `create_codebase.bat`, `create_codebase.md`, `docs/SoT/50_standard_tooling_and_snapshots.md`
