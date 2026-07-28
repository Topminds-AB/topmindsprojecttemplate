#!/usr/bin/env python3
"""
verify_domain.py — verify a configured domain alias end-to-end.

Three checks:
  1. local   — Traefik responds on 127.0.0.1:80 with Host header
  2. tunnel  — Cloudflare Tunnel ingress lists the hostname
  3. public  — public HTTPS request resolves and lands on the L2 redirect

Each check has retry/backoff (DNS propagation can take seconds to minutes).

Usage:
    python verify_domain.py --repo-root .
    python verify_domain.py --repo-root . --skip-public  # only local + tunnel
    python verify_domain.py --repo-root . --max-wait 120 # wait longer for DNS
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))

import cloudflare_api as cf  # noqa: E402

try:
    import yaml
except ImportError:
    print("PyYAML not installed", file=sys.stderr)
    sys.exit(2)

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):  # type: ignore
        pass


def color(text: str, c: str) -> str:
    if os.environ.get("NO_COLOR"):
        return text
    codes = {"red": 31, "green": 32, "yellow": 33, "cyan": 36, "gray": 90}
    return f"\033[{codes.get(c, 0)}m{text}\033[0m"


def step(msg: str) -> None:
    print(f"{color('▸', 'cyan')} {msg}")


def ok(msg: str) -> None:
    print(f"  {color('✓', 'green')} {msg}")


def warn(msg: str) -> None:
    print(f"  {color('!', 'yellow')} {msg}")


def fail(msg: str) -> None:
    print(f"  {color('✗', 'red')} {msg}", file=sys.stderr)


# ----- Config -------------------------------------------------------------


def load_settings(repo_root: Path) -> dict[str, Any]:
    """Load hostname and slug from docs-config.yaml."""
    candidates = [
        repo_root / "docs" / "docs-config.yaml",
        repo_root / "docs-config.yaml",
    ]
    config = None
    for p in candidates:
        if p.exists():
            config = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            break
    if config is None:
        raise FileNotFoundError("docs-config.yaml not found")

    domain = config.get("domain") or {}
    if not domain.get("hostname"):
        raise RuntimeError("domain.hostname not set in docs-config.yaml")
    if not (config.get("system") or {}).get("slug"):
        raise RuntimeError("system.slug not set in docs-config.yaml")

    return {
        "hostname": domain["hostname"],
        "system_slug": config["system"]["slug"],
        "expected_path_fragment": f"/{config['system']['slug']}/anvandardokumentation",
    }


# ----- Local check (curl Traefik on 127.0.0.1) ----------------------------


def check_local(hostname: str, expected_fragment: str) -> dict[str, Any]:
    """GET http://127.0.0.1/ with Host: <hostname>. Expect 302/301 to L2 path."""
    step(f"Local: Traefik response for Host: {hostname}")
    req = urllib.request.Request(
        "http://127.0.0.1/",
        headers={"Host": hostname},
        method="GET",
    )
    # Don't follow redirects — we want to see the redirect itself
    opener = urllib.request.build_opener(NoRedirectHandler())
    try:
        with opener.open(req, timeout=10) as resp:
            location = resp.headers.get("Location", "")
            status_code = resp.status
    except urllib.error.HTTPError as e:
        # Some redirects come through as HTTPError; that's fine
        location = e.headers.get("Location", "") if e.headers else ""
        status_code = e.code
    except (urllib.error.URLError, socket.timeout) as e:
        fail(f"could not reach 127.0.0.1: {e}")
        return {"status": None, "location": None, "ok": False, "error": str(e)}

    is_redirect = status_code in (301, 302, 303, 307, 308)
    fragment_ok = expected_fragment in (location or "")
    if is_redirect and fragment_ok:
        ok(f"{status_code} -> {location}")
        return {"status": status_code, "location": location, "ok": True}
    if is_redirect:
        warn(f"{status_code} -> {location} "
             f"(does not contain expected '{expected_fragment}')")
        return {"status": status_code, "location": location, "ok": False,
                "reason": "redirect target does not match expected fragment"}
    fail(f"unexpected status {status_code} (expected 301/302/303/307/308)")
    return {"status": status_code, "location": location, "ok": False,
            "reason": "no redirect"}


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


