# TEST-LOG

Record meaningful test executions here with the newest run first.

## Entry template

```md
## <YYYY-MM-DD HH:MM> - <actor> - <result>

- `test_ids`:
- `category`:
- `command`:
- `runtime_target`:
- `result`:
- `artifacts`:
- `note`:
```

## Latest runs

Add the newest entry directly under this heading.

## 2026-07-28 17:51 - Codex - green

- `test_ids`: `T-BTPL-004`, `T-BTPL-001`, `T-BTPL-002`, `T-BTPL-003`
- `category`: `security-config`, `smoke-runtime`
- `command`: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\codex_startup_distribution_smoke.ps1`; official `skills-ref validate` for four distributed skill bundles; ephemeral read-only `codex exec --strict-config`; `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\template_backup_standardization_smoke.ps1`
- `runtime_target`: `E:\projects\teamtopminds\project_templates`
- `result`: `green`
- `artifacts`: `The template contains 26-file repo-user-documentation and 13-file system-docs-domain bundles for each client; all four bundles validate; the real Codex startup emitted none of the targeted warnings; existing template smoke passed.`
- `note`: `Point rollout requires .codex/config.toml plus the four complete skill directories. Internal test and evidence files do not need to be copied to older repositories solely for the warning fix.`

## 2026-07-28 17:47 - Codex - red

- `test_ids`: `T-BTPL-004`
- `category`: `security-config`
- `command`: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\codex_startup_distribution_smoke.ps1`
- `runtime_target`: `E:\projects\teamtopminds\project_templates`
- `result`: `red`
- `artifacts`: `The template still used deprecated features.codex_hooks and did not contain the repo-user-documentation or system-docs-domain bundles under either client distribution path.`
- `note`: `Expected qualifying red baseline captured before adding the corrected distribution files.`

## 2026-06-29 16:39 - Codex - green

- `test_ids`: `T-BTPL-001`, `T-BTPL-002`, `T-BTPL-003`
- `category`: `smoke-runtime`
- `command`: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\template_backup_standardization_smoke.ps1`; `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dbbackup_full.ps1 -SkipIfUnconfigured`; `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\collect_docker_logs.ps1`; `powershell -NoProfile -ExecutionPolicy Bypass -File .\create_codebase.ps1`; `cmd /c scripts\dbbackup_full.bat -SkipIfUnconfigured`; `cmd /c dockerlogs.bat`; `cmd /c create_codebase.bat -SkipDb -SkipDocker`
- `runtime_target`: `E:\projects\teamtopminds\project_templates`
- `result`: `green`
- `artifacts`: `Smoke test passed; dbbackup PowerShell and .bat launchers skipped cleanly without DB config; docker log PowerShell and .bat launchers skipped cleanly without compose files; create_codebase PowerShell and .bat launchers produced verified ZIP E:\projects\teamtopminds\project_templates\.codebasebackup\PROJECT_TEMPLATES_codebase_2026-06-29_16-39.zip`
- `note`: `Template-only phase verified after helper/dbbackup/create_codebase standardization.`

## 2026-06-29 16:24 - Codex - red

- `test_ids`: `T-BTPL-001`, `T-BTPL-002`, `T-BTPL-003`
- `category`: `smoke-runtime`
- `command`: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\template_backup_standardization_smoke.ps1`
- `runtime_target`: `E:\projects\teamtopminds\project_templates`
- `result`: `red`
- `artifacts`: `Expected red baseline before implementation; current template still lacks shared helper, PowerShell dbbackup engine, portable dockerlogs entrypoint, and non-hardcoded create_codebase defaults.`
- `note`: `Governed baseline captured before changing template backup and snapshot scripts.`
