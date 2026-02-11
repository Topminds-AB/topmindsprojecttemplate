# Secrets Handling (Mandatory)

## The ZIP must not contain secrets
Examples (non-exhaustive):
- `.env`
- `*.pem`, private keys, `id_rsa`
- service account JSON
- access tokens, kubeconfig
- any credentials files

If secrets are detected: **CRITICAL failure**.

## Immediate containment actions
- Add the exact secret-bearing filename/pattern to repo-root **`.gitignore`** so it is not reintroduced.
- If the secret file is already tracked by git:
  - stop and clean it properly before proceeding
  - do not commit further changes until secrets are resolved

## Evidence without leaking secrets
You may report only:
- file path
- category-level reason (e.g., “dotenv credentials”, “private key”, “token”)

Do **not** paste secret values into logs, manifests, or messages.

## History cleanup rule
If a secret is committed in any branch (including salvage):
- it **must** be removed from that branch’s history before pushing/merging
- prefer `git filter-repo` (or equivalent)
- document steps in `manifest/agent_final_message.md` **without** revealing secret values
- if force-push is required, state it explicitly
