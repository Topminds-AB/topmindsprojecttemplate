# SoT — 10 Runtime & Config

> **Purpose:** Make configuration and runtime behavior predictable across environments.
> **Rule:** List only variables actually used by this repo or required by the standard repo workflow.
> **Keep updated:** Update this file when env vars, ports, URLs, config entrypoints, or runtime commands change.

---

## 1) Environments

- **APP_ENV values used here:** `local | dev | test | staging | prod`
- **Local:**
- **Dev:**
- **Test:**
- **Staging:**
- **Prod:**

---

## 2) Configuration entrypoints

Document the exact files and processes that read configuration.

- **Root env example:** `.env.example`
- **Local secrets file:** `.env` must be gitignored and must never be included in snapshots.
- **Docker Compose:**
  - Compose file(s):
  - Profiles:
- **Backend:**
  - Path:
  - Reads from:
  - Startup command:
- **Frontend:**
  - Path:
  - Reads from:
  - Build command:
- **Worker/jobs:**
  - Path:
  - Reads from:
  - Startup command:
- **Other config files:**
  -

---

## 3) Standard repo workflow variables

These variables are part of the standard repository workflow and may be used by agents, scripts, or documentation tooling.

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| OBSIDIAN_VAULT_PATH | Agents, documentation workflow, shared skills lookup | Yes, when Obsidian integration is used | Points to the local Obsidian vault root. Example value belongs in `.env.example`; secrets do not. |

Expected `.env.example` entry:

```env
OBSIDIAN_VAULT_PATH=D:\Dropbox\Obsidian\Vaults\Topminds
```

Do not hardcode this path in scripts or documentation outside `.env.example`. Scripts must read the value from the environment or from the repo-approved config loading mechanism.

---

## 4) Core app settings

Keep only variables used by this repo. Remove unused rows when converting the template into a real repo.

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| APP_NAME |  |  |  |
| APP_ENV |  |  | `local`, `dev`, `test`, `staging`, or `prod`. |
| APP_TIMEZONE |  |  |  |
| BASE_URL |  |  |  |
| PUBLIC_BASE_URL | `scripts/purge-cloudflare.*` fallback domain detection | No | Used only if `SITE_DOMAIN` is not set. |
| SITE_DOMAIN | `scripts/purge-cloudflare.*` | No | Preferred hostname for Cloudflare zone lookup. |
| SITE_URL |  |  |  |
| DEBUG |  |  |  |
| LOG_LEVEL |  |  |  |
| TIMEOUT_SECONDS |  |  |  |
| SESSION_LIFETIME_MINUTES |  |  |  |

---

## 5) Database settings

### 5.1 Primary database

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| DB_ENGINE | `scripts/dbbackup_full.ps1` | Yes when a repo has a DB | `mysql`, `mariadb`, `postgres`, or `sqlite`. |
| DB_URL | `scripts/dbbackup_full.ps1` | No | Canonical connection string for the active backup target. |
| DB_HOST | `scripts/dbbackup_full.ps1` | No | Use with split DB credentials when `DB_URL` is absent. |
| DB_PORT | `scripts/dbbackup_full.ps1` | No |  |
| DB_NAME | `scripts/dbbackup_full.ps1` | No |  |
| DB_USER | `scripts/dbbackup_full.ps1` | No |  |
| DB_PASSWORD | `scripts/dbbackup_full.ps1` | No | Secret. Must never be committed. |
| DB_PATH | `scripts/dbbackup_full.ps1` | No | SQLite file path when `DB_ENGINE=sqlite`. |
| DB_BACKUP_PROFILE | `scripts/dbbackup_full.ps1` | No | Required when the repo exposes multiple viable DB targets. |
| DB_SSL_MODE | `scripts/dbbackup_full.ps1` | No |  |

### 5.2 Local/dev database

Use `MYSQL_*` for local MySQL. Use `POSTGRES_*` for local PostgreSQL. These remain compatibility aliases and are not the canonical backup contract.

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| MYSQL_HOST |  |  |  |
| MYSQL_PORT |  |  |  |
| MYSQL_DATABASE |  |  |  |
| MYSQL_USER |  |  |  |
| MYSQL_PASSWORD |  |  | Secret. Must never be committed. |
| POSTGRES_HOST |  |  |  |
| POSTGRES_PORT |  |  |  |
| POSTGRES_DB |  |  |  |
| POSTGRES_USER |  |  |  |
| POSTGRES_PASSWORD |  |  | Secret. Must never be committed. |

---

## 6) Cache and sessions

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| REDIS_HOST |  |  |  |
| REDIS_PORT |  |  |  |
| REDIS_PASSWORD |  |  | Secret. Must never be committed. |
| REDIS_URL |  |  | Secret if it contains credentials. |
| SESSION_STORE |  |  | `cookie`, `redis`, `db`, or documented repo-specific value. |

