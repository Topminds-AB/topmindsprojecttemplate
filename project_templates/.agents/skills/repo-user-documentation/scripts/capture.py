#!/usr/bin/env python3
"""
capture.py — Playwright-driven screenshot capture for user documentation.

Requirements (install once):
    pip install playwright python-dotenv
    playwright install chromium

Environment variables (read from shell; .env is loaded if python-dotenv is installed):
    APP_URL                    — base URL (required)
    APP_USERNAME, APP_PASSWORD — login credentials (required)
    APP_LOGIN_PATH             — path to login form, default "/login"
    APP_USERNAME_SELECTOR      — default 'input[name="username"], input[type="email"]'
    APP_PASSWORD_SELECTOR      — default 'input[name="password"], input[type="password"]'
    APP_SUBMIT_SELECTOR        — default 'button[type="submit"]'
    APP_POST_LOGIN_URL_CONTAINS — a substring that must appear in the URL after
                                  successful login, for verification. Default: not set.
    APP_SUPPORTED_LOCALES      — comma-separated (informational; --locale is authoritative)
    APP_LOCALE_SWITCH_STRATEGY — url-param | path-prefix | cookie | user-setting
    APP_LOCALE_SWITCH_PARAM    — query-param key or cookie name

Read-only mode (default):
    Refuses to click elements matching DANGEROUS_SELECTORS unless --allow-mutations.

Subcommands:
    login-check   — log in once, print the landing URL, exit
    capture-url   — capture a single URL (for ad-hoc use)
    run           — capture all screens in a plan JSON, for a given locale
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from playwright.sync_api import sync_playwright, Page, BrowserContext


DEFAULTS = {
    "APP_LOGIN_PATH": "/login",
    "APP_USERNAME_SELECTOR": 'input[name="username"], input[type="email"], input[name="email"]',
    "APP_PASSWORD_SELECTOR": 'input[name="password"], input[type="password"]',
    "APP_SUBMIT_SELECTOR": 'button[type="submit"], input[type="submit"]',
    "APP_LOCALE_SWITCH_STRATEGY": "url-param",
    "APP_LOCALE_SWITCH_PARAM": "lang",
}

DANGEROUS_SELECTORS = [
    'button:has-text("Delete")', 'button:has-text("Ta bort")',
    'button:has-text("Remove")', 'button:has-text("Radera")',
    'button:has-text("Confirm")', 'button:has-text("Bekräfta")',
    'form:not([data-doc-safe])',
]

VIEWPORT = {"width": 1440, "height": 900}


def env(key: str) -> str | None:
    return os.environ.get(key) or DEFAULTS.get(key)


def require(*keys: str) -> dict[str, str]:
    missing = [k for k in keys if not env(k)]
    if missing:
        print(f"Missing required env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(2)
    return {k: env(k) for k in keys}


def build_url(base: str, path: str, locale: str) -> str:
    """Apply locale switching strategy when building a URL."""
    strategy = env("APP_LOCALE_SWITCH_STRATEGY")
    param = env("APP_LOCALE_SWITCH_PARAM")
    base = base.rstrip("/")
    path = "/" + path.lstrip("/")
    if strategy == "path-prefix":
        return f"{base}/{locale}{path}"
    if strategy == "url-param":
        sep = "&" if "?" in path else "?"
        return f"{base}{path}{sep}{param}={locale}"
    # cookie / user-setting: URL unchanged, locale applied out-of-band
    return f"{base}{path}"


def apply_locale_cookie(context: BrowserContext, base_url: str, locale: str) -> None:
    """Set a locale cookie on the context. Used when strategy == cookie."""
    from urllib.parse import urlparse
    host = urlparse(base_url).hostname
    if not host:
        return
    context.add_cookies([{
        "name": env("APP_LOCALE_SWITCH_PARAM") or "locale",
        "value": locale,
        "domain": host,
        "path": "/",
    }])


def do_login(page: Page, base_url: str) -> None:
    """Navigate to login path and authenticate."""
    creds = require("APP_USERNAME", "APP_PASSWORD")
    login_url = base_url.rstrip("/") + env("APP_LOGIN_PATH")
    page.goto(login_url, wait_until="domcontentloaded")
    page.wait_for_selector(env("APP_USERNAME_SELECTOR"), timeout=15000)
    page.fill(env("APP_USERNAME_SELECTOR"), creds["APP_USERNAME"])
    page.fill(env("APP_PASSWORD_SELECTOR"), creds["APP_PASSWORD"])
    page.click(env("APP_SUBMIT_SELECTOR"))
    # Wait for navigation to complete
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    expected = os.environ.get("APP_POST_LOGIN_URL_CONTAINS")
    if expected and expected not in page.url:
        print(f"Post-login URL {page.url!r} does not contain {expected!r}. "
              "Check credentials and APP_POST_LOGIN_URL_CONTAINS.", file=sys.stderr)
        sys.exit(3)


def safe_navigate(page: Page, url: str, allow_mutations: bool) -> None:
    """Navigate and refuse to accidentally trigger dangerous UI."""
    page.goto(url, wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    if not allow_mutations:
        # Disable form submission by evaluating JS that preventDefaults.
        page.evaluate(
            "() => { document.querySelectorAll('form:not([data-doc-safe])').forEach("
            "f => f.addEventListener('submit', e => e.preventDefault(), {capture:true})); }"
        )



def take_screenshot(page: Page, out_path: Path, full_page: bool = True) -> None:
    """Take a screenshot and write it to out_path."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_path), full_page=full_page)


