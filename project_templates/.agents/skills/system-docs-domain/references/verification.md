# Verification reference

What `verify_domain.py` checks, and how to debug each step.

## Three independent checks

`verify_domain.py` runs three checks. They're independent so you can pin down exactly where a failure is.

### 1. Local check

```
GET http://127.0.0.1/  with Host: <hostname>
```

Expects: `302` (or 301/307/308) with `Location` containing the system slug fragment.

What it proves: Traefik is running, the file watcher loaded `wikijs-<slug>.yml`, and the redirect-middleware regex matches.

What it doesn't prove: that Cloudflare can reach Traefik, that DNS resolves, or that public TLS works.

### 2. Tunnel check

```
GET /accounts/{id}/cfd_tunnel/{id}/configurations
```

Expects: an ingress rule with the hostname.

What it proves: Cloudflare Tunnel knows about the hostname and routes it somewhere.

What it doesn't prove: that the cloudflared service is actually running on DOCKERHOST1, or that the tunnel can reach Traefik. Only that the API has the configuration.

For runtime verification of the tunnel itself:

```powershell
curl.exe -sS http://127.0.0.1:20241/metrics | Select-String "tunnel_ha_connections"
```

Should be ≥ 1. Cloudflare requires at least one HA connection for the tunnel to serve traffic.

### 3. Public check

```
GET https://<hostname>/
```

Expects: final URL (after redirects) contains the system slug fragment, status 200.

What it proves: the entire chain works end-to-end as a real user would experience it.

Why it can fail temporarily: DNS propagation. New CNAMEs typically resolve within 30–90 seconds, but can take longer. The script retries with backoff up to `--max-wait` seconds (default 60).

## Accesslog delta

If `TRAEFIK_ACCESS_LOG` is set (typically `C:\projects\traefik\logs\access.log`), the script counts lines before and after the public check.

Expected delta: **2** for a successful public test.

- Line 1: redirect from `/` → L2 path (status 302)
- Line 2: GET on the L2 path (status 200)

A delta of 0 means the request didn't reach Traefik (Cloudflare-side issue). A delta of 1 means the redirect happened but the follow-up didn't — usually means Wiki.js is unreachable from Traefik.

## Reading domain-verification.json

The script writes `tmp/docs-build/domain-verification.json`. Shape:

```json
{
  "hostname": "docs.docpilot.se",
  "expected_fragment": "/docpilot/anvandardokumentation",
  "checks": {
    "local": {
      "ok": true,
      "status": 302,
      "location": "/sv/docpilot/anvandardokumentation/?lang=sv"
    },
    "tunnel": {
      "ok": true,
      "rule": {"hostname": "docs.docpilot.se", "service": "http://127.0.0.1:80"},
      "config_version": 5
    },
    "public": {
      "ok": true,
      "status": 200,
      "final_url": "https://docs.docpilot.se/sv/docpilot/anvandardokumentation/sv",
      "attempts": 1
    }
  },
  "accesslog_delta": 2,
  "ok": true
}
```

`ok: true` at the top level means all three checks passed. Each check has its own `ok` field with details.

## Failure patterns

### Local fails, tunnel ok, public fails

Traefik isn't picking up the dynamic file. Check:

- Is `<TRAEFIK_DYNAMIC_CONFIG_DIR>/wikijs-<slug>.yml` actually there?
- `docker logs traefik-gateway --tail 50` — any parse errors?
- Is `wikijs-shared.yml` present? (provides the shared middleware)

### Local ok, tunnel ok, public fails

DNS not propagated yet, OR Cloudflare-edge issue.

- Test DNS directly: `nslookup docs.docpilot.se 1.1.1.1`
  - Should return `<tunnel-id>.cfargotunnel.com`
- Test public reachability of tunnel:
  ```powershell
  curl.exe -sS http://127.0.0.1:20241/metrics | Select-String "tunnel_total_requests"
  ```
  - Should increment after a public request attempt
- Wait 5 minutes and re-run: `python verify_domain.py --repo-root .`

### Local ok, tunnel fails

API token issue. Most likely missing the `Account:Cloudflare Tunnel:Edit` scope. Recreate the token in Cloudflare dashboard.

### Local fails with 404

Traefik received the request but couldn't match a router. Check:

- Hostname matches exactly (case-sensitive subdomain doesn't matter, but typos do)
- The file ends in `.yml` (not `.yaml` — Traefik watches `.yml` and `.yaml` both, but stick to `.yml` for consistency)

### Local fails with 502

Traefik matched a router but can't reach the backend. Wiki.js container not on `proxy` network:

```powershell
docker network inspect proxy | Select-String "wikijs-app"
```

Empty output means it's not connected. Fix:

```powershell
docker network connect proxy wikijs-app
```

### Public returns 200 but lands on wrong page

Redirect target points wrong. Check:

- `domain.redirect_target` in `docs-config.yaml` (if explicitly set)
- Otherwise the auto-derived target uses `WIKIJS_DEFAULT_LOCALE` from `.env`
- Inspect `wikijs-<slug>.yml` directly, look at the `replacement:` line

To re-generate without re-running everything: edit `docs-config.yaml`, then:

```powershell
python .agents/skills/system-docs-domain/scripts/configure_domain.py add --repo-root .
```

The Traefik file gets rewritten; DNS and tunnel are no-op since they're unchanged.

## When to re-run verification

- After `configure_domain.py add` — automatic, but rerunnable
- 5–10 minutes after a fresh DNS create (if `--max-wait` was too short)
- After Wiki.js restart, to confirm Traefik can still reach it
- After any change to `.env` that affects the redirect target
- Periodically as a smoke-test that the chain still works