# ----- Tunnel check (API) -------------------------------------------------


def check_tunnel(hostname: str) -> dict[str, Any]:
    """Verify the hostname has an ingress rule in the Cloudflare Tunnel."""
    step(f"Tunnel: ingress rule for {hostname}")
    try:
        cfg = cf.get_tunnel_config()
    except cf.CloudflareError as e:
        fail(f"tunnel API error: {e}")
        return {"ok": False, "error": str(e)}

    ingress = (cfg.get("config") or {}).get("ingress") or []
    rule = next((r for r in ingress if r.get("hostname") == hostname), None)
    if rule:
        ok(f"rule found: {hostname} -> {rule.get('service')}")
        return {"ok": True, "rule": rule, "config_version": cfg.get("version")}
    fail(f"no ingress rule found for {hostname}")
    return {"ok": False, "rule": None, "config_version": cfg.get("version")}


# ----- Public check (HTTPS curl with retry) -------------------------------


def check_public(
    hostname: str,
    expected_fragment: str,
    max_wait_seconds: int = 60,
) -> dict[str, Any]:
    """GET https://<hostname>/, follow redirects, verify final URL."""
    step(f"Public: https://{hostname}/ (waits up to {max_wait_seconds}s for DNS)")
    deadline = time.time() + max_wait_seconds
    last_error = None
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(f"https://{hostname}/", method="GET",
                                          headers={"User-Agent": "verify_domain/1.0"})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                final_url = resp.geturl()
                status_code = resp.status
            fragment_ok = expected_fragment in final_url
            if status_code == 200 and fragment_ok:
                ok(f"{status_code} final={final_url} (attempt {attempt})")
                return {"ok": True, "status": status_code, "final_url": final_url,
                        "attempts": attempt}
            warn(f"{status_code} final={final_url} "
                 f"(expected fragment {expected_fragment!r}, attempt {attempt})")
            return {"ok": False, "status": status_code, "final_url": final_url,
                    "attempts": attempt,
                    "reason": "fragment missing" if not fragment_ok else None}
        except (urllib.error.HTTPError, urllib.error.URLError,
                socket.gaierror, ssl.SSLError, socket.timeout) as e:
            last_error = str(e)
            time.sleep(min(5, max(2, attempt)))
    fail(f"public check failed after {attempt} attempts: {last_error}")
    return {"ok": False, "attempts": attempt, "error": last_error}


# ----- Accesslog delta (optional) -----------------------------------------


def count_lines(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except OSError:
        return None


# ----- CLI ----------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(prog="verify_domain")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--skip-public", action="store_true",
                   help="Skip the public HTTPS test (DNS may not have propagated)")
    p.add_argument("--max-wait", type=int, default=60,
                   help="Seconds to wait for public DNS (default 60)")
    p.add_argument("--output", default=None)
    args = p.parse_args()

    repo = Path(args.repo_root).resolve()
    load_dotenv(repo / ".env")

    try:
        settings = load_settings(repo)
    except Exception as e:
        fail(str(e))
        return 2

    hostname = settings["hostname"]
    expected = settings["expected_path_fragment"]

    # Optional: capture accesslog line count before/after
    log_path_str = os.environ.get("TRAEFIK_ACCESS_LOG", "")
    log_path = Path(log_path_str) if log_path_str else None
    before = count_lines(log_path) if log_path else None

    results: dict[str, Any] = {
        "hostname": hostname,
        "expected_fragment": expected,
        "checks": {},
    }

    results["checks"]["local"] = check_local(hostname, expected)
    results["checks"]["tunnel"] = check_tunnel(hostname)

    if args.skip_public:
        warn("skipping public check (--skip-public)")
        results["checks"]["public"] = {"ok": None, "skipped": True}
    else:
        results["checks"]["public"] = check_public(hostname, expected, args.max_wait)

    if log_path and before is not None:
        after = count_lines(log_path)
        if after is not None:
            results["accesslog_delta"] = after - before
            ok(f"accesslog delta: {after - before} lines")

    all_ok = all(
        c.get("ok") is not False
        for c in results["checks"].values()
    )
    results["ok"] = all_ok

    out = Path(args.output) if args.output else (
        repo / "tmp" / "docs-build" / "domain-verification.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResult written: {out}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
