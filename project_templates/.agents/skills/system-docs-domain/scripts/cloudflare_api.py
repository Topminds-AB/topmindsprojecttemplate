#!/usr/bin/env python3
"""
cloudflare_api.py — minimal Cloudflare API client for DNS records and
Tunnel ingress configuration.

Uses only the standard library (urllib) so it works on a fresh DOCKERHOST1
without extra pip installs beyond what bootstrap.py already gives us.

API reference:
- DNS records:    https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-list-dns-records
- Tunnel config:  https://developers.cloudflare.com/api/operations/cloudflare-tunnel-configuration-get-configuration

Environment variables read:
- CLOUDFLARE_API_TOKEN
- CLOUDFLARE_ACCOUNT_ID
- CLOUDFLARE_TUNNEL_ID
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


API_BASE = "https://api.cloudflare.com/client/v4"


class CloudflareError(Exception):
    """Raised when the Cloudflare API returns an error response."""

    def __init__(self, status: int, errors: list[dict[str, Any]] | str):
        self.status = status
        self.errors = errors
        msg = f"Cloudflare API {status}: {errors}"
        super().__init__(msg)


def _token() -> str:
    t = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not t:
        raise RuntimeError("CLOUDFLARE_API_TOKEN not set in environment")
    return t


def _account_id() -> str:
    a = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    if not a:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID not set in environment")
    return a


def _tunnel_id() -> str:
    t = os.environ.get("CLOUDFLARE_TUNNEL_ID", "").strip()
    if not t:
        raise RuntimeError("CLOUDFLARE_TUNNEL_ID not set in environment")
    return t


def _request(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    *,
    timeout: int = 20,
) -> dict[str, Any]:
    """Make an authenticated request to the Cloudflare API."""
    url = API_BASE + path
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {_token()}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode("utf-8"))
        except Exception:
            raise CloudflareError(e.code, str(e)) from e
        raise CloudflareError(e.code, payload.get("errors", payload)) from e
    if not payload.get("success"):
        raise CloudflareError(200, payload.get("errors", []))
    return payload


# ----- Zone lookup --------------------------------------------------------


def get_zone_id(zone_name: str) -> str:
    """Resolve a zone name (e.g. 'docpilot.se') to its Cloudflare zone ID."""
    resp = _request("GET", f"/zones?name={zone_name}")
    result = resp.get("result", [])
    if not result:
        raise RuntimeError(f"Zone not found in Cloudflare account: {zone_name}")
    return result[0]["id"]


def derive_zone_from_hostname(hostname: str) -> str:
    """Return the apex domain from a hostname.

    'docs.docpilot.se' -> 'docpilot.se'
    'docs.example.co.uk' -> 'example.co.uk'  (best-effort heuristic)
    """
    parts = hostname.strip(".").split(".")
    if len(parts) < 2:
        raise ValueError(f"Hostname has no apex: {hostname}")
    # Two-label TLDs we know about. For others, take last two labels.
    two_label_tlds = {"co.uk", "com.au", "co.nz", "co.jp"}
    last_two = ".".join(parts[-2:])
    last_three = ".".join(parts[-3:]) if len(parts) >= 3 else last_two
    if last_two in two_label_tlds and len(parts) >= 3:
        return last_three
    return last_two


# ----- DNS records --------------------------------------------------------


def find_dns_record(zone_id: str, name: str, record_type: str = "CNAME") -> dict[str, Any] | None:
    """Find an existing DNS record by name + type. Returns None if not found."""
    resp = _request(
        "GET",
        f"/zones/{zone_id}/dns_records?name={name}&type={record_type}"
    )
    records = resp.get("result", [])
    return records[0] if records else None


def upsert_cname(
    zone_id: str,
    name: str,
    content: str,
    proxied: bool = True,
    ttl: int = 1,
) -> dict[str, Any]:
    """Create or update a CNAME record.

    Returns the record dict from Cloudflare.
    Idempotent: if a record with the same name already exists with the same
    content + proxied + ttl, this is a no-op and returns the existing record.
    """
    existing = find_dns_record(zone_id, name, "CNAME")
    body = {
        "type": "CNAME",
        "name": name,
        "content": content,
        "proxied": proxied,
        "ttl": ttl,
    }
    if existing:
        if (
            existing.get("content") == content
            and existing.get("proxied") == proxied
            and existing.get("ttl") == ttl
        ):
            return existing
        resp = _request("PUT", f"/zones/{zone_id}/dns_records/{existing['id']}", body)
    else:
        resp = _request("POST", f"/zones/{zone_id}/dns_records", body)
    return resp["result"]


def delete_cname(zone_id: str, name: str) -> bool:
    """Delete the CNAME record for `name`. Returns True if a record was deleted."""
    existing = find_dns_record(zone_id, name, "CNAME")
    if not existing:
        return False
    _request("DELETE", f"/zones/{zone_id}/dns_records/{existing['id']}")
    return True


# ----- Tunnel ingress -----------------------------------------------------


def get_tunnel_config() -> dict[str, Any]:
    """Fetch the current Cloudflare Tunnel configuration."""
    resp = _request(
        "GET",
        f"/accounts/{_account_id()}/cfd_tunnel/{_tunnel_id()}/configurations",
    )
    return resp["result"]


def put_tunnel_config(config: dict[str, Any]) -> dict[str, Any]:
    """Replace the Cloudflare Tunnel configuration with `config`.

    `config` must be the full config dict (including 'config' key with
    'ingress' and 'warp-routing'). Use update_tunnel_ingress() for the
    common case of adding/updating one hostname.
    """
    resp = _request(
        "PUT",
        f"/accounts/{_account_id()}/cfd_tunnel/{_tunnel_id()}/configurations",
        config,
    )
    return resp["result"]


def update_tunnel_ingress(
    hostname: str,
    service: str,
) -> dict[str, Any]:
    """Add or update an ingress rule for `hostname` -> `service`.

    Preserves existing rules. Idempotent: if the rule already exists with
    the same service, no API write is performed.

    The catch-all rule (no hostname, service: http_status:404) is preserved
    as the LAST entry per Cloudflare requirements.
    """
    current = get_tunnel_config()
    inner = current.get("config") or {}
    ingress = list(inner.get("ingress") or [])

    # Split into specific rules + catch-all (last one without hostname)
    specific = [r for r in ingress if r.get("hostname")]
    catchall = [r for r in ingress if not r.get("hostname")]
    if not catchall:
        # Default catch-all if missing
        catchall = [{"service": "http_status:404"}]

    # Find existing rule for this hostname
    new_rule = {"hostname": hostname, "service": service}
    found = False
    for i, rule in enumerate(specific):
        if rule.get("hostname") == hostname:
            if rule.get("service") == service:
                # Already configured correctly
                return current
            specific[i] = new_rule
            found = True
            break
    if not found:
        specific.append(new_rule)

    new_config = {
        "config": {
            **inner,
            "ingress": specific + catchall,
        }
    }
    return put_tunnel_config(new_config)


def remove_tunnel_ingress(hostname: str) -> bool:
    """Remove the ingress rule for `hostname`. Returns True if a rule was removed."""
    current = get_tunnel_config()
    inner = current.get("config") or {}
    ingress = list(inner.get("ingress") or [])
    new_ingress = [r for r in ingress if r.get("hostname") != hostname]
    if len(new_ingress) == len(ingress):
        return False
    put_tunnel_config({"config": {**inner, "ingress": new_ingress}})
    return True


# ----- Self-test ----------------------------------------------------------


def main() -> int:
    """Quick smoke test: verify env vars + reach the API."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing Cloudflare API access...")
        try:
            cfg = get_tunnel_config()
            ingress = (cfg.get("config") or {}).get("ingress") or []
            print(f"  OK — tunnel has {len(ingress)} ingress rule(s)")
            for r in ingress:
                host = r.get("hostname") or "(catch-all)"
                print(f"    {host} -> {r.get('service')}")
            return 0
        except Exception as e:
            print(f"  FAIL — {e}", file=sys.stderr)
            return 1
    print("Usage: python cloudflare_api.py test")
    return 2


if __name__ == "__main__":
    sys.exit(main())
