# Branch Naming & Workflow (Mandatory)

## Core rules
- Never work directly on `main`/`master`.
- Every task/phase must be implemented on a dedicated task branch.
- Keep history auditable; do not rewrite away work.

## Required branch types
### Task branches (Bucket A)
Use one of:
- `fix/<short-description>`
- `feature/<short-description>`
- `chore/<short-description>` (only for packaging/docs required by the AO prompt)

Task branches must contain **only** changes required for the current AO-defined scope.

### Salvage branches (Bucket B)
- `salvage/<short-description>`
Use salvage branches only to preserve legitimate unrelated work discovered in a dirty worktree.

## Commit policy
- Commit logically grouped changes.
- Do not bundle unrelated files into one commit.
- Avoid rebasing that discards evidence; prefer merges that preserve auditability.

## After dirty-worktree bucket handling
- Task branch contains only Bucket A commits.
- Bucket B is isolated in salvage branch(es).
- Bucket C is cleaned only when truly generated noise, with explicit documentation in manifest files.
