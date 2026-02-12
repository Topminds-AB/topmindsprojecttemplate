# Project Overview - Template v.1.0.

**System version:** <SYSTEM_VERSION>  
**Documentation version:** <DOC_VERSION>  
**Repo snapshot / artifact:** `rss_codebase_2026-02-10_07-55.zip`  
**Last updated:** 2026-02-10  
**Audience:** New developers working in this repository (human + IA agents)  
**Delivery model:** PO → OA (orchestrator) → IA (implementation)  

---

## 0. TL;DR (Read this first)

**ReportForge** is a Dockerized web application that supports field professionals by converting recorded speech into structured, template-driven reports.

- **Primary value:** upload/record → transcription → LLM processing → professional report output
- **Core UI areas:** Home, Templates, Uploads, Projects, Capture, Admin, Profile, Audit
- **Local dev:** `docker_compose_up.bat` (Nginx + PHP-FPM + MySQL + phpMyAdmin)
- **Production deploy:** Loopia FTP deploy scripts in `/scripts/` and `deploy_loopia.bat`
- **Authoritative documents:** `/docs/PRD/` + `/docs/SoT/` + `/docs/implementation/`

### 0.1 Glossary

- **TL;DR:** “Too Long; Didn’t Read” — fast onboarding overview.
- **DoD:** “Definition of Done” — the acceptance criteria for completing work.
- **PO:** Product Owner — controls scope and priorities for OA/IA.
- **OA:** Orchestration Agent — coordinates work and instructs IA using PRD/SoT/Plan.
- **IA:** Implementation Agent — performs code changes in the repository.
- **Tenant / Customer:** the top-level organization boundary in the multi-tenant model.
- **Project:** belongs to a customer; used for scoping recordings/templates/access.
- **Capture:** the recording/capture module (web UI under `/capture` + REST API under `/api/capture/*`).

### 0.2 Definition of Done (DoD) — repo work

Work is considered “Done” when all items below are true:

- Scope matches PRD/SoT and is phase-aligned (if phases are used).
- No secrets are added to repo or artifacts.
- Required tests are executed and results are captured as evidence.
- Evidence artifacts are produced (screenshots / HTML dumps / logs / LOC report) as required by the phase.
- Documentation is updated if the change impacts: user flows, endpoints, schema, integrations, or deployment.

---

## 1. Purpose & goals

### 1.1 Problem statement

Field professionals (e.g., building inspectors; later additional domains) record speech while working. They need:

1) High-quality Swedish transcription from audio recordings (MP3/WAV and capture recordings).
2) Reliable, template-driven generation of **professional reports** (Markdown; optional exports such as DOCX for capture workflows).

### 1.2 What problems the system solves

- Eliminates manual transcription and manual report writing.
- Standardizes report content and structure using centrally managed templates.
- Enables project/tenant-scoped access control and auditing for professional environments.
- Provides a local Docker workflow for development and a Loopia-oriented production path.

### 1.3 Goals (product)

- Simple web UI to upload/select audio and generate reports.
- Admin UI to manage templates (system prompts) and tenant/project structure.
- Capture workflows: record audio in chunks + attach images + generate transcript/report/export.
- Maintain auditability and a predictable agent-driven development flow.

---

## 2. Repository orientation (how this repo is organized)

### 2.1 Canonical directory map (high-level)

This repository follows SoT-driven structure. Key directories:

- `/docs/PRD/` — Product Requirements Documents (authoritative)
- `/docs/SoT/` — Source of Truth constraints/policies/contracts (authoritative)
- `/docs/implementation/` — phased plans, tasks, evidence expectations
- `/services/` — application services (PHP app, nginx config, etc.)
- `/database/migrations/` — MySQL init/migrations (executed by docker DB init)
- `/scripts/` — helper scripts (deploy, LOC, etc.)
- `/agents/` — agent prompt templates and workflows (OA/IA)

Local-only artifact directories used by the workflow (MUST be gitignored):

- `/.codebasebackup/` — ZIP snapshots + manifests (created by `create_codebase.bat`)
- `/.dbdump/` — local database dump artifacts (if used in this workflow)

