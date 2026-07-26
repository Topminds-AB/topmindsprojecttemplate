# Mock Registry

> Purpose: keep an auditable, searchable inventory of every explicitly permitted mock, fake, fixture, seed, placeholder, or simulated integration path in this repo.

## Canonical split

- Cross-repo policy lives in Obsidian:
  - `<OBSIDIAN_VAULT_PATH>/_system/dev-standards/core/10-mock-registry-standard.md`
- Repo-local working files live here:
  - `docs/SoT/mock-registry.jsonl`
  - `docs/SoT/mock.md`

## Current status

- `docs/SoT/mock-registry.jsonl` is the machine-friendly source for this repo.
- `docs/SoT/mock.md` is the human-readable guide.
- New repos should start with an empty registry and add entries only when mock usage is explicitly approved.

## Required fields

Each JSON line in `docs/SoT/mock-registry.jsonl` must contain:

- `mock_repo`
- `mock_id`
- `mock_title`
- `mock_type`
- `mock_scope`
- `mock_status`
- `mock_description`
- `mock_reason`
- `mock_file_name`
- `mock_file_path`
- `mock_file_row_start`
- `mock_file_row_end`
- `mock_timestamp`
- `mock_created_by`
- `mock_removal_condition`

## Recommended fields

- `mock_review_at`
- `mock_linked_issue_or_adr`
- `mock_tags`
- `mock_notes`

## Allowed values

- `mock_type`: `file`, `db-row`, `db-seed`, `api-response`, `image`, `ui-placeholder`, `fixture`, `test-double`, `generated-content`, `static-json`, `static-csv`, `other`
- `mock_scope`: `test`, `dev`, `demo`, `staging`, `migration`, `bootstrap`, `docs`, `benchmark`, `other`
- `mock_status`: `active`, `retired`

## Rules

1. Hidden mocks are forbidden.
2. If a mock is explicitly permitted, register it in the same change.
3. `mock_file_row_start` and `mock_file_row_end` must point to the real location in the file.
4. If automated tests use mock or fake data, the entry must link the approved ADR or deviation because repo test governance forbids that by default.
5. When a mock is removed, keep the entry and change `mock_status` to `retired`.
6. `mock_timestamp` is the last time the entry itself was updated, in ISO 8601 format.

## JSONL template

```json
{"mock_repo":"llm-wiki","mock_id":"mock-2026-06-03-001","mock_title":"Short title","mock_type":"file","mock_scope":"dev","mock_status":"active","mock_description":"What the mock is and what it stands in for.","mock_reason":"Why it is temporarily allowed.","mock_file_name":"relative-file.ext","mock_file_path":"relative/path/to/relative-file.ext","mock_file_row_start":1,"mock_file_row_end":1,"mock_timestamp":"2026-06-03T12:00:00+02:00","mock_created_by":"agent","mock_removal_condition":"Remove when real path exists.","mock_review_at":"2026-06-10","mock_linked_issue_or_adr":"ADR-20260603-example","mock_tags":["mock","temporary"],"mock_notes":"Optional extra note."}
```

## Search examples

```powershell
rg -n "\"mock_status\":\"active\"" docs/SoT/mock-registry.jsonl
rg -n "\"mock_scope\":\"test\"" docs/SoT/mock-registry.jsonl
rg -n "\"mock_file_path\":\"src/example.ts\"" docs/SoT/mock-registry.jsonl
```
