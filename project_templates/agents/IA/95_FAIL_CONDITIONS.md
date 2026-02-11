# Fail Conditions (Quick Checklist)

These are immediate failure conditions for an implementation delivery.

## Automatic FAIL
- No new audit ZIP created by running repo-root `create_codebase.bat`.
- ZIP filename does not match: `SYSTEMPREFIX_codebase_YYYY-MM-DD_HH-mm.zip`.
- ZIP prefix does not match the expected project prefix for the audit cycle.
- `manifest/manifest.md` prefix does not match ZIP filename prefix.
- Missing mandatory folders: `/code/` or `/manifest/`.
- Missing mandatory manifest files:
  - `manifest/manifest.md`
  - `manifest/agent_final_message.md`
  - `manifest/change_summary.md`
  - `manifest/questions_for_po.md`
  - `manifest/file_inventory.txt` or `.csv`
- Secrets included in ZIP (dotenv/private keys/tokens/etc.).
- Required tests not run or evidence missing from `test-results/` (when tests are required by the AO prompt).

## High-severity failures (typically NOT APPROVED)
- Playwright/E2E executed headed (non-headless) when Playwright is used/required.
- Unrelated changes included outside task scope.
- Dirty worktree not resolved deterministically with evidence and bucket handling.
- `.zip` artifacts under `test-results/` included in the audit ZIP.
