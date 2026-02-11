# Git Discipline — Dirty Worktree Handling (Mandatory)

## Absolute rule
You are **not allowed** to “ignore and continue.”  
If the repo is dirty (modified/untracked files), you must make it clean **without losing anything**, and produce evidence in the next audit ZIP.

## Step A — Inventory first (no guessing)
Run:
- `git status --porcelain=v1`
- `git diff --stat`
- `git diff`
- `git diff --cached`

Save outputs (must be included in next audit ZIP):
- `logs/git_status_porcelain.txt`
- `logs/git_diff_stat.txt`
- `logs/git_diff.txt`
- `logs/git_diff_cached.txt`

## Step B — Classify every change into exactly one bucket
- **Bucket A:** Required for *this* task.
- **Bucket B:** Not required for this task but legitimate work (previous/parallel).
- **Bucket C:** Generated noise (caches, build outputs, temp files, local logs).

## Step C — Nothing may be silently discarded
- Bucket A: keep, commit in the **task branch**.
- Bucket B: isolate:
  - create `salvage/<short-description>` branch
  - commit Bucket B there
  - return to the task branch
- Bucket C: delete/clean only if truly generated; if removed it must be:
  - listed in `manifest/change_summary.md`
  - explained in `manifest/agent_final_message.md`
  - excluded by ZIP packaging rules (where applicable)

## Step D — Branch workflow (mandatory)
- Create a dedicated task branch: `fix/<short-description>` (or similar).
- After buckets handled:
  - task branch contains **only Bucket A** commits
  - salvage branches contain **only Bucket B**
- Do **not** rebase away history; keep commits auditable.

## Step E — Required audit evidence in ZIP
Include:
- the four git evidence files above (Step A)
- `manifest/change_summary.md` listing:
  - Bucket A changed files
  - salvage branch name(s) for Bucket B
  - Bucket C cleaned files + rationale
- `manifest/agent_final_message.md` must explicitly state:
  - “Worktree was dirty at start”
  - bucket decisions
  - branches created
  - commits created (hash + message)
