# SoT — 10 Runtime & Config
> **Purpose:** Make configuration and runtime behavior predictable across environments.  
> **Rule:** List only variables actually used by this repo (subset of `.env.example`).  
> **Keep updated:** When adding/removing env vars or changing ports/URLs.

---

## 1) Environments
- **APP_ENV values used here:** `local | dev | test | staging | prod`
- **What changes per environment:**
  - Local:
  - Dev:
  - Prod:

---

## 2) Entrypoints (where config is read)
> Document the exact files/processes that read env vars.

- **Backend:** (e.g. `services/api/`, framework, entry file)
  - Reads from:
  - Startup command:
- **Frontend:** (if any)
  - Reads from:
  - Build command:
- **Worker / jobs:** (if any)
  - Reads from:
  - Startup command:
- **Docker Compose:** (if used)
  - Compose file(s):
  - Profiles (if any):

---

## 3) Core app settings (APP_*)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| APP_NAME |  |  |  |
| APP_ENV |  |  |  |
| APP_TIMEZONE |  |  |  |
| BASE_URL |  |  |  |
| SITE_URL |  |  |  |
| DEBUG |  |  |  |
| LOG_LEVEL |  |  |  |
| TIMEOUT_SECONDS |  |  |  |
| SESSION_LIFETIME_MINUTES |  |  |  |

---

## 4) Database settings
### 4.1 Production/primary DB (DB_*)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| DB_ENGINE |  |  | mysql/postgres/etc |
| DB_HOST |  |  |  |
| DB_PORT |  |  |  |
| DB_NAME |  |  |  |
| DB_USER |  |  |  |
| DB_PASSWORD |  |  |  |
| DB_SSL_MODE |  |  |  |

### 4.2 Local/dev DB (MYSQL_* or POSTGRES_*)
> Use `MYSQL_*` for local MySQL (common in compose). If you use Postgres locally, document `POSTGRES_*` too.

| Variable | Used by | Required | Notes |
|---|---|---:|---|
| MYSQL_HOST |  |  |  |
| MYSQL_PORT |  |  |  |
| MYSQL_DATABASE |  |  |  |
| MYSQL_USER |  |  |  |
| MYSQL_PASSWORD |  |  |  |

---

## 5) Cache / sessions (REDIS_*)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| REDIS_HOST |  |  |  |
| REDIS_PORT |  |  |  |
| REDIS_PASSWORD |  |  |  |
| REDIS_URL |  |  |  |
| SESSION_STORE |  |  | cookie/redis/db |

---

## 6) Email (SMTP_*)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| MAIL_FROM_NAME |  |  |  |
| MAIL_FROM_ADDRESS |  |  |  |
| SMTP_HOST |  |  |  |
| SMTP_PORT |  |  |  |
| SMTP_USER |  |  |  |
| SMTP_PASSWORD |  |  |  |
| SMTP_SECURE |  |  | none/starttls/ssl |

---

## 7) AI configuration (subset used)
> If the repo uses AI, list provider + routing variables actually referenced in code.

### 7.1 Routing
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| AI_PROVIDER_DEFAULT |  |  | openai/anthropic/google/perplexity/grok/ollama |
| AI_MODEL_DEFAULT |  |  |  |
| AI_REQUEST_TIMEOUT_SECONDS |  |  |  |
| AI_RETRIES |  |  |  |

### 7.2 Providers used in this repo
> Fill the sections you actually use; delete the rest.

#### OpenAI
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| OPENAI_API_KEY |  |  |  |
| OPENAI_DEFAULT_MODEL |  |  |  |
| OPENAI_EMBEDDINGS_MODEL |  |  |  |

#### Anthropic
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| ANTHROPIC_API_KEY |  |  |  |
| ANTHROPIC_DEFAULT_MODEL |  |  |  |

#### Google AI (Gemini)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| GOOGLE_AI_API_KEY |  |  |  |
| GOOGLE_AI_DEFAULT_MODEL |  |  |  |

#### Perplexity
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| PERPLEXITY_API_KEY |  |  |  |
| PERPLEXITY_DEFAULT_MODEL |  |  |  |

#### xAI (Grok)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| XAI_API_KEY |  |  |  |
| XAI_DEFAULT_MODEL |  |  |  |

#### Local AI (Ollama)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| OLLAMA_HOST |  |  |  |
| OLLAMA_DEFAULT_MODEL |  |  |  |

#### Local AI (KBWhisper)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| KBWHISPER_HOST |  |  |  |
| KBWHISPER_MODEL |  |  |  |
| KBWHISPER_LANGUAGE |  |  |  |

---

## 8) Storage (subset used)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| STORAGE_DRIVER |  |  | local/s3/gcs/azure |
| STORAGE_LOCAL_PATH |  |  |  |
| STORAGE_PUBLIC_URL |  |  |  |

### S3 (if used)
| Variable | Used by | Required | Notes |
|---|---|---:|---|
| S3_ENDPOINT |  |  |  |
| S3_REGION |  |  |  |
| S3_BUCKET |  |  |  |
| S3_ACCESS_KEY_ID |  |  |  |
| S3_SECRET_ACCESS_KEY |  |  |  |

---

## 9) Ports and endpoints (effective values)
> List what actually runs where, so it’s trivial to verify.

- **Backend:** host:port → 
- **Frontend:** host:port → 
- **DB local:** host:port → 
- **Redis:** host:port → 
- **Ollama:** URL → 
- **KBWhisper:** URL → 

---

## 10) Snapshot expectations (config perspective)
- `.env` is **never** included in snapshots.
- `.env.example` **is** included.
- Any config files containing secrets must be excluded by `create_codebase`.

---

## 11) Change log for config
> Add a short note each time you change env var usage.

- YYYY-MM-DD: 
