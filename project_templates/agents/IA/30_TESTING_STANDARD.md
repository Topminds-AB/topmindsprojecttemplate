# Testing Standard (Mandatory)

## Test selection principle (always apply)
- Prefer the simplest effective test that validates acceptance criteria (unit/integration/API) when sufficient.
- Use Playwright (or equivalent E2E) **only** when unique E2E capabilities are required:
  - UI flows
  - screenshots / traces
  - browser-level behavior
- When E2E is required, it must be Playwright (or equivalent) and must be headless.

## Headless enforcement (critical)
- Playwright MUST run headless.
- It must not open browser windows.
- Enforce via config (`headless: true`) or CLI flags/env (explicitly documented).

## Evidence location (fixed structure)
All test evidence must be under:
- `test-results/`

Required subfolders:
- `test-results/unit/`
- `test-results/integration/`
- `test-results/e2e/`
- `test-results/summary.md` (single human-readable summary)

## Summary requirements (`test-results/summary.md`)
Must include:
- what was tested (unit/integration/e2e)
- exact commands executed (copy-pasteable)
- pass/fail counts
- where raw artifacts live (relative paths under `test-results/`)
- if any test skipped: reason + impact assessment
- confirmation Playwright was headless + how enforced

## ZIP exclusion rule for huge test-report ZIPs
To keep audit ZIP small:
- Any `.zip` files located anywhere under `test-results/` MUST be excluded from the audit ZIP.
- Reports still must be generated under `test-results/` — just don’t package `.zip` artifacts from that subtree.
