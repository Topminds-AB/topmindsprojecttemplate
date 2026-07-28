#!/usr/bin/env python3
"""
configure_domain.py — orchestrator for adding a per-system domain alias.

Reads docs-config.yaml, writes a Traefik dynamic config file, updates the
Cloudflare Tunnel ingress configuration, and creates/updates a Cloudflare
DNS CNAME record. End-to-end, idempotent.

Usage:
    python configure_domain.py add --repo-root .
    python configure_domain.py remove --repo-root .
    python configure_domain.py status --repo-root .

The skill reads:
    docs/docs-config.yaml      — system slug + domain config
    .env                        — Cloudflare credentials, Traefik paths

Writes:
    <traefik-dynamic>/wikijs-<slug>.yml
    Cloudflare DNS record
    Cloudflare Tunnel ingress rule
    ./tmp/docs-build/domain-status.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# Make sibling scripts importable
sys.path.insert(0, str(Path(__file__).parent))

import cloudflare_api as cf  # noqa: E402
import traefik_config as tc  # noqa: E402

try:
    import yaml
except ImportError:
    print("PyYAML not installed. Run bootstrap.py or: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):  # type: ignore
        pass


# ----- Helpers ------------------------------------------------------------


def color(text: str, c: str) -> str:
    if os.environ.get("NO_COLOR"):
        return text
    codes = {"red": 31, "green": 32, "yellow": 33, "cyan": 36, "gray": 90, "magenta": 35}
    return f"\033[{codes.get(c, 0)}m{text}\033[0m"


def step(msg: str) -> None:
    print(f"{color('▸', 'cyan')} {msg}")


def ok(msg: str) -> None:
    print(f"  {color('✓', 'green')} {msg}")


def warn(msg: str) -> None:
    print(f"  {color('!', 'yellow')} {msg}")


def fail(msg: str) -> None:
    print(f"  {color('✗', 'red')} {msg}", file=sys.stderr)


# ----- Config loading -----------------------------------------------------


def load_config(repo_root: Path) -> dict[str, Any]:
    """Load docs-config.yaml from repo root."""
    candidates = [
        repo_root / "docs" / "docs-config.yaml",
        repo_root / "docs-config.yaml",
        repo_root / ".docs-config.yaml",
    ]
    for p in candidates:
        if p.exists():
            return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    raise FileNotFoundError(
        f"docs-config.yaml not found in {repo_root}/docs or repo root. "
        f"Run prompt 00b first to create it."
    )


def required_env(*keys: str) -> dict[str, str]:
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        raise RuntimeError(
            f"Missing required env vars: {', '.join(missing)}. "
            f"Add them to .env in the repo root."
        )
    return {k: os.environ[k] for k in keys}


def derive_redirect_target(
    config: dict[str, Any],
    system_slug: str,
    wiki_locale: str,
    default_locale: str,
) -> str:
    """Build the redirect target path from config or sensible defaults."""
    domain_cfg = config.get("domain") or {}
    explicit = domain_cfg.get("redirect_target")
    if explicit:
        # User supplied an explicit target — respect it but ensure leading slash
        return explicit if explicit.startswith("/") else "/" + explicit
    return tc.build_redirect_target(wiki_locale, system_slug, default_locale)


# ----- Pre-flight ---------------------------------------------------------


def preflight(repo_root: Path) -> dict[str, Any]:
    """Verify environment and return resolved settings."""
    step("Pre-flight: loading config and env")

    config = load_config(repo_root)

    system = config.get("system") or {}
    slug = system.get("slug")
    if not slug:
        raise RuntimeError("system.slug missing from docs-config.yaml")

    domain_cfg = config.get("domain") or {}
    if not domain_cfg.get("enabled"):
        raise RuntimeError(
            "domain.enabled is not true in docs-config.yaml. "
            "Set it to true and provide domain.hostname to use this skill."
        )

    hostname = domain_cfg.get("hostname")
    if not hostname:
        raise RuntimeError("domain.hostname missing from docs-config.yaml")

    env = required_env(
        "CLOUDFLARE_API_TOKEN",
        "CLOUDFLARE_ACCOUNT_ID",
        "CLOUDFLARE_TUNNEL_ID",
        "TRAEFIK_DYNAMIC_CONFIG_DIR",
        "WIKIJS_DEFAULT_LOCALE",
    )

    dynamic_dir = Path(env["TRAEFIK_DYNAMIC_CONFIG_DIR"])
    if not dynamic_dir.exists():
        raise RuntimeError(
            f"Traefik dynamic config dir not found: {dynamic_dir}. "
            f"Verify TRAEFIK_DYNAMIC_CONFIG_DIR in .env."
        )

    backend_url = os.environ.get("WIKIJS_BACKEND_URL", "http://wikijs-app:3000")
    wiki_locale = env["WIKIJS_DEFAULT_LOCALE"]
    default_locale = (
        (config.get("locales") or [wiki_locale])[0]
        if isinstance(config.get("locales"), list)
        else wiki_locale
    )

    cf_cfg = domain_cfg.get("cloudflare") or {}
    zone = cf_cfg.get("zone") or cf.derive_zone_from_hostname(hostname)
    proxied = cf_cfg.get("proxied", True)

    redirect_target = derive_redirect_target(
        config, slug, wiki_locale, default_locale
    )

    ok(f"system: {slug}")
    ok(f"hostname: {hostname}")
    ok(f"zone: {zone}")
    ok(f"redirect target: {redirect_target}")
    ok(f"backend: {backend_url}")
    ok(f"traefik dynamic dir: {dynamic_dir}")

    return {
        "config": config,
        "system_slug": slug,
        "hostname": hostname,
        "zone": zone,
        "proxied": proxied,
        "wiki_locale": wiki_locale,
        "default_locale": default_locale,
        "redirect_target": redirect_target,
        "backend_url": backend_url,
        "dynamic_dir": dynamic_dir,
    }


# ----- Add ----------------------------------------------------------------


def cmd_add(repo_root: Path, dry_run: bool, force: bool) -> dict[str, Any]:
    """Configure a domain alias end-to-end."""
    settings = preflight(repo_root)
    status: dict[str, Any] = {
        "hostname": settings["hostname"],
        "system_slug": settings["system_slug"],
        "redirect_target": settings["redirect_target"],
        "dry_run": dry_run,
    }

    # 1. Traefik dynamic config
    step("Writing Traefik dynamic config")
    path, changed = tc.write_config(
        settings["dynamic_dir"],
        settings["system_slug"],
        settings["hostname"],
        settings["redirect_target"],
        settings["backend_url"],
        dry_run=dry_run,
    )
    status["traefik_file"] = str(path)
    status["traefik_changed"] = changed
    if changed:
        ok(f"{'would write' if dry_run else 'wrote'}: {path}")
        if not dry_run:
            time.sleep(2)  # let Traefik file watcher pick it up
    else:
        ok(f"unchanged: {path}")

    # 2. Cloudflare Tunnel ingress
    step("Updating Cloudflare Tunnel ingress")
    if dry_run:
        warn("(dry-run) would call PUT /accounts/.../cfd_tunnel/.../configurations")
        status["tunnel_updated"] = "dry-run"
    else:
        tunnel_target = os.environ.get("TRAEFIK_HOST_BIND", "http://127.0.0.1:80")
        try:
            cfg_after = cf.update_tunnel_ingress(settings["hostname"], tunnel_target)
            version = cfg_after.get("version", "?")
            ok(f"ingress updated → tunnel config version {version}")
            status["tunnel_config_version"] = version
            status["tunnel_target"] = tunnel_target
        except cf.CloudflareError as e:
            fail(f"tunnel update failed: {e}")
            status["tunnel_error"] = str(e)
            raise

    # 3. Cloudflare DNS
    step("Creating/updating Cloudflare DNS CNAME")
    if dry_run:
        warn(f"(dry-run) would upsert CNAME {settings['hostname']} -> "
             f"{os.environ['CLOUDFLARE_TUNNEL_ID']}.cfargotunnel.com")
        status["dns_record"] = "dry-run"
    else:
        try:
            zone_id = cf.get_zone_id(settings["zone"])
            cname_target = f"{os.environ['CLOUDFLARE_TUNNEL_ID']}.cfargotunnel.com"
            existing = cf.find_dns_record(zone_id, settings["hostname"], "CNAME")
            if existing and existing.get("content") != cname_target and not force:
                warn(
                    f"CNAME {settings['hostname']} already exists pointing to "
                    f"{existing.get('content')!r}. Re-run with --force to overwrite."
                )
                status["dns_record"] = {"existing": existing, "skipped": True}
            else:
                record = cf.upsert_cname(
                    zone_id, settings["hostname"], cname_target, settings["proxied"]
                )
                ok(f"DNS record id={record['id']} -> {record['content']} "
                   f"(proxied={record['proxied']})")
                status["dns_record"] = {
                    "id": record["id"],
                    "name": record["name"],
                    "type": record["type"],
                    "content": record["content"],
                    "proxied": record["proxied"],
                }
        except cf.CloudflareError as e:
            fail(f"DNS update failed: {e}")
            status["dns_error"] = str(e)
            raise

    status["ok"] = True
    return status


# ----- Remove -------------------------------------------------------------


def cmd_remove(repo_root: Path, dry_run: bool) -> dict[str, Any]:
    """Remove a domain alias end-to-end."""
    settings = preflight(repo_root)
    status: dict[str, Any] = {
        "hostname": settings["hostname"],
        "system_slug": settings["system_slug"],
        "dry_run": dry_run,
    }

    step("Removing Cloudflare DNS CNAME")
    if not dry_run:
        try:
            zone_id = cf.get_zone_id(settings["zone"])
            removed = cf.delete_cname(zone_id, settings["hostname"])
            ok("removed" if removed else "no record found")
            status["dns_removed"] = removed
        except cf.CloudflareError as e:
            warn(f"DNS removal failed: {e}")
            status["dns_error"] = str(e)
    else:
        warn("(dry-run) would delete CNAME")

    step("Removing Cloudflare Tunnel ingress rule")
    if not dry_run:
        try:
            removed = cf.remove_tunnel_ingress(settings["hostname"])
            ok("removed" if removed else "no ingress rule found")
            status["tunnel_ingress_removed"] = removed
        except cf.CloudflareError as e:
            warn(f"tunnel ingress removal failed: {e}")
            status["tunnel_error"] = str(e)
    else:
        warn("(dry-run) would remove ingress rule")

    step("Removing Traefik dynamic config file")
    if not dry_run:
        removed = tc.remove_config(settings["dynamic_dir"], settings["system_slug"])
        ok("removed" if removed else "no file to remove")
        status["traefik_removed"] = removed
    else:
        warn("(dry-run) would delete Traefik dynamic file")

    status["ok"] = True
    return status


# ----- Status -------------------------------------------------------------


def cmd_status(repo_root: Path) -> dict[str, Any]:
    """Inspect current state without changing anything."""
    settings = preflight(repo_root)
    status: dict[str, Any] = {
        "hostname": settings["hostname"],
        "system_slug": settings["system_slug"],
    }

    step("Inspecting Traefik dynamic config")
    target = tc.file_path(settings["dynamic_dir"], settings["system_slug"])
    status["traefik_file_exists"] = target.exists()
    ok(f"{'present' if target.exists() else 'missing'}: {target}")

    step("Inspecting Cloudflare Tunnel ingress")
    try:
        cfg = cf.get_tunnel_config()
        ingress = (cfg.get("config") or {}).get("ingress") or []
        match = next(
            (r for r in ingress if r.get("hostname") == settings["hostname"]), None
        )
        status["tunnel_ingress"] = match
        ok(f"rule {'found' if match else 'missing'} for {settings['hostname']}")
    except cf.CloudflareError as e:
        fail(f"tunnel query failed: {e}")
        status["tunnel_error"] = str(e)

    step("Inspecting Cloudflare DNS")
    try:
        zone_id = cf.get_zone_id(settings["zone"])
        record = cf.find_dns_record(zone_id, settings["hostname"], "CNAME")
        if record:
            status["dns_record"] = {
                "name": record["name"],
                "content": record["content"],
                "proxied": record["proxied"],
            }
            ok(f"CNAME -> {record['content']} (proxied={record['proxied']})")
        else:
            status["dns_record"] = None
            ok("no CNAME record")
    except cf.CloudflareError as e:
        fail(f"DNS query failed: {e}")
        status["dns_error"] = str(e)

    return status


# ----- CLI ----------------------------------------------------------------


def write_status(status: dict[str, Any], repo_root: Path) -> None:
    out = repo_root / "tmp" / "docs-build" / "domain-status.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nStatus written: {out}")


def main() -> int:
    p = argparse.ArgumentParser(prog="configure_domain")
    sub = p.add_subparsers(dest="cmd", required=True)
    for cmd in ("add", "remove", "status"):
        sp = sub.add_parser(cmd)
        sp.add_argument("--repo-root", default=".")
        if cmd != "status":
            sp.add_argument("--dry-run", action="store_true")
        if cmd == "add":
            sp.add_argument("--force", action="store_true",
                            help="Overwrite an existing DNS record pointing elsewhere")

    args = p.parse_args()
    repo = Path(args.repo_root).resolve()
    load_dotenv(repo / ".env")

    try:
        if args.cmd == "add":
            status = cmd_add(repo, args.dry_run, args.force)
        elif args.cmd == "remove":
            status = cmd_remove(repo, args.dry_run)
        else:
            status = cmd_status(repo)
    except RuntimeError as e:
        fail(str(e))
        return 2
    except cf.CloudflareError:
        return 1

    write_status(status, repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
