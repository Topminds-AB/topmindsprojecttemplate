#!/usr/bin/env python3
"""
config_check.py — read docs-config.yaml and report which decisions are
pre-filled and which still need to be answered interactively.

Run this BEFORE doing anything else in a generation/update workflow. It tells
the agent exactly what to ask the user, and what to proceed with silently.

Usage:
    python config_check.py --repo-root . --output ./tmp/docs-build/config-status.json

Exit codes:
    0 = config is complete, no questions needed
    1 = config has gaps that need interactive answers
    2 = config file is missing or invalid
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)



# Each check returns (status, message). Status: "ok", "missing", "warning"
# "missing" = blocks the run, "warning" = run can proceed but quality may suffer

REQUIRED_ENV_VARS_APP = [
    "APP_URL", "APP_USERNAME", "APP_PASSWORD",
    "APP_SUPPORTED_LOCALES", "APP_LOCALE_SWITCH_STRATEGY",
]
REQUIRED_ENV_VARS_WIKI = [
    "WIKIJS_URL", "WIKIJS_API_TOKEN", "WIKIJS_DEFAULT_LOCALE",
    "WIKIJS_DEFAULT_EDITOR", "WIKIJS_SYSTEM_SLUG",
]
RECOMMENDED_ENV_VARS = ["APP_POST_LOGIN_URL_CONTAINS"]


def load_env(repo_root: Path) -> dict[str, str]:
    """Load .env file if present. Returns dict of key=value."""
    env_path = repo_root / ".env"
    if not env_path.exists():
        return {}
    out: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def load_config(repo_root: Path) -> tuple[dict[str, Any] | None, str]:
    """Try to load docs-config.yaml from common locations. Returns (data, path)."""
    candidates = [
        repo_root / "docs" / "docs-config.yaml",
        repo_root / "docs-config.yaml",
        repo_root / ".docs-config.yaml",
    ]
    for p in candidates:
        if p.exists():
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                return data, str(p.relative_to(repo_root))
            except yaml.YAMLError as e:
                print(f"YAML error in {p}: {e}", file=sys.stderr)
                return None, str(p.relative_to(repo_root))
    return None, ""



def check_env(env: dict[str, str]) -> list[dict[str, str]]:
    """Return list of issues with env vars."""
    issues: list[dict[str, str]] = []
    for key in REQUIRED_ENV_VARS_APP + REQUIRED_ENV_VARS_WIKI:
        if not env.get(key):
            issues.append({"category": "env", "severity": "missing", "key": key,
                           "message": f"Required env var {key} not set"})
    for key in RECOMMENDED_ENV_VARS:
        if not env.get(key):
            issues.append({"category": "env", "severity": "warning", "key": key,
                           "message": f"Recommended env var {key} not set "
                                      f"(without it, failed login passes silently)"})
    return issues


def check_config(config: dict[str, Any] | None) -> list[dict[str, str]]:
    """Return list of issues with the config file."""
    issues: list[dict[str, str]] = []
    if config is None:
        issues.append({"category": "config", "severity": "missing", "key": "file",
                       "message": "docs-config.yaml not found. "
                                  "Generation will rely on interactive prompts."})
        return issues

    # Required sections
    if not config.get("system", {}).get("slug"):
        issues.append({"category": "config", "severity": "missing",
                       "key": "system.slug",
                       "message": "system.slug is required"})
    if not config.get("locales"):
        issues.append({"category": "config", "severity": "missing",
                       "key": "locales",
                       "message": "locales[] is required"})

    # Sections that prevent unattended runs if missing
    if not config.get("flows"):
        issues.append({"category": "config", "severity": "warning",
                       "key": "flows",
                       "message": "No flows defined. Agent will ask interactively."})
    if not config.get("roles"):
        issues.append({"category": "config", "severity": "warning",
                       "key": "roles",
                       "message": "No roles defined. Agent will ask interactively."})
    if not config.get("audience", {}).get("inline") and \
       not config.get("audience", {}).get("file"):
        issues.append({"category": "config", "severity": "warning",
                       "key": "audience",
                       "message": "No audience set. Will use default "
                                  "(municipal caseworker)."})
    return issues


def check_locales_match(env: dict[str, str], config: dict[str, Any] | None) -> list[dict[str, str]]:
    """Verify .env locales match docs-config.yaml locales."""
    issues: list[dict[str, str]] = []
    env_locales = [l.strip() for l in env.get("APP_SUPPORTED_LOCALES", "").split(",") if l.strip()]
    cfg_locales = (config or {}).get("locales") or []
    if env_locales and cfg_locales and set(env_locales) != set(cfg_locales):
        issues.append({"category": "consistency", "severity": "missing",
                       "key": "locales",
                       "message": f"APP_SUPPORTED_LOCALES ({env_locales}) and "
                                  f"docs-config.yaml locales ({cfg_locales}) "
                                  f"don't match. Reconcile before running."})
    return issues



def main() -> int:
    p = argparse.ArgumentParser(prog="config_check")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--output", default=None,
                   help="Write status JSON to this path (in addition to stdout)")
    p.add_argument("--quiet", action="store_true",
                   help="Only print exit code-relevant info")
    args = p.parse_args()

    repo = Path(args.repo_root).resolve()
    env = load_env(repo)
    config, config_path = load_config(repo)

    issues = []
    issues.extend(check_env(env))
    issues.extend(check_config(config))
    issues.extend(check_locales_match(env, config))

    blocking = [i for i in issues if i["severity"] == "missing"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    status = {
        "repo_root": str(repo),
        "config_file": config_path or None,
        "env_loaded": len(env) > 0,
        "blocking_count": len(blocking),
        "warning_count": len(warnings),
        "blocking": blocking,
        "warnings": warnings,
        "summary": (
            "ready" if not blocking and not warnings else
            "ready_with_warnings" if not blocking else
            "blocked"
        ),
    }

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(status, indent=2, ensure_ascii=False),
                                     encoding="utf-8")

    if not args.quiet:
        if blocking:
            print(f"BLOCKED — {len(blocking)} issue(s) prevent unattended run:")
            for i in blocking:
                print(f"  ✗ [{i['key']}] {i['message']}")
        if warnings:
            print(f"\nWARNINGS — {len(warnings)} item(s) will trigger interactive questions:")
            for i in warnings:
                print(f"  ! [{i['key']}] {i['message']}")
        if not blocking and not warnings:
            print("OK — config is complete, no questions needed.")
        elif not blocking:
            print(f"\nReady to run. Agent will ask {len(warnings)} question(s) along the way.")

    if blocking:
        return 1 if config else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
