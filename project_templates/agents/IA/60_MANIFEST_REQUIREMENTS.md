# Manifest Requirements (Mandatory)

All manifest files must be inside `/manifest/`.

## Required files
### `manifest/manifest.md`
Must include:
- system prefix used
- expected project prefix for this snapshot (must match ZIP filename prefix)
- exact commands executed to create ZIP (including `create_codebase.bat`)
- which backup/log scripts were invoked
- DB engine and connection method used (no secrets)
- services included in dockerlogs
- tests executed (commands) + where outputs are stored
- declared exclusions (what was not included and why), including:
  - mandatory exclusion of `.zip` files under `test-results/`

### `manifest/file_inventory.txt` (or `.csv`)
- flat list of all ZIP members with sizes (paths normalized to `/`)

### `manifest/change_summary.md`
- what changed since previous snapshot (if known): file list + brief reason
- include dirty-worktree bucket outcomes when applicable (see Git rules)

### `manifest/agent_final_message.md`
- your final message (standalone inside ZIP):
  - what changed (exact paths)
  - what you verified
  - commands run
  - where evidence is stored

### `manifest/questions_for_po.md`
- must always exist (see questions protocol file)
