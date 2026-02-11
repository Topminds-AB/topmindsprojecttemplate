# Docker Logs Requirements (Mandatory when Docker is used)

If the repo uses Docker for development/testing/runtime, the audit ZIP must include `/dockerlogs/`.

## Preferred script
- If repo-root `dockerlogs.bat` exists, use it.
- If it does not exist, produce equivalent artifacts using the commands below and document them in `manifest/manifest.md`.

## Minimum required artifacts
Place these under `/dockerlogs/`:

1) **Service logs (all services)**
- `docker compose logs --no-color` (or compose v1 equivalent)
- Save as: `dockerlogs/compose_logs.txt`

2) **Container status snapshot**
- `docker ps -a`
- Save as: `dockerlogs/docker_ps.txt`

3) **Compose config snapshot (recommended)**
- `docker compose config`
- Save as: `dockerlogs/compose_config.txt`

## Rules
- Do not include secrets.
- If logs include tokens/credentials, redact values before packaging and document that redaction occurred (without revealing the secret).
