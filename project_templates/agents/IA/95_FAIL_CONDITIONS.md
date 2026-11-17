# Fail Conditions (Quick Checklist)

These are immediate failure conditions for an implementation delivery.

## Automatic FAIL
- Secrets committed or exposed in logs or evidence.
- Required tests not run or required evidence missing from the paths specified by the AO prompt.

## High-severity failures (typically NOT APPROVED)
- Playwright/E2E executed headed (non-headless) when Playwright is used/required.
- Unrelated changes included outside task scope.
- Dirty worktree not resolved deterministically with evidence and bucket handling.
- Unrelated changes included in the delivery.
