# SoT — 70 Test Governance

> **Purpose:** Define the repo-local adapter for governed testing.  
> **Canonical rule:** Obsidian is the source of truth: `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/07-test-and-evidence-standard.md`.

---

## 1) Canonical source

- Repo-local files in `docs/TESTING/` are working copies and local truth for this repo.
- The normative cross-repo policy lives in Obsidian.
- Agents must not invent weaker local rules than the Obsidian standard.

---

## 2) Required local files

- `docs/TESTING/TEST-STRATEGY.md`
- `docs/TESTING/TEST-CATALOG.md`
- `docs/TESTING/TEST-LOG.md`

---

## 3) Required workflow

For every new governed test:

1. Register the test in `docs/TESTING/TEST-CATALOG.md`.
2. Create the test.
3. Run the first qualifying execution red before implementation when the behavior is not yet correct.
4. Record that execution in `docs/TESTING/TEST-LOG.md`.
5. Implement only after the red baseline is captured.
6. Record later meaningful runs in the log with the latest run first.

---

## 4) Forbidden patterns

- mocks
- stubs
- fixtures
- fake integrations
- synthetic business data
- post-implementation tests presented as test-first
- governed test runs omitted from the log

Any exception requires an ADR-approved deviation.

---

## 5) Standard categories

Use these category labels when they fit:

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
