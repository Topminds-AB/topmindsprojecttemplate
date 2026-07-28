# Architecture

How a request to `docs.<system>.se` becomes a rendered Wiki.js page.

## Full request flow

```
[ User browser ]
       │
       │  https://docs.docpilot.se/
       ↓
[ Cloudflare edge (proxied) ]                         ← TLS termination
       │
       │  CNAME lookup: docs.docpilot.se
       │     → 72d16344-d1ac-41e7-8f30-2766ed8edc5e
       │       .cfargotunnel.com
       ↓
[ Cloudflare Tunnel — Zero Trust ingress ]
       │
       │  Ingress rule:
       │    docs.docpilot.se → http://127.0.0.1:80
       ↓
[ DOCKERHOST1 — Windows service "Cloudflared" ]
       │
       │  Forwards to local port 80
       ↓
[ Traefik container (traefik-gateway) ]               ← entrypoint: web
       │
       │  Router: wikijs-docpilot@file
       │    rule: Host(`docs.docpilot.se`)
       │    middlewares:
       │      - wikijs-forwarded-headers (X-Forwarded-Proto: https)
       │      - wikijs-docpilot-redirect (regex / → L2 path)
       ↓
[ Redirect: 302 Location: /sv/docpilot/anvandardokumentation/?lang=sv ]
       │
       │  Browser follows redirect, new request:
       │    https://docs.docpilot.se/sv/docpilot/anvandardokumentation/?lang=sv
       ↓
[ Traefik again, same router ]
       │
       │  Path is no longer "/" — redirect-middleware doesn't fire
       │  passes through to backend
       ↓
[ wikijs-app container — port 3000 ]                  ← on Docker net "proxy"
       │
       │  Wiki.js renders L2 page with embedded JS redirect
       ↓
[ User sees L2 page, then L3 landing for "sv" ]
```

## Three configuration sources

Each component owns part of the configuration. The skill writes to all three through their respective APIs:

1. **Cloudflare DNS** — what `docs.docpilot.se` resolves to. Written via `/zones/{id}/dns_records` REST API.
2. **Cloudflare Tunnel ingress** — which hostnames the tunnel accepts. Written via `/accounts/{id}/cfd_tunnel/{id}/configurations` REST API. Remote-managed (no local config file).
3. **Traefik dynamic config** — which router matches which hostname and where it forwards. Written as a YAML file in the Traefik dynamic directory, picked up via the file watcher.

## Why a separate file per system

Traefik supports multiple files in `dynamic/`. Each new system gets its own file `wikijs-<slug>.yml`. This means:

- Adding a system: write one new file
- Removing a system: delete one file
- Bug in one system's config: only that one router is broken
- No risk of formatting or merge conflicts in a shared file

The legacy `wikijs.yml` (which contains a multi-host router for `prohat.topminds.se`, `docs.prohat.se`, etc.) keeps working unchanged. Per-system files are additive.

## Why redirect at Traefik, not Wiki.js

Wiki.js doesn't natively know "this hostname should redirect to that path". It serves whatever path the request asks for.

Doing the redirect at Traefik:

- `/` on `docs.docpilot.se` → 302 to L2 redirect page
- `/sv/docpilot/...` on `docs.docpilot.se` → passed through to Wiki.js as-is

This means deep links from external sources still work — only the bare-hostname case redirects.

## TLS

Cloudflare proxies all traffic in our setup (`proxied: true` on the DNS record), which means:

- TLS is terminated at Cloudflare's edge
- Traffic from Cloudflare to DOCKERHOST1 goes through the encrypted tunnel
- Traefik receives plain HTTP, but with `X-Forwarded-Proto: https` set by the `wikijs-forwarded-headers` middleware
- Wiki.js sees `https` as the effective scheme, generates correct absolute URLs

If you ever switch to `proxied: false`, Cloudflare DNS becomes pure DNS and the tunnel still works, but TLS would have to be terminated by Traefik with Let's Encrypt or similar. That's a different topology — not what this skill configures.

## Idempotency

All three components allow safe re-runs:

| Component | Behaviour on re-run with same input |
|-----------|--------------------------------------|
| Traefik file | Compares content; only writes if different |
| Tunnel ingress | Looks for existing rule for hostname; updates only if service differs |
| DNS CNAME | Looks for existing record; updates only if content/proxied differs |

Re-running `configure_domain.py add` with the same `docs-config.yaml` is a no-op when state matches.
