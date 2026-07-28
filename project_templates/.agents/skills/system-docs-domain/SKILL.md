---
name: system-docs-domain
description: Configure and verify a documentation hostname through Traefik and Cloudflare Tunnel using the accompanying scripts and references in this bundle.
---

# System Docs Domain

## Purpose

Use this skill when a docs hostname such as `docs.<system>.se` must be added,
removed, or verified through the established Traefik plus Cloudflare Tunnel
flow.

## Workflow

1. Confirm the repo has the expected docs config and `.env` inputs.
2. Run the add, remove, or status flow through the provided scripts.
3. Run verification to confirm local Traefik, tunnel ingress, and public HTTPS.
4. Use the references below when debugging.

## Failure modes

- **DNS already exists pointing elsewhere** - script flags this, asks for `--force` to overwrite
- **Traefik watcher hasn't picked up the file** - local curl will fail; script retries 3x with 2s backoff
- **Tunnel API returns 401** - token is missing scopes; emit specific error pointing at the docs page
- **Public curl fails after 30s** - DNS hasn't propagated yet; emit warning and let user re-run `verify_domain.py` later

## Additional resources

- [references/architecture.md](references/architecture.md) - full request flow diagram
- [references/cloudflare-api.md](references/cloudflare-api.md) - endpoints, scopes, response shapes
- [references/traefik-router.md](references/traefik-router.md) - file format, middleware, network requirements
- [references/shared-middleware.md](references/shared-middleware.md) - how `wikijs-shared.yml` is managed
- [references/verification.md](references/verification.md) - what gets tested at each step

## Quality rules

- API token is read from `.env`, never logged or written to disk
- Account ID and Tunnel ID may be logged (not secrets)
- Traefik file always uses absolute backend URL via Docker DNS, never `localhost`
- Redirect target always uses absolute path including wiki-locale prefix
- Public verification waits up to 30s for DNS propagation; if it fails, the run is marked partial-success
