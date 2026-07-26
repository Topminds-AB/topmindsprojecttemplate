---
name: production-docker-migration
description: Execute a verified migration of a Docker Compose based repository from a development machine to a production Docker host, including database migration, routing preparation, runtime verification, and old-repo archiving only after all gates pass.
---

# Production Docker Migration Executor

## Mission

Move one Docker Compose based repository from a source development environment to a production Docker host without relying on host-installed runtime dependencies, and without deleting or archiving the source repository until the destination is fully verified.

This skill is generic and reusable for future repository migrations. The Wiki.js migration is the first concrete implementation.

## Non-Negotiable Rules

1. Runtime dependencies must be inside the Docker stack. Do not rely on ffmpeg, node, python, database clients, or other application runtime tools installed directly on the host unless they are used only as migration helper tools.
2. Never perform destructive actions before all verification gates pass.
3. Never delete the source repository until the destination environment has been verified locally, through Traefik, through Cloudflare, and through application-level API tests.
4. Never print secrets, tokens, database passwords, or `.env` contents in full.
5. Use source-controlled files when possible, but verify against the real runtime environment.
6. Treat generated snapshots as evidence, not as a replacement for inspecting the live source repo.
7. If a snapshot redacts secrets inside a file that must be executable, verify the corresponding live source file before copying it to production.
8. If a required answer is missing from the migration questionnaire, stop and report the exact missing field.
9. The development workstation must not remain a production routing dependency.
10. The old source repository must not be archived/deleted until Claude or the independent auditor has returned PASS or explicit user-approved CONDITIONAL PASS.

## Verified Compose Source Rule

For the Wiki.js migration, the Docker Compose content provided by the user in the ChatGPT conversation is the verified compose source.

Before executing the migration, compare the live source compose file at the questionnaire-defined source path:

```text
<SOURCE_REPO_PATH>\docker-compose.yml
```

For the current Wiki.js migration this is expected to be:

```text
E:\projects\wiki.js\docker-compose.yml
```

against the verified user-provided compose structure:

- `postgres` service uses `postgres:16-alpine`.
- `wiki` service uses `ghcr.io/requarks/wiki:2.5.308`.
- `pgadmin` service uses `dpage/pgadmin4:9.14`.
- `postgres` uses `${POSTGRES_DB}`, `${POSTGRES_USER}`, `${POSTGRES_PASSWORD}`.
- `wiki` uses `DB_PASS: ${POSTGRES_PASSWORD}`.
- `wiki` binds `127.0.0.1:${WIKI_HOST_PORT}:3000`.
- `pgadmin` binds `127.0.0.1:${PGADMIN_HOST_PORT}:80`.
- `wiki` is attached to both `wikijs_net` and external `proxy`.
- `proxy` is external and must be created if missing.

If the live file differs:

1. Report the exact differences.
2. Classify each difference as harmless, suspicious, or blocking.
3. Do not silently overwrite or normalize the file.
4. Proceed only if the live file is functionally equivalent or after explicit user approval.

## Production Target Architecture

The intended production routing architecture is:

```text
Cloudflare
  -> cloudflared on DOCKERHOST1 (Windows service or Docker container)
  -> Traefik on DOCKERHOST1
  -> Wiki.js container over Docker network proxy
  -> PostgreSQL only on internal wikijs_net
```

Traefik must be installed and run in the production environment on DOCKERHOST1 unless the user explicitly decides to keep a central reverse proxy elsewhere.

The development workstation must not remain a production routing dependency.

## Documentation Hotel Model

Wiki.js is intended to become a documentation hotel.

Initial canonical hostname:

```text
docs.prohat.se
```

Future supported hostname pattern:

```text
docs.<systemname>.se
```

For this migration, verify `docs.prohat.se` first.

Additional system hostnames must be treated as aliases to the same Wiki.js instance unless the migration questionnaire explicitly says that a system requires its own isolated Wiki.js instance and database.

Recommended content namespace model:

```text
systems/<systemname>/...
```

## Inputs

Read a completed migration questionnaire before starting. Required fields:

