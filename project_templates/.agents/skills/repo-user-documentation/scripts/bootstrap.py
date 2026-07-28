#!/usr/bin/env python3
"""
bootstrap.py — one-command setup for repo-user-documentation in any repo.

Detects OS, installs Python dependencies with the right flags, installs
chromium for Playwright, validates .env, and runs login-check.

Usage:
    python .agents/skills/repo-user-documentation/scripts/bootstrap.py
    python .agents/skills/repo-user-documentation/scripts/bootstrap.py --skip-deps
    python .agents/skills/repo-user-documentation/scripts/bootstrap.py --skip-login

Works on:
  - Linux (Debian/Ubuntu) — uses --break-system-packages for pip
  - macOS — standard pip
  - Windows / WSL2 — standard pip
  - Alpine and similar — standard pip with venv recommended

Exit codes:
  0 = ready to use
  1 = manual action required
  2 = unrecoverable failure
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_PACKAGES = ["playwright", "python-dotenv", "pillow", "pyyaml"]
REQUIRED_PYTHON = (3, 9)


def color(text: str, c: str) -> str:
    """ANSI color wrapper. Disabled on Windows cmd without colorama."""
    if os.environ.get("NO_COLOR") or platform.system() == "Windows" and not os.environ.get("WT_SESSION"):
        return text
    codes = {"red": 31, "green": 32, "yellow": 33, "blue": 34, "cyan": 36, "gray": 90}
    return f"\033[{codes.get(c, 0)}m{text}\033[0m"


def step(msg: str) -> None:
    print(f"{color('▸', 'cyan')} {msg}")


def ok(msg: str) -> None:
    print(f"  {color('✓', 'green')} {msg}")


def warn(msg: str) -> None:
    print(f"  {color('!', 'yellow')} {msg}")


def fail(msg: str) -> None:
    print(f"  {color('✗', 'red')} {msg}", file=sys.stderr)



def detect_os() -> dict[str, str]:
    """Return a dict describing the current platform."""
    info = {
        "system": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }
    # Detect WSL specifically
    if info["system"] == "Linux":
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    info["system"] = "WSL"
        except Exception:
            pass
    # Detect distro for Linux pip flags
    if info["system"] in ("Linux", "WSL"):
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read().lower()
                if "debian" in content or "ubuntu" in content:
                    info["distro"] = "debian"
                elif "alpine" in content:
                    info["distro"] = "alpine"
                else:
                    info["distro"] = "other"
        except Exception:
            info["distro"] = "unknown"
    return info


def check_python_version() -> bool:
    if sys.version_info < REQUIRED_PYTHON:
        fail(f"Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ required, "
             f"found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    ok(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def pip_install(packages: list[str], os_info: dict[str, str]) -> bool:
    """Install packages with platform-appropriate flags."""
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    # Debian/Ubuntu (incl. WSL Ubuntu) requires --break-system-packages from 3.11+
    if os_info["system"] in ("Linux", "WSL") and os_info.get("distro") == "debian":
        cmd.append("--break-system-packages")
    cmd.extend(packages)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            fail(f"pip install failed:\n{result.stderr}")
            return False
        return True
    except FileNotFoundError:
        fail("pip not found in current Python environment")
        return False


def check_or_install_packages(os_info: dict[str, str], skip: bool) -> bool:
    if skip:
        warn("Skipping dependency installation (--skip-deps)")
        return True
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    if not missing:
        ok(f"All Python deps already installed: {', '.join(REQUIRED_PACKAGES)}")
        return True
    step(f"Installing: {', '.join(missing)}")
    if not pip_install(missing, os_info):
        return False
    ok(f"Installed: {', '.join(missing)}")
    return True



def install_chromium(skip: bool) -> bool:
    if skip:
        warn("Skipping chromium install (--skip-deps)")
        return True
    step("Installing Playwright chromium browser")
    cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            fail(f"playwright install chromium failed:\n{result.stderr}")
            warn("Try manually: python -m playwright install chromium")
            warn("On Linux/WSL you may also need: python -m playwright install-deps chromium")
            return False
        ok("Chromium installed")
        return True
    except Exception as e:
        fail(f"playwright install failed: {e}")
        return False


def validate_env(repo_root: Path) -> tuple[bool, list[str]]:
    """Read .env and check that all required variables are set.
    Returns (ok, missing_keys)."""
    env_path = repo_root / ".env"
    if not env_path.exists():
        fail(f".env not found at {env_path}")
        warn("Create one based on .env.example or the SKILL.md env reference")
        return False, []
    env: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")

    required = [
        "APP_URL", "APP_USERNAME", "APP_PASSWORD",
        "APP_SUPPORTED_LOCALES", "APP_LOCALE_SWITCH_STRATEGY",
        "WIKIJS_URL", "WIKIJS_API_TOKEN", "WIKIJS_DEFAULT_LOCALE",
        "WIKIJS_SYSTEM_SLUG",
    ]
    recommended = ["APP_POST_LOGIN_URL_CONTAINS"]

    missing = [k for k in required if not env.get(k)]
    missing_recommended = [k for k in recommended if not env.get(k)]

    if missing:
        fail(f"Missing required env vars: {', '.join(missing)}")
        return False, missing
    ok("All required env vars present")
    if missing_recommended:
        warn(f"Recommended vars not set: {', '.join(missing_recommended)}")
        warn("Without APP_POST_LOGIN_URL_CONTAINS, failed logins pass silently")
    return True, []


def run_login_check(repo_root: Path, skip: bool) -> bool:
    if skip:
        warn("Skipping login-check (--skip-login)")
        return True
    step("Running login-check against deployed environment")
    capture_script = (Path(__file__).parent / "capture.py").resolve()
    if not capture_script.exists():
        fail(f"capture.py not found at {capture_script}")
        return False

    # Determine first locale from .env
    env_path = repo_root / ".env"
    locale = "sv"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("APP_SUPPORTED_LOCALES="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                first = value.split(",")[0].strip()
                if first:
                    locale = first
                break

    cmd = [sys.executable, str(capture_script), "login-check", "--locale", locale]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root))
        out = (result.stdout or "") + (result.stderr or "")
        if result.returncode != 0 or "Login OK" not in out:
            fail("login-check failed")
            print(out)
            warn("Common causes: wrong APP_USERNAME_SELECTOR/APP_PASSWORD_SELECTOR/APP_SUBMIT_SELECTOR,")
            warn("missing APP_POST_LOGIN_URL_CONTAINS, or app not reachable from this host")
            return False
        ok(f"Login OK on locale '{locale}'")
        return True
    except Exception as e:
        fail(f"login-check execution failed: {e}")
        return False



def main() -> int:
    parser = argparse.ArgumentParser(
        prog="bootstrap",
        description="One-command setup for repo-user-documentation."
    )
    parser.add_argument("--skip-deps", action="store_true",
                        help="Skip Python pip and Playwright chromium installation")
    parser.add_argument("--skip-login", action="store_true",
                        help="Skip the deployed-env login-check step")
    parser.add_argument("--repo-root", default=".",
                        help="Path to the repo root (default: current directory)")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    if not repo.exists():
        fail(f"Repo root does not exist: {repo}")
        return 2

    print(color("Bootstrapping repo-user-documentation", "blue"))
    print(color(f"Repo: {repo}", "gray"))

    step("Detecting environment")
    os_info = detect_os()
    ok(f"{os_info['system']} {os_info['machine']} (Python {os_info['python']})")
    if os_info.get("distro"):
        ok(f"Distro: {os_info['distro']}")

    step("Checking Python version")
    if not check_python_version():
        return 2

    step("Checking Python dependencies")
    if not check_or_install_packages(os_info, args.skip_deps):
        return 2

    step("Checking Playwright browser")
    if not install_chromium(args.skip_deps):
        return 1  # not fatal — user may install manually

    step("Validating .env")
    env_ok, missing = validate_env(repo)
    if not env_ok:
        warn("Bootstrap will continue, but later steps will fail until .env is complete")
        if missing:
            print()
            print(color("Add the following to your .env (values not shown for security):", "yellow"))
            for k in missing:
                print(f"  {k}=...")
        return 1

    step("Verifying deployed environment login")
    if not run_login_check(repo, args.skip_login):
        warn("Bootstrap completed with login-check failure")
        warn("Inspect APP_* env vars and selectors, then re-run with --skip-deps")
        return 1

    print()
    print(color("✓ Bootstrap complete. Ready to run prompt 00b or 01.", "green"))
    print(color("  Next: edit docs/docs-config.yaml or run prompt 00b to fill it.", "gray"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