### 2.2 Mandatory repo root files

The following root files exist and names must remain stable (per SoT):

- `create_codebase.bat`
- `docker_compose_up.bat`
- `docker_compose_build_pull.bat`
- `docker_compose_build_nocache.bat`
- `docker-compose.yml`
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`

---

## 3. System at a glance

### 3.1 Main user journeys

#### Journey A — Upload audio → generate report (MVP flow)

1) User uploads MP3/WAV (or selects previously uploaded file).
2) User selects a template (system prompt).
3) System transcribes audio (kbwhisper).
4) System runs LLM pipeline (OpenAI) to extract structured data + render final Markdown.
5) User downloads the `.md` report.

#### Journey B — Templates management

1) Admin opens Templates UI.
2) Admin creates/edits a template (system prompt).
3) Template is used during report generation (generic / customer / project scope).

#### Journey C — Capture workflow (recordings + images)

1) User works in Capture UI (`/capture`).
2) Client uploads audio chunks + images + events via `/api/capture/*`.
3) Recording is finalized; background job created.
4) Worker processes transcription/report/docx export jobs.
5) User views transcript/report and optionally downloads exports.

### 3.2 Main UI modules (product map)

| Module | Purpose | How to access | Typical actions |
|--------|---------|---------------|-----------------|
| Home | entry point and primary navigation | `/?page=home` | navigate to other modules |
| Templates | manage templates/system prompts | `/?page=templates` | create/edit/delete templates |
| Uploads | manage uploaded files and outputs | `/?page=uploads` | browse uploads, access generated outputs |
| Projects | choose current project scope | `/?page=projects` and `/?page=switch_project` | set project, list available |
| Capture | recording UI | `/capture` or `/?page=capture` | record, view, generate, export |
| Admin: Customers | tenant management (superuser) | `/?page=admin_customers` | create/edit/deactivate |
| Admin: Projects | project management (admin) | `/?page=admin_projects` | create/edit/delete |
| Admin: Users | user management | `/?page=admin_users` | create/edit, role/access |
| Profile | self-service settings | `/?page=profile` | password, TOTP, locale |
| Audit | audit log viewer | `/?page=audit` | filter and review events |

---

## 4. External integrations

| Integration | Used for | Where configured | Notes |
|------------|----------|------------------|------|
| OpenAI API | LLM processing pipeline (extract + render report) | `.env` (`OPENAI_*`) | report generation |
| kbwhisper | Swedish transcription service | `.env` (`KB_WHISPER_*`) | used by capture worker + report flow |
| Loopia (FTP) | production deployment + syncing (if enabled) | `.env` (`FTP_*`) | deploy scripts in `/scripts/` |
| SMTP | password reset / notifications (if enabled) | `.env` (`MAIL_*`) | environment-dependent |
| MySQL | primary datastore | `.env` (`DB_*` / `MYSQL_*`) | local docker + production mysql |

---

## 5. Environments, hosting, and configuration

### 5.1 Local development (Docker)

Local stack (from `docker-compose.yml`):

- `nginx` (port mapping `28080:80`)
- `app` (PHP-FPM)
- `db` (MySQL 8.4; init scripts from `/database/migrations/`)
- `phpmyadmin` (DB admin UI)

### 5.2 Production

- Deployed to a Loopia-hosted environment (via FTP deploy scripts).
- MySQL in production is provided externally (Loopia MySQL endpoint).
- The PHP entrypoint supports both Docker layout and “flat” Loopia layout (autoload path fallback).

### 5.3 `.env` policy

- `.env` is local/secret and MUST NOT be committed.
- `.env.example` is committed and contains keys only (no secrets).

### 5.4 `.env.example` (blank values)

```dotenv
# === Required ===
OPENAI_API_KEY=
OPENAI_MODEL=

# Optional override (default https://api.openai.com/v1)
OPENAI_BASE_URL=

# === MySQL (Loopia Production) ===
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

# === MySQL (Docker - local development) ===
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_ROOT_PASSWORD=

# === FTP Deployment (Loopia) ===
FTP_HOST=
FTP_USER=
FTP_PASSWORD=
FTP_PORT=
FTP_BASE_PATH=

# === Site URL ===
SITE_URL=

# === App ===
APP_ENV=
APP_DEBUG=

# === Phase 02 UI Feature Flags ===
# Set to 1 to enable Phase 02 desktop shell/navigation.
FEATURE_UI_PHASE02=
DOCPILOT_SIDEBAR=

# === KB Whisper ASR ===
KB_WHISPER_URL=
KB_WHISPER_TIMEOUT=
KB_WHISPER_LANGUAGE=
KB_WHISPER_VAD_FILTER=

# === Loopia Sync Storage ===
CAPTURE_STORAGE_PATH=
LOOPIA_CACHE_PATH=

# === Upload/Performance ===
UPLOAD_MAX_FILESIZE=
POST_MAX_SIZE=
PHP_MEMORY_LIMIT=
PHP_MAX_EXECUTION_TIME=

# === OpenAI ===
OPENAI_TIMEOUT=

# === Authentication ===
SESSION_LIFETIME=
SESSION_COOKIE_NAME=
CSRF_TOKEN_LIFETIME=

# === Security ===
PASSWORD_RESET_LIFETIME=
MAX_LOGIN_ATTEMPTS=
LOGIN_LOCKOUT_DURATION=

# === Mail (SMTP) ===
MAIL_HOST=
MAIL_PORT=
MAIL_ENCRYPTION=
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM_ADDRESS=
MAIL_FROM_NAME=
```

---

## 6. System architecture

### 6.1 High-level component diagram

If your Markdown renderer supports Mermaid:

```
flowchart LR
  U[User] --> FE[Web UI (Nginx + PHP)]
  FE --> DB[(MySQL)]
  FE --> W[kbwhisper]
  FE --> L[OpenAI API]
  FE --> FTP[Loopia FTP (deploy/sync)]
```

Fallback (always renders):

```text
User -> Web UI (Nginx + PHP) -> MySQL
                       |-> kbwhisper
                       |-> OpenAI API
                       |-> Loopia FTP (deploy/sync)
```

### 6.2 Runtime components

| Component | Responsibility | Location |
|----------|-----------------|----------|
| Nginx | serves static assets, routes PHP requests, serves `/capture/` static files | `/services/nginx/` |
| PHP app | web UI pages (`?page=...`), capture API (`/api/capture/*`), auth, admin | `/services/app/` |
| MySQL | persistence (tenants, users, recordings, templates, jobs, etc.) | `/database/migrations/` |
| Worker | processes queued capture jobs (transcribe/report/docx) | `/services/app/bin/worker.php` |
| Loopia sync runner | sync/deploy helper for production | `/services/app/bin/loopia_sync.php` + `/scripts/` |
| E2E tests | Playwright tests against production/dev targets | `/e2e/` |

### 6.3 Cross-cutting concerns (middleware-like behavior)

- Authentication and session handling (login/TOTP).
- Authorization: tenant/project scoping via membership/access tables.
- CSRF protection for web forms.
- Audit logging for admin/critical operations.
- Idempotency for capture uploads (idempotency keys).

---

## 7. HTTP interface (pages + APIs)

### 7.1 Web “page” routes (query-param router)

The primary UI uses `/?page=<route>` (see `/services/app/src/Http/Router.php`). Key routes include:

- `home`
- `templates`, `templates_save`, `templates_delete`
- `uploads`
- `projects`, `switch_project`
- `audio_upload`
- `report_run`, `report_download`
- `login`, `login_submit`, `logout`, `totp_verify`, `totp_verify_submit`
- `password_reset_request`, `password_reset_request_submit`, `password_reset_complete`, `password_reset_submit`
- `admin_customers`, `admin_customer_form`, `admin_customer_save`, `admin_customer_delete`
- `admin_projects`, `admin_project_form`, `admin_project_save`, `admin_project_delete`
- `admin_users`, `admin_user_form`, `admin_user_save`, `admin_user_delete`
- `profile`, `profile_password`, `profile_password_save`, `profile_totp`, `profile_totp_enable`, `profile_totp_disable`, `profile_locale`, `profile_logout_others`
- `audit`
- `capture`, `capture_viewer`

### 7.2 Capture REST API (`/api/capture/*`)

Capture API routes are path-based and handled before `?page=` routing.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/capture/login` | capture client login |
| GET | `/api/capture/bootstrap` | client bootstrap/config |
| GET | `/api/capture/recordings` | list recordings |
| POST | `/api/capture/recordings` | create recording |
| GET | `/api/capture/images/{id}` | get image binary |
| GET | `/api/capture/recordings/{id}` | get recording |
| GET | `/api/capture/recordings/{id}/images` | list images |
| POST | `/api/capture/recordings/{id}/images` | upload image |
| POST | `/api/capture/recordings/{id}/chunks` | upload audio chunk |
| POST | `/api/capture/recordings/{id}/events` | post events |
| POST | `/api/capture/recordings/{id}/finalize` | finalize recording |
| GET | `/api/capture/recordings/{id}/transcript` | get transcript |
| GET | `/api/capture/recordings/{id}/report` | get report |
| POST | `/api/capture/recordings/{id}/report/generate` | generate report |
| GET | `/api/capture/recordings/{id}/export/docx` | export DOCX |

---

## 8. Data model (MySQL)

### 8.1 Migrations

Database init/migrations are executed via MySQL init scripts in:

- `/database/migrations/`

### 8.2 Table inventory (high level)

The repository currently defines the following tables (via migrations):

- `customers`, `projects`
- `users`, `sessions`
- `user_customer_memberships`, `user_project_access`
- `audit_logs`
- `templates`
- `audio_files`, `reports`
- Capture domain:
  - `capture_recordings`
  - `capture_audio_chunks`, `capture_audio_final`
  - `capture_images`
  - `capture_events`
  - `capture_transcripts`
  - `capture_reports`
  - `capture_docx_exports`
  - `capture_processing_jobs`
  - `capture_idempotency_keys`

For authoritative column-level details, use the SQL migrations as the source of truth.

---

## 9. Data flows (how data moves)

### 9.1 MVP report flow (audio upload → report)

1) Upload audio file.
2) Persist upload metadata in DB and store file in storage.
3) Transcribe via kbwhisper.
4) Run OpenAI pipeline:
   - Step 1: extract structured JSON
   - Step 2: render Markdown report
5) Store paths/metadata and make report downloadable.

### 9.2 Capture processing flow (chunks/images → transcript/report/export)

1) Client creates a recording and uploads chunks/images/events.
2) Client finalizes the recording.
3) System creates processing jobs in `capture_processing_jobs`.
4) Worker (`/services/app/bin/worker.php`) processes pending jobs:
   - assemble audio final
   - transcribe via kbwhisper
   - generate report via OpenAI
   - generate DOCX export (if requested/available)
5) UI retrieves transcript/report/export endpoints for viewing/download.

---

## 10. How we work (OA/IA)

### 10.1 Document-driven development

- PRD defines **what** must be built: `/docs/PRD/`
- SoT defines **rules and constraints**: `/docs/SoT/`
- Implementation plans define **phases + tasks + evidence**: `/docs/implementation/`

### 10.2 Agent contract (OA → IA)

OA must provide IA with:
- Exact phase/task scope + referenced PRD/SoT paths.
- Tests to run and required evidence artifacts.
- “Do not change” constraints and file boundaries.

IA must deliver:
- Incremental commits per task.
- Test results and evidence outputs.
- Updated docs when behavior/contracts change.

---

## 11. Appendix

### 11.1 Key references (in repo)

- PRD: `/docs/PRD/000_prd_reportforge.md`
- SoT main: `/docs/SoT/000_sot_reportforge.md`
- Repo layout SoT: `/docs/SoT/20_repo_layout.md`
- Modularity policy: `/docs/SoT/modularity_policy.md`
- Runtime ports: `/docs/SoT/runtime_ports.md`
- Implementation plans: `/docs/implementation/` (multiple sub-projects)
- Agent docs: `AGENTS.md` and `/agents/`

### 11.2 Change log

| Date | Change | Author |
|------|--------|--------|
| 2026-02-10 | Initial project overview export | OA |