- `PROJECT_NAME`
- `SNAPSHOT_PREFIX`
- `SOURCE_REPO_PATH`
- `DEST_HOST`
- `DEST_HOST_IP`
- `DEST_REPO_PATH`
- `DEST_ACCESS_METHOD`
- `COMPOSE_FILE_PATH`
- `COMPOSE_PROJECT_NAME`
- `REQUIRED_EXTERNAL_DOCKER_NETWORKS`
- `CREATE_MISSING_NETWORKS`
- `DB_ENGINE`
- `DB_MIGRATION_MODE`
- `DB_CONTAINER_NAME`
- `SOURCE_ENV_PATH`
- `DEST_ENV_PATH`
- `CANONICAL_HOSTNAME`
- `TRAEFIK_DYNAMIC_CONFIG_PATH`
- `TRAEFIK_CONTAINER_NAME`
- `CLOUDFLARED_RUN_MODE`
- `CLOUDFLARED_SERVICE_NAME` when `CLOUDFLARED_RUN_MODE=windows_service`
- `CLOUDFLARED_CONTAINER_NAME` when `CLOUDFLARED_RUN_MODE=docker_container`
- `CLOUDFLARED_CONFIG_SOURCE`
- `ARCHIVE_TARGET_PATH`
- `ARCHIVE_NAME_RULE`

## Phase 0 — Preflight

1. Confirm current date.
2. Confirm source repo exists.
3. Confirm destination path is reachable.
4. Confirm archive target path exists or can be reached by fallback UNC.
5. Confirm Docker is available on destination.
6. Confirm Docker Compose is available on destination.
7. Confirm source repo is not dirty unless the migration plan explicitly allows uncommitted files.
8. Confirm `.env` exists on source and contains every variable referenced by Docker Compose.
9. Render source compose config:

```powershell
docker compose config
```

10. Search the repo for host dependency assumptions:

```powershell
Get-ChildItem -Path . -Recurse -File | Select-String -Pattern "ffmpeg|node.exe|python.exe|C:\\|D:\\|E:\\|host.docker.internal"
```

Report findings and distinguish application runtime dependencies from migration/admin helper usage.

## Phase 1 — Build Migration Package

1. Create a timestamped working directory outside the repo.
2. Create a file inventory for source repo excluding `.git`, `node_modules`, `vendor`, virtualenvs, generated caches, previous archives, and runtime data that will be handled separately.
3. Copy the source repo to the migration working directory preserving file timestamps.
4. Copy `.env` only through the approved secret handling path.
5. Create or locate a database dump according to `DB_ENGINE` and `DB_MIGRATION_MODE`.

For PostgreSQL in Docker:

```powershell
docker exec <DB_CONTAINER_NAME> pg_dump -U <POSTGRES_USER> -d <POSTGRES_DB> --clean --if-exists > <SNAPSHOT_PREFIX>_db_dump_YYYY-MM-DD_HH-mm.sql
```

Do not hardcode credentials. Read them from `.env` or the running container environment.

6. Verify the dump is non-empty and starts with PostgreSQL dump content.
7. Record checksums for repo package and database dump.

## Phase 2 — Copy To Destination

1. Ensure destination parent directory exists.
2. If destination repo already exists, rename it to a timestamped pre-migration backup. Do not overwrite.
3. Copy repo files to destination.
4. Copy `.env` to destination using the approved secret handling path.
5. Copy database dump to destination migration folder.
6. Compare source and destination file inventory.
7. Report any missing, extra, or changed files before continuing.

## Phase 3 — Destination Docker Preparation

1. On the destination host, create required external Docker networks if missing:

```powershell
docker network inspect proxy > $null 2>&1; if ($LASTEXITCODE -ne 0) { docker network create proxy }
```

2. Render destination compose config:

```powershell
docker compose config
```

3. Pull required images:

```powershell
docker compose pull
```

4. Start only the database first if the stack supports it:

```powershell
docker compose up -d postgres
```

5. Wait for database health.

## Phase 4 — Database Restore

For PostgreSQL:

1. Copy dump into the database container or stream it through `psql`.
2. Restore into the destination database.
3. Verify table count and key Wiki.js tables:

```sql
SELECT count(*) FROM pages;
SELECT count(*) FROM assets;
SELECT count(*) FROM users;
SELECT count(*) FROM "apiKeys";
SELECT count(*) FROM settings;
```

4. Compare source counts if source is still running.
5. If restore fails, stop and report exact failing statement or command.

## Phase 5 — Start Destination Stack

1. Start all services:

```powershell
docker compose up -d
```

2. Verify:

```powershell
docker compose ps
docker compose logs --tail 150
```

3. Confirm only intended services are on public/proxy networks.
4. Confirm database and pgAdmin are not exposed through Traefik unless explicitly approved.

## Phase 6 — Local Verification

Run from destination:

```powershell
curl.exe -I http://127.0.0.1:<LOCAL_PORT>/
curl.exe -sS -D - -o NUL http://127.0.0.1:<LOCAL_PORT>/graphql
```

Confirm expected HTTP status codes and no container crash loops.

## Phase 7 — Traefik Preparation

