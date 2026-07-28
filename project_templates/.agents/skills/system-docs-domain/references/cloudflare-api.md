# Cloudflare API reference

Endpoints, scopes, and response shapes used by the `system-docs-domain` skill.

## Authentication

All requests use Bearer token authentication:

```
Authorization: Bearer <CLOUDFLARE_API_TOKEN>
```

Tokens are scoped — give them only the minimum needed. For this skill:

| Permission | Resource | Notes |
|---|---|---|
| `Zone:DNS:Edit` | the apex zone (e.g. `docpilot.se`) | for CNAME create/update/delete |
| `Account:Cloudflare Tunnel:Edit` | account that owns the tunnel | for ingress configuration |

Create token at: Cloudflare dashboard → My Profile → API Tokens → Create Token → Custom token.

## Endpoints used

### Zones

```
GET /zones?name=<apex>
```

Returns array of zones the token can see, filtered by name. Used to convert
`docpilot.se` (zone name) to a zone ID.

### DNS records

```
GET    /zones/{zone_id}/dns_records?name=<full hostname>&type=CNAME
POST   /zones/{zone_id}/dns_records
PUT    /zones/{zone_id}/dns_records/{record_id}
DELETE /zones/{zone_id}/dns_records/{record_id}
```

Body for POST/PUT:

```json
{
  "type": "CNAME",
  "name": "docs.docpilot.se",
  "content": "72d16344-d1ac-41e7-8f30-2766ed8edc5e.cfargotunnel.com",
  "proxied": true,
  "ttl": 1
}
```

`ttl: 1` means "automatic" (required when `proxied: true`).

### Tunnel configuration

```
GET /accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations
PUT /accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations
```

GET returns the full tunnel config:

```json
{
  "result": {
    "tunnel_id": "72d16344-...",
    "version": 4,
    "config": {
      "ingress": [
        {"hostname": "docs.prohat.se", "service": "http://127.0.0.1:80"},
        {"hostname": "wiki.topminds.se", "service": "http://127.0.0.1:80"},
        {"service": "http_status:404"}
      ],
      "warp-routing": {"enabled": false}
    },
    "source": "cloudflare"
  },
  "success": true
}
```

PUT replaces the entire config. The catch-all `{"service": "http_status:404"}` MUST remain as the last entry — Cloudflare requires it.

When updating ingress, the skill:

1. GETs current config
2. Splits ingress into specific (with hostname) and catch-all (without)
3. Adds or updates one specific rule
4. PUTs back: `[...specific, ...catchall]`

## Response shape

Successful responses always have:

```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": <endpoint-specific>
}
```

Errors:

```json
{
  "success": false,
  "errors": [
    {"code": 1003, "message": "Invalid or missing zone id."}
  ],
  "result": null
}
```

The `cloudflare_api.py` client raises `CloudflareError(status, errors)` on any non-success response.

## Common errors

| Status | Cause | Fix |
|---|---|---|
| 400 — `Invalid request headers` | Token format wrong | Check `Authorization: Bearer <token>` |
| 401 — `Authentication error` | Token invalid or expired | Regenerate token in Cloudflare dashboard |
| 403 — `Insufficient permissions` | Token missing scope | Add `Zone:DNS:Edit` or `Account:Tunnel:Edit` |
| 404 — `Zone not found` | Token doesn't have access to that zone | Add zone to token's zone list |
| 1003 — `Invalid zone id` | Wrong zone, e.g. apex misspelled | Verify zone name matches Cloudflare dashboard |
| 81044 — `Record already exists` | CNAME conflict | Skill detects this; use `--force` to overwrite |

## Rate limits

Cloudflare API rate limits at the time of writing:

- 1200 requests per 5 minutes per token (general)
- DNS API: 4 requests per second per zone

The skill makes 4–6 API calls per `add` run, so rate limits are never an issue in normal use.

## References

- [DNS records API](https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-list-dns-records)
- [Tunnel configuration API](https://developers.cloudflare.com/api/operations/cloudflare-tunnel-configuration-get-configuration)
- [Token permissions](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
