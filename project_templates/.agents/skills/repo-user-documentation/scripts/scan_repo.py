#!/usr/bin/env python3
"""
scan_repo.py — produce a baseline user-surface inventory of a repository.

This script is a BEST-EFFORT baseline. It detects common patterns across
popular stacks and emits a JSON inventory. The agent running this skill
MUST review the output and fill in gaps by reading code directly.

Subcommands:
  routes        — detect routes (Next.js, React Router, Vue Router, Django, Express)
  i18n          — detect supported locales and i18n message files
  env           — parse .env.example and .env for user-relevant variables
  features      — best-effort feature inventory from navigation/menu files
  full-inventory— run everything and assemble one JSON file

Output JSON shape (inventory):
{
  "system": {"slug": "...", "name": "...", "description": "..."},
  "stack": {"framework": "...", "language": "...", "package_manager": "..."},
  "locales": ["sv", "en"],
  "routes": [{"path": "/dashboard", "auth": true, "source_file": "..."}],
  "features": [{"id": "reports", "label": "Reports", "routes": ["/reports"]}],
  "flows": [{"id": "login", "steps": [...]}],
  "roles": ["admin", "handlaggare"],
  "notifications": [...],
  "integrations": [...],
  "gaps": ["Flows could not be auto-detected; author manually."]
}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


IGNORE_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", "out",
    "__pycache__", ".venv", "venv", "coverage", ".turbo", ".cache",
    "vendor", "target", ".idea", ".vscode",
}


def walk(root: Path):
    for p in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        yield p


def detect_stack(root: Path) -> dict[str, Any]:
    stack: dict[str, Any] = {"framework": None, "language": None, "package_manager": None}
    if (root / "package.json").exists():
        stack["language"] = "javascript"
        try:
            pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "next" in deps:
                stack["framework"] = "nextjs"
            elif "react-router-dom" in deps or "react-router" in deps:
                stack["framework"] = "react-router"
            elif "vue-router" in deps or "vue" in deps:
                stack["framework"] = "vue"
            elif "express" in deps:
                stack["framework"] = "express"
            stack["package_manager"] = (
                "pnpm" if (root / "pnpm-lock.yaml").exists()
                else "yarn" if (root / "yarn.lock").exists()
                else "npm"
            )
        except Exception:
            pass
    elif (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        stack["language"] = "python"
        if any(root.rglob("manage.py")):
            stack["framework"] = "django"
        elif any((root / "requirements.txt").exists() and "flask" in (root / "requirements.txt").read_text(errors="ignore").lower() for _ in [0]):
            stack["framework"] = "flask"
    elif (root / "composer.json").exists():
        stack["language"] = "php"
        stack["framework"] = "laravel" if any(root.rglob("artisan")) else "php"
    return stack


def detect_routes(root: Path, framework: str | None) -> list[dict[str, Any]]:
    """Best-effort route detection. Returns list of {path, auth, source_file}."""
    routes: list[dict[str, Any]] = []

    # Next.js App Router: app/**/page.{tsx,jsx,ts,js}
    if framework == "nextjs":
        app_dir = root / "app"
        if not app_dir.exists():
            app_dir = root / "src" / "app"
        if app_dir.exists():
            for page in app_dir.rglob("page.*"):
                rel = page.relative_to(app_dir).parent
                path = "/" + "/".join(p for p in rel.parts if not p.startswith("("))
                path = path.replace("[", ":").replace("]", "")
                routes.append({"path": path or "/", "auth": None, "source_file": str(page.relative_to(root))})
        # Next.js Pages Router: pages/**/*.{tsx,jsx}
        pages_dir = root / "pages"
        if not pages_dir.exists():
            pages_dir = root / "src" / "pages"
        if pages_dir.exists():
            for page in pages_dir.rglob("*.[jt]sx"):
                rel = page.relative_to(pages_dir)
                if rel.name.startswith("_"):
                    continue
                path = "/" + str(rel.with_suffix("")).replace("\\", "/")
                path = path.replace("/index", "").replace("[", ":").replace("]", "")
                routes.append({"path": path or "/", "auth": None, "source_file": str(page.relative_to(root))})

    # React Router / Vue Router: scan source files for route patterns
    if framework in ("react-router", "vue"):
        route_pat = re.compile(r"""path\s*[:=]\s*["']([^"']+)["']""")
        src = root / "src"
        if src.exists():
            for f in src.rglob("*.[jt]s*"):
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for m in route_pat.finditer(text):
                    routes.append({"path": m.group(1), "auth": None, "source_file": str(f.relative_to(root))})

    # Django: urls.py patterns
    if framework == "django":
        urls_pat = re.compile(r"""path\s*\(\s*["']([^"']*)["']""")
        for f in root.rglob("urls.py"):
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for m in urls_pat.finditer(text):
                routes.append({"path": "/" + m.group(1).lstrip("/"), "auth": None, "source_file": str(f.relative_to(root))})

    # Dedupe by path, preserve first source_file
    seen: dict[str, dict[str, Any]] = {}
    for r in routes:
        if r["path"] not in seen:
            seen[r["path"]] = r
    return sorted(seen.values(), key=lambda r: r["path"])


def detect_locales(root: Path) -> list[str]:
    """Detect supported locales from common i18n file patterns."""
    locales: set[str] = set()
    candidates = [
        root / "locales", root / "public" / "locales", root / "src" / "locales",
        root / "messages", root / "src" / "messages",
        root / "i18n", root / "src" / "i18n",
    ]
    for base in candidates:
        if not base.exists():
            continue
        for item in base.iterdir():
            if item.is_dir() and re.match(r"^[a-z]{2}(-[A-Z]{2})?$", item.name):
                locales.add(item.name)
            elif item.is_file() and re.match(r"^[a-z]{2}(-[A-Z]{2})?\.(json|ya?ml|po)$", item.name):
                locales.add(item.stem)
    # .po / gettext
    for po in root.rglob("*.po"):
        if any(part in IGNORE_DIRS for part in po.parts):
            continue
        m = re.match(r"^([a-z]{2}(_[A-Z]{2})?)\.po$", po.name)
        if m:
            locales.add(m.group(1).replace("_", "-"))
    return sorted(locales)


def detect_env_vars(root: Path) -> list[dict[str, str]]:
    """Parse .env.example for user-relevant variables (names + inline comments)."""
    env_file = root / ".env.example"
    if not env_file.exists():
        env_file = root / ".env"
    if not env_file.exists():
        return []
    out: list[dict[str, str]] = []
    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            name, _, rest = line.partition("=")
            comment = ""
            if "#" in rest:
                _, _, comment = rest.partition("#")
            out.append({"name": name.strip(), "comment": comment.strip()})
    return out


def detect_system_meta(root: Path) -> dict[str, str]:
    """Pull system name / slug / description from package.json or pyproject."""
    meta: dict[str, str] = {"slug": root.name, "name": root.name, "description": ""}
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            meta["name"] = data.get("name", meta["name"])
            meta["slug"] = re.sub(r"[^a-z0-9]+", "-", meta["name"].lower()).strip("-")
            meta["description"] = data.get("description", "")
        except Exception:
            pass
    return meta


def full_inventory(root: Path) -> dict[str, Any]:
    stack = detect_stack(root)
    inv: dict[str, Any] = {
        "system": detect_system_meta(root),
        "stack": stack,
        "locales": detect_locales(root),
        "routes": detect_routes(root, stack["framework"]),
        "env": detect_env_vars(root),
        "features": [],
        "flows": [],
        "roles": [],
        "notifications": [],
        "integrations": [],
        "gaps": [],
    }
    # Gap flags — the agent must fill these
    if not inv["routes"]:
        inv["gaps"].append("No routes auto-detected. Read code directly and list them.")
    if not inv["locales"]:
        inv["gaps"].append("No locales auto-detected. Check APP_SUPPORTED_LOCALES and confirm.")
    inv["gaps"].extend([
        "Features must be grouped by the agent from routes + navigation code.",
        "Flows are not auto-detected. Identify by reading code and the UI.",
        "Roles must be read from auth/permission code.",
        "Notifications and integrations must be inferred from code and existing docs.",
    ])
    return inv


def write_output(data: Any, output: str | None) -> None:
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(payload, encoding="utf-8")
        print(f"Wrote {output}")
    else:
        print(payload)


def main() -> int:
    p = argparse.ArgumentParser(prog="scan_repo")
    sub = p.add_subparsers(dest="cmd", required=True)

    for cmd in ("routes", "i18n", "env", "features", "full-inventory"):
        sp = sub.add_parser(cmd)
        sp.add_argument("--repo-root", default=".")
        sp.add_argument("--output", default=None)

    args = p.parse_args()
    root = Path(args.repo_root).resolve()
    if not root.exists():
        print(f"Repo root does not exist: {root}", file=sys.stderr)
        return 2

    if args.cmd == "routes":
        stack = detect_stack(root)
        write_output(detect_routes(root, stack["framework"]), args.output)
    elif args.cmd == "i18n":
        write_output(detect_locales(root), args.output)
    elif args.cmd == "env":
        write_output(detect_env_vars(root), args.output)
    elif args.cmd == "features":
        write_output([], args.output)  # placeholder — agent fills
    elif args.cmd == "full-inventory":
        write_output(full_inventory(root), args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