---

## 7) Email

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| MAIL_FROM_NAME |  |  |  |
| MAIL_FROM_ADDRESS |  |  |  |
| SMTP_HOST |  |  |  |
| SMTP_PORT |  |  |  |
| SMTP_USER |  |  |  |
| SMTP_PASSWORD |  |  | Secret. Must never be committed. |
| SMTP_SECURE |  |  | `none`, `starttls`, or `ssl`. |

---

## 8) AI configuration

If this repo uses AI, list provider and routing variables actually referenced in code. Remove provider sections that are not used.

### 8.1 Routing

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| AI_PROVIDER_DEFAULT |  |  | `openai`, `anthropic`, `google`, `perplexity`, `xai`, `ollama`, or documented repo-specific value. |
| AI_MODEL_DEFAULT |  |  |  |
| AI_REQUEST_TIMEOUT_SECONDS |  |  |  |
| AI_RETRIES |  |  |  |

### 8.2 Providers

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| OPENAI_API_KEY |  |  | Secret. Must never be committed. |
| OPENAI_DEFAULT_MODEL |  |  |  |
| OPENAI_EMBEDDINGS_MODEL |  |  |  |
| ANTHROPIC_API_KEY |  |  | Secret. Must never be committed. |
| ANTHROPIC_DEFAULT_MODEL |  |  |  |
| GOOGLE_AI_API_KEY |  |  | Secret. Must never be committed. |
| GOOGLE_AI_DEFAULT_MODEL |  |  |  |
| PERPLEXITY_API_KEY |  |  | Secret. Must never be committed. |
| PERPLEXITY_DEFAULT_MODEL |  |  |  |
| XAI_API_KEY |  |  | Secret. Must never be committed. |
| XAI_DEFAULT_MODEL |  |  |  |
| OLLAMA_HOST |  |  |  |
| OLLAMA_DEFAULT_MODEL |  |  |  |
| KBWHISPER_HOST |  |  |  |
| KBWHISPER_MODEL |  |  |  |
| KBWHISPER_LANGUAGE |  |  |  |

---

## 9) Storage

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| STORAGE_DRIVER |  |  | `local`, `s3`, `gcs`, `azure`, or documented repo-specific value. |
| STORAGE_LOCAL_PATH |  |  |  |
| STORAGE_PUBLIC_URL |  |  |  |
| S3_ENDPOINT |  |  | Required only when S3-compatible storage is used. |
| S3_REGION |  |  |  |
| S3_BUCKET |  |  |  |
| S3_ACCESS_KEY_ID |  |  | Secret. Must never be committed. |
| S3_SECRET_ACCESS_KEY |  |  | Secret. Must never be committed. |

---

## 10) Ports and endpoints

List effective values for this repo.

- **Backend:**
- **Frontend:**
- **Database:**
- **Redis:**
- **Ollama:**
- **KBWhisper:**
- **Other:**

---

## 11) Snapshot expectations

- `.env` is never included in snapshots.
- `.env.example` is included.
- Config files containing secrets must be excluded by `create_codebase`.
- `create_codebase.ps1` derives project identity from repo truth and delegates DB dumps to `scripts/dbbackup_full.ps1`.
- `scripts/dbbackup_full.ps1` writes to repo-root `.dbbackup\` and retains successful artifacts for 10 days by default.
- Snapshot behavior and standard backup folders are documented in `docs/SoT/50_standard_tooling_and_snapshots.md`.

---

## 12) Cloudflare cache purge support

The repo-level helpers `scripts/purge-cloudflare.ps1` and `scripts/purge-cloudflare.sh` read Cloudflare credentials from the repo `.env` by default.

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| CLOUDFLARE_API_TOKEN | `scripts/purge-cloudflare.*` | Yes | Primary token source for Cloudflare purge requests. |
| CLOUDFLARE_ZONE_ID | `scripts/purge-cloudflare.*` | No | Optional optimization. If absent, the script resolves the zone from `SITE_DOMAIN`. |

The reserve token path must not be hardcoded in repo config. The scripts resolve it from `OBSIDIAN_VAULT_PATH/_keys/Cloudflare.md` only when the explicit reserve-token switch is used.

---

## 13) Change log for config

Add a short note each time env var usage, ports, URLs, or config loading changes.

- 2026-05-29: Added repo-local Cloudflare purge script variables and reserve-token routing via `OBSIDIAN_VAULT_PATH`.
- 2026-06-29: Added canonical backup contract `DB_ENGINE + DB_URL|DB_HOST...`, multi-target profile support via `DB_BACKUP_PROFILE`, and repo-root `.dbbackup\` handling for the shared template scripts.
- YYYY-MM-DD:
