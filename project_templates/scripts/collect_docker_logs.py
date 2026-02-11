#!/usr/bin/env python3
"""
Collect Docker container logs from docker-compose projects.

This script:
1. Finds docker-compose files in the current directory
2. Extracts container names from the compose configuration
3. Collects logs from all running containers
4. Creates a timestamped zip file in .dockerlogs/

Usage:
    python scripts/collect_docker_logs.py

    # Or from any directory:
    python /path/to/collect_docker_logs.py
"""

import os
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def find_project_root() -> Path:
    """Find the project root by looking for docker-compose files."""
    current = Path.cwd()

    # Check current directory first
    compose_files = list(current.glob("docker-compose*.yml")) + list(current.glob("docker-compose*.yaml"))
    if compose_files:
        return current

    # Walk up the directory tree
    for parent in current.parents:
        compose_files = list(parent.glob("docker-compose*.yml")) + list(parent.glob("docker-compose*.yaml"))
        if compose_files:
            return parent

    return current


def get_project_prefix(project_root: Path) -> str:
    """Get project prefix from directory name."""
    return project_root.name.lower().replace(" ", "_").replace("-", "_")


def get_compose_containers() -> list[str]:
    """Get container names from docker-compose configuration."""
    containers = []

    try:
        # Use docker compose ps to get running containers
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and result.stdout.strip():
            containers = [name.strip() for name in result.stdout.strip().split("\n") if name.strip()]
    except subprocess.TimeoutExpired:
        print("Warning: docker compose ps timed out")
    except FileNotFoundError:
        print("Warning: docker command not found")
    except Exception as e:
        print(f"Warning: Error getting compose containers: {e}")

    # Fallback: try to get all running containers if compose ps fails
    if not containers:
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and result.stdout.strip():
                containers = [name.strip() for name in result.stdout.strip().split("\n") if name.strip()]
        except Exception as e:
            print(f"Warning: Error getting docker containers: {e}")

    return containers


def get_container_logs(container_name: str, tail_lines: int = 10000) -> str:
    """Get logs from a specific container."""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail_lines), "--timestamps", container_name],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Combine stdout and stderr (docker logs outputs to both)
        logs = ""
        if result.stdout:
            logs += result.stdout
        if result.stderr:
            logs += result.stderr

        return logs
    except subprocess.TimeoutExpired:
        return f"[ERROR] Timeout while fetching logs for {container_name}\n"
    except Exception as e:
        return f"[ERROR] Failed to get logs for {container_name}: {e}\n"


def collect_docker_info() -> str:
    """Collect general docker information."""
    info_parts = []

    # Docker version
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            info_parts.append(f"Docker Version: {result.stdout.strip()}")
    except Exception:
        pass

    # Docker compose version
    try:
        result = subprocess.run(
            ["docker", "compose", "version", "--short"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            info_parts.append(f"Docker Compose Version: {result.stdout.strip()}")
    except Exception:
        pass

    # Running containers
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Image}}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            info_parts.append(f"\nRunning Containers:\n{result.stdout}")
    except Exception:
        pass

    return "\n".join(info_parts)


def main():
    """Main entry point."""
    print("Docker Log Collector")
    print("=" * 50)

    # Find project root
    project_root = find_project_root()
    os.chdir(project_root)
    print(f"Project root: {project_root}")

    # Get project prefix
    project_prefix = get_project_prefix(project_root)
    print(f"Project prefix: {project_prefix}")

    # Create output directory
    output_dir = project_root / ".dockerlogs"
    output_dir.mkdir(exist_ok=True)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    zip_filename = f"{project_prefix}_docker_logs_{timestamp}.zip"
    zip_path = output_dir / zip_filename

    print(f"Output file: {zip_path}")
    print()

    # Get containers
    print("Finding containers...")
    containers = get_compose_containers()

    if not containers:
        print("No running containers found!")
        sys.exit(1)

    print(f"Found {len(containers)} container(s):")
    for container in containers:
        print(f"  - {container}")
    print()

    # Collect logs
    print("Collecting logs...")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add docker info
        docker_info = collect_docker_info()
        zf.writestr("_docker_info.txt", docker_info)
        print("  + _docker_info.txt")

        # Add container logs
        for container in containers:
            print(f"  + {container}.log", end="", flush=True)
            logs = get_container_logs(container)

            if logs:
                zf.writestr(f"{container}.log", logs)
                # Show log size
                size_kb = len(logs.encode('utf-8')) / 1024
                print(f" ({size_kb:.1f} KB)")
            else:
                zf.writestr(f"{container}.log", "[No logs available]\n")
                print(" (empty)")

    # Final summary
    zip_size = zip_path.stat().st_size / 1024
    print()
    print("=" * 50)
    print(f"Done! Created: {zip_path}")
    print(f"Size: {zip_size:.1f} KB")
    print(f"Contains logs from {len(containers)} container(s)")


if __name__ == "__main__":
    main()
