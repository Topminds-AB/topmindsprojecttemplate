# Tunnel ingress

How the Cloudflare Tunnel routes incoming traffic by hostname.

## Tunnel architecture (this installation)

The cloudflared service on DOCKERHOST1 runs in **token mode**:

```
cloudflared.exe tunnel run --token <REDACTED>
```

This means the configuration is **remote-managed** — stored in Cloudflare's edge, not in a local `config.yml`. There is no `cert.pem` or `credentials.json` file on disk. To change ingress rules, you talk to the Cloudflare API.

Local metrics endpoint exposes runtime info but not config:

```
http://127.0.0.1:20241/metrics
```

The metric `cloudflared_orchestration_config_version` increments each time edge pushes a new config, which the skill uses for verification.

## Ingress config shape

```json
{
  "config": {
    "ingress": [
      {
        "hostname": "docs.prohat.se",
        "service": "http://127.0.0.1:80"
      },
      {
        "hostname": "docs.docpilot.se",
        "service": "http://127.0.0.1:80"
      },
      {
        "service": "http_status:404"
      }
    ]
  }
}
```

**Critical rules:**

1. **Catch-all must be last.** A rule without a `hostname` matches anything. Cloudflare requires it as the final entry. The skill always preserves and re-positions it.

2. **First-match wins.** If two rules have the same hostname, only the first is used. Don't add duplicates.

3. **All hostnames point to the same local target.** Every documentation domain on this host routes to `http://127.0.0.1:80` (Traefik). Traefik then dispatches by hostname.

4. **`originRequest` settings are inherited from defaults** unless overridden per rule. The skill doesn't set per-rule overrides — defaults work.

## What the skill does

When you `apply` a new hostname:

```python
cf.upsert_tunnel_ingress(
    tunnel_id="72d16344-d1ac-41e7-8f30-2766ed8edc5e",
    hostname="docs.docpilot.se",
    service="http://127.0.0.1:80",
)
```

The client does:

1. GET current config
2. Filter out catch-all (the rule with no hostname)
3. Look for an existing rule with same hostname:
   - If found and `service` matches → no-op (return current config)
   - If found and `service` differs → replace in place
   - If not found → append to named rules
4. Re-attach catch-all as the last entry
5. PUT the full config back

This guarantees:
- No duplicate hostnames
- Catch-all stays last
- Order of other named rules is preserved

## Verifying tunnel picked up the change

After PUT, check `cloudflared_orchestration_config_version` on local metrics. It should increment within ~10 seconds. The skill does this implicitly when running `verify_domain.py`.

## Removing a tunnel ingress rule

```python
cf.remove_tunnel_ingress(tunnel_id, "docs.docpilot.se")
```

Filters the array, PUTs back. Removing a non-existent hostname is a silent no-op.

## What if the tunnel breaks after edit?

If the ingress config is malformed, cloudflared will reject the new config and continue running with the previous version. The dashboard shows an error in this case. The skill builds the config carefully and uses Cloudflare's validation, so this should be rare.

If it does happen:

1. Check Cloudflare dashboard → Zero Trust → Networks → Tunnels → click your tunnel → "Public Hostname" tab
2. Manually fix or remove the offending rule
3. Re-run `configure_domain.py apply` to reconcile

## Tunnel and account IDs

These are not secrets — they appear in URLs and DNS targets:

- Account ID: `f15c9e620bd67302addb2eb6a92b621d`
- Tunnel ID: `72d16344-d1ac-41e7-8f30-2766ed8edc5e`

Store them in `.env` for convenience but they're safe in the SoT document.

The **tunnel token** (used by `cloudflared --token`) is secret. Never commit, never log.