def new_context(pw, locale: str) -> tuple[Any, BrowserContext]:
    """Launch a fresh browser + context with the locale pre-applied where possible."""
    browser = pw.chromium.launch(headless=True)
    context_args: dict[str, Any] = {
        "viewport": VIEWPORT,
        "locale": locale.replace("_", "-"),
    }
    context = browser.new_context(**context_args)
    base_url = require("APP_URL")["APP_URL"]
    strategy = env("APP_LOCALE_SWITCH_STRATEGY")
    if strategy == "cookie":
        apply_locale_cookie(context, base_url, locale)
    return browser, context


def cmd_login_check(args) -> int:
    base_url = require("APP_URL")["APP_URL"]
    with sync_playwright() as pw:
        browser, context = new_context(pw, args.locale or "sv")
        page = context.new_page()
        do_login(page, base_url)
        print(f"Login OK. Landing URL: {page.url}")
        browser.close()
    return 0



def cmd_capture_url(args) -> int:
    base_url = require("APP_URL")["APP_URL"]
    out_path = Path(args.output)
    with sync_playwright() as pw:
        browser, context = new_context(pw, args.locale)
        page = context.new_page()
        if args.login:
            do_login(page, base_url)
        target = build_url(base_url, args.path, args.locale)
        safe_navigate(page, target, allow_mutations=args.allow_mutations)
        if args.wait_selector:
            page.wait_for_selector(args.wait_selector, timeout=15000)
        if args.wait_ms:
            page.wait_for_timeout(args.wait_ms)
        take_screenshot(page, out_path, full_page=not args.no_full_page)
        print(f"Wrote {out_path}")
        browser.close()
    return 0


def cmd_run(args) -> int:
    """Run a full plan for one locale. Plan shape documented in references/page-hierarchy.md."""
    base_url = require("APP_URL")["APP_URL"]
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    locale = args.locale
    out_dir = Path(args.output_dir)
    screens = plan.get("screens", [])
    if not screens:
        print("Plan has no 'screens' array. Nothing to capture.", file=sys.stderr)
        return 1

    manifest: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with sync_playwright() as pw:
        browser, context = new_context(pw, locale)
        page = context.new_page()
        do_login(page, base_url)
        for screen in screens:
            if screen.get("skip_locales") and locale in screen["skip_locales"]:
                continue
            filename = f"{screen['section']}/{screen['slug']}--{screen.get('state', 'default')}.png"
            out_path = out_dir / filename
            try:
                target = build_url(base_url, screen["path"], locale)
                safe_navigate(page, target, allow_mutations=args.allow_mutations)
                if screen.get("wait_selector"):
                    page.wait_for_selector(screen["wait_selector"], timeout=15000)
                if screen.get("wait_ms"):
                    page.wait_for_timeout(screen["wait_ms"])
                take_screenshot(page, out_path, full_page=screen.get("full_page", True))
                manifest.append({
                    "screen_id": screen.get("id"),
                    "section": screen["section"],
                    "slug": screen["slug"],
                    "state": screen.get("state", "default"),
                    "locale": locale,
                    "path": str(out_path.relative_to(out_dir.parent.parent)) if out_dir.parent.parent in out_path.parents else str(out_path),
                })
                print(f"  ✓ {filename}")
            except Exception as e:
                failures.append({"screen": screen, "error": str(e)})
                print(f"  ✗ {filename}: {e}", file=sys.stderr)
        browser.close()

    manifest_path = out_dir / "_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"locale": locale, "screens": manifest, "failures": failures}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote manifest {manifest_path} ({len(manifest)} ok, {len(failures)} failed)")
    return 0 if not failures else 1


def main() -> int:
    p = argparse.ArgumentParser(prog="capture")
    sub = p.add_subparsers(dest="cmd", required=True)

    lc = sub.add_parser("login-check", help="Log in and report the landing URL.")
    lc.add_argument("--locale", default="sv")

    cu = sub.add_parser("capture-url", help="Capture a single URL.")
    cu.add_argument("--path", required=True, help="Path relative to APP_URL.")
    cu.add_argument("--locale", required=True)
    cu.add_argument("--output", required=True)
    cu.add_argument("--login", action="store_true", default=True)
    cu.add_argument("--no-login", dest="login", action="store_false")
    cu.add_argument("--wait-selector", default=None)
    cu.add_argument("--wait-ms", type=int, default=0)
    cu.add_argument("--no-full-page", action="store_true")
    cu.add_argument("--allow-mutations", action="store_true")


    rn = sub.add_parser("run", help="Run a plan for one locale.")
    rn.add_argument("--plan", required=True, help="Path to plan.json")
    rn.add_argument("--locale", required=True)
    rn.add_argument("--output-dir", required=True)
    rn.add_argument("--allow-mutations", action="store_true")

    args = p.parse_args()
    if args.cmd == "login-check":
        return cmd_login_check(args)
    if args.cmd == "capture-url":
        return cmd_capture_url(args)
    if args.cmd == "run":
        return cmd_run(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