1. Ensure Traefik runs in the production environment.
2. Ensure Traefik is connected to the same external Docker network as the application service, usually `proxy`.
3. Install or update the dynamic config for the project.
4. Use the canonical hostname and all required aliases.
5. Restart only Traefik if the file provider does not reload automatically.
6. Verify the route points to the destination app container/service and not to the development host.
7. Verify via hostname when possible.

## Phase 8 — Cloudflare / Cloudflared Verification

`cloudflared` may run on the production side either as a Windows service or as a Docker container. Do not fail the migration only because `docker inspect cloudflared` returns `no such object`. First verify the configured run mode from the questionnaire and the actual host state.

For DOCKERHOST1 in the Wiki.js migration, the verified production mode is:

```text
CLOUDFLARED_RUN_MODE=windows_service
CLOUDFLARED_SERVICE_NAME=Cloudflared
```

1. Confirm `cloudflared` runs on the production side, not on the development workstation.

For Windows service mode, run:

```powershell
Get-Service *cloudflared*
sc.exe qc Cloudflared
where.exe cloudflared
```

The service must be `Running`. The service binary/config must belong to DOCKERHOST1.

For Docker container mode, run:

```powershell
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
docker inspect <CLOUDFLARED_CONTAINER_NAME>
```

2. Determine whether the tunnel is locally managed by a config file or remotely managed by the Cloudflare dashboard.
3. If locally managed, locate the actual config path from `sc.exe qc Cloudflared` or service arguments and validate ingress:

```powershell
cloudflared tunnel ingress validate --config <CONFIG_PATH>
```

If no local config exists because the tunnel is remotely managed, record that fact and verify the route through Cloudflare/dashboard evidence and live HTTPS tests instead.

4. Confirm Cloudflare DNS/tunnel contains the canonical hostname.
5. Confirm ingress routes to Traefik on DOCKERHOST1, not to the development workstation.
6. Validate:

```powershell
curl.exe -I https://<CANONICAL_HOSTNAME>/
curl.exe -sS -D - -o NUL https://<CANONICAL_HOSTNAME>/graphql
```

7. Confirm no route still depends on the development workstation.

## Phase 9 — Application-Level Verification

For Wiki.js:

1. Verify GraphQL responds.
2. Verify `WIKIJS_API_TOKEN` works.
3. Read page list.
4. Create a temporary migration verification page.
5. Read it back.
6. Update it.
7. Upload a small verification asset.
8. Read the asset back.
9. Remove or clearly mark the verification page according to project policy.

## Phase 10 — Final Cutover Gate

Before any source archive/delete step, produce a final report containing:

- Source repo path
- Destination repo path
- Compose status
- Container image list
- Database restore evidence
- Source/destination page/user/asset counts
- Local route evidence
- Traefik route evidence
- Cloudflare route evidence
- API create/update/readback evidence
- Upload/readback evidence
- File inventory comparison result
- Known deviations

If any required gate failed, stop. Do not archive or delete the source repo.

## Phase 11 — Archive Old Source Repo

Only after Phase 10 passes and the independent auditor has returned PASS or explicit user-approved CONDITIONAL PASS:

1. Stop source stack only if the cutover plan requires it.
2. Create archive named by `ARCHIVE_NAME_RULE`, for example:

```text
<SNAPSHOT_PREFIX>_YYYY-MM-DD.zip
```

3. Store archive in `ARCHIVE_TARGET_PATH`.
4. If mapped drive is unavailable, use approved UNC fallback.
5. Verify archive exists and can be opened.
6. Verify archive contains source repo files.
7. Only then remove the old source repo directory from `projects`.
8. Record deletion evidence.

## Hard Archive/Delete Gate

The old source repository must not be deleted until all of the following are true:

1. Destination repository exists on the destination host.
2. `docker compose config` passes on destination.
3. All containers are healthy/running.
4. PostgreSQL dump has been restored successfully.
5. Wiki.js responds locally from destination.
6. Wiki.js responds through Traefik.
7. Wiki.js responds through Cloudflare on the canonical hostname.
8. At least one restored page can be read from the restored database.
9. At least one test page can be created, updated, read back, and deleted or clearly marked as test.
10. pgAdmin is reachable only according to the approved exposure model.
11. A final archive exists at the approved archive path or UNC fallback.
12. The archive filename uses the snapshot prefix, for example `WIKI_YYYY-MM-DD.zip`.
13. The independent auditor has completed verification with PASS or explicit user-approved CONDITIONAL PASS.

## Output

Return a concise migration report with:

- PASS/FAIL for each phase
- Commands run
- Verification evidence
- Any skipped step and why
- Exact remaining manual action, if any
