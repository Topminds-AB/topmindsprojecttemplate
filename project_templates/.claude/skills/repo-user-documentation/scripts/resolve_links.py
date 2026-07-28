#!/usr/bin/env python3
"""
resolve_links.py — rewrite relative markdown links to absolute wiki paths.

Wiki.js page URLs do not have trailing slashes, so browser-relative link
resolution points one level too high and links break. This script rewrites
any relative link in generated markdown to an absolute wiki path based on
each page's own wiki path.

Run this AFTER authoring, BEFORE publication.

Usage:
    python resolve_links.py rewrite \\
      --plan ./tmp/docs-build/plan.json \\
      --pages-dir ./tmp/docs-build/pages \\
      --system-slug docpilot

What gets rewritten:
    - [text](page)                  → [text](/<slug>/.../<locale>/.../page)
    - [text](./page)                → [text](/<slug>/.../<locale>/.../page)
    - [text](../other/page)         → [text](/<slug>/.../<locale>/.../other/page)
    - [text](section/page)          → [text](/<slug>/.../<locale>/.../section/page)

What is left untouched:
    - [text](http://...)            — external links
    - [text](https://...)           — external links
    - [text](/already/absolute)     — already absolute
    - [text](#anchor)               — same-page anchors
    - ![alt](/u/asset.png)          — Wiki.js asset paths (already absolute)
    - ![alt](http://img.com/x.png)  — external images

The plan.json must contain a `pages[]` array with objects having:
    - wiki_path  (the full wiki path without leading slash)
    - locale     (or absent for L1/L2 pages)
    - type       ("feature", "flow", "locale-landing", etc.)

For each page, resolve_links derives the directory the page "lives in" and
treats every bare or ./-relative link as pointing to a sibling or descendant.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Match markdown links: [text](target) and ![alt](target)
# We capture the target so we can decide whether to rewrite it.
LINK_RE = re.compile(r"(!?\[[^\]]*\])\(([^)]+)\)")

# Targets we never rewrite.
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#", "/", "data:")


def should_skip(target: str) -> bool:
    """Return True if target is already absolute/external and must not be rewritten."""
    t = target.strip()
    return t.startswith(SKIP_PREFIXES)


def page_base_path(wiki_path: str) -> str:
    """
    The directory the page lives in — used to resolve sibling and ./ links.
    For wiki_path='docpilot/anvandardokumentation/sv/funktioner/rapporter'
    returns '/docpilot/anvandardokumentation/sv/funktioner'.
    """
    wiki_path = wiki_path.strip("/")
    parts = wiki_path.split("/")
    if len(parts) <= 1:
        return "/" + wiki_path
    return "/" + "/".join(parts[:-1])


def resolve_target(target: str, base_path: str) -> str:
    """
    Convert a relative markdown link target into an absolute wiki path.
    base_path is the directory of the page that contains the link.
    """
    t = target.strip()

    # Drop any fragment/query for resolution, re-attach at the end.
    suffix = ""
    for sep in ("#", "?"):
        if sep in t:
            idx = t.index(sep)
            suffix = t[idx:]
            t = t[:idx]
            break

    # Normalise ./ and ../ hops manually — we don't want to touch the filesystem.
    segments = [s for s in t.split("/") if s != ""]
    stack: list[str] = list(filter(None, base_path.strip("/").split("/")))

    # If the link starts with '.' or '..', consume base stack accordingly.
    if segments and segments[0] == ".":
        segments = segments[1:]
    while segments and segments[0] == "..":
        if stack:
            stack.pop()
        segments = segments[1:]

    stack.extend(segments)
    resolved = "/" + "/".join(stack)
    return resolved + suffix


def rewrite_file(path: Path, base_path: str) -> tuple[int, int]:
    """
    Rewrite relative markdown links in a single file.
    Returns (rewritten_count, total_link_count).
    """
    text = path.read_text(encoding="utf-8")
    rewritten = 0
    total = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal rewritten, total
        total += 1
        label, target = match.group(1), match.group(2)
        if should_skip(target):
            return match.group(0)
        new_target = resolve_target(target, base_path)
        if new_target != target:
            rewritten += 1
        return f"{label}({new_target})"

    new_text = LINK_RE.sub(repl, text)
    if rewritten:
        path.write_text(new_text, encoding="utf-8")
    return rewritten, total


def cmd_rewrite(args) -> int:
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    pages_dir = Path(args.pages_dir)

    pages = plan.get("pages", [])
    if not pages:
        print("Plan has no 'pages' array. Nothing to do.", file=sys.stderr)
        return 1

    total_rewritten = 0
    total_links = 0
    files_touched = 0
    files_missing = 0

    for page in pages:
        wiki_path = page.get("wiki_path")
        if not wiki_path:
            continue
        # Derive local file path from wiki_path + locale, matching authoring convention.
        # Authoring convention: ./tmp/docs-build/pages/<locale>/<section>/<slug>.md
        locale = page.get("locale")
        # Strip system-slug/anvandardokumentation/<locale>/ prefix to get the local subpath
        rel_parts = wiki_path.strip("/").split("/")
        # Expected shape: <slug>/anvandardokumentation/<locale>/<...>
        if locale and len(rel_parts) >= 3 and rel_parts[2] == locale:
            local_sub = "/".join(rel_parts[3:]) or "home"
            local_file = pages_dir / locale / f"{local_sub}.md"
        else:
            # L1 hub / L2 redirect / uncommon — derive by type if possible
            ptype = page.get("type")
            if ptype == "system-hub":
                local_file = pages_dir / "home.md"
            elif ptype == "section-landing":
                local_file = pages_dir / "documentation.md"
            else:
                # Fallback: treat wiki_path tail as filename
                local_file = pages_dir / (rel_parts[-1] + ".md")

        if not local_file.exists():
            print(f"  [miss] {local_file} — expected from plan, not found", file=sys.stderr)
            files_missing += 1
            continue

        base = page_base_path(wiki_path)
        rewritten, total = rewrite_file(local_file, base)
        total_rewritten += rewritten
        total_links += total
        if rewritten:
            files_touched += 1
            print(f"  [fix]  {local_file.relative_to(pages_dir)} — {rewritten}/{total} links rewritten")

    print(f"\nDone. {total_rewritten}/{total_links} links rewritten across {files_touched} files. {files_missing} files missing.")
    return 0 if files_missing == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(prog="resolve_links")
    sub = p.add_subparsers(dest="cmd", required=True)
    rw = sub.add_parser("rewrite", help="Rewrite relative links in generated markdown.")
    rw.add_argument("--plan", required=True, help="Path to plan.json")
    rw.add_argument("--pages-dir", required=True, help="Directory of generated markdown")
    rw.add_argument("--system-slug", help="Not used directly — wiki_path in plan is authoritative")
    args = p.parse_args()
    if args.cmd == "rewrite":
        return cmd_rewrite(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
