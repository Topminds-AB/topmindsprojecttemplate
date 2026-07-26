#!/usr/bin/env python3
"""File-based local orchestrator for OA/IA/TA workflows inside a repository.

This module coordinates a strict turn-taking workflow between an
Orchestration Agent (OA), an Implementation Agent (IA), and a Test Agent (TA).
The orchestrator watches a shared state file, launches the correct agent
command when requested, prevents concurrent execution, and writes operational
logs for traceability.

Design goals:
    - One shared source of truth: .orch/state.json.
    - One active agent at a time.
    - Predictable handoff through files, not hidden agent memory.
    - Minimal coupling to any specific CLI by delegating commands to config.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ORCH_DIR: Path = Path(".orch")
STATE_PATH: Path = ORCH_DIR / "state.json"
CONFIG_PATH: Path = ORCH_DIR / "config.json"
RUNTIME_DIR: Path = ORCH_DIR / "runtime"
ORCH_LOG_PATH: Path = RUNTIME_DIR / "orchestrator.log"

ALLOWED_NEXT_ACTIONS = {
    "IDLE",
    "OA_START",
    "IA_START",
    "TA_START",
    "OA_REVIEW",
    "WAIT_USER",
    "DONE",
}
ALLOWED_STATUSES = {
    "idle",
    "ready_for_oa",
    "ready_for_ia",
    "ready_for_ta",
    "oa_running",
    "ia_running",
    "ta_running",
    "ready_for_review",
    "waiting_user",
    "done",
    "error",
}


@dataclass(frozen=True)
class AgentSpec:
    """Configuration for an agent process.

    Attributes:
        label: Human-readable name for logs.
        working_directory: Directory where the command should execute.
        command: Full command array to run.
    """

    label: str
    working_directory: str
    command: List[str]


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format.

    Returns:
        Current UTC timestamp as a string.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_directories() -> None:
    """Create required runtime directories if they do not already exist."""
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)


def log_message(message: str) -> None:
    """Append a timestamped message to the orchestrator log and stdout.

    Args:
        message: Log message to write.
    """
    ensure_directories()
    line = f"[{utc_now_iso()}] {message}\n"
    with ORCH_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line)
    print(line, end="")


def load_json_file(path: Path) -> Dict[str, Any]:
    """Load JSON content from disk.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON object.
    """
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json_file(path: Path, payload: Dict[str, Any]) -> None:
    """Write JSON content to disk with indentation.

    Args:
        path: Destination JSON file path.
        payload: JSON-serializable object to persist.
    """
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def validate_state(state: Dict[str, Any]) -> None:
    """Validate required fields and allowed values in state.json.

    Args:
        state: State object loaded from disk.

    Raises:
        ValueError: If a required field is missing or invalid.
    """
    required_keys = {
        "run_id",
        "current_owner",
        "next_action",
        "status",
        "source_prompt_file",
        "target_agent",
        "last_updated_utc",
        "iteration",
        "approved",
        "halt_reason",
        "repo_root",
        "notes",
    }
    missing = required_keys.difference(state.keys())
    if missing:
        raise ValueError(f"state.json is missing keys: {sorted(missing)}")

    if state["next_action"] not in ALLOWED_NEXT_ACTIONS:
        raise ValueError(f"Invalid next_action: {state['next_action']}")

    if state["status"] not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status: {state['status']}")

    if not isinstance(state["iteration"], int) or state["iteration"] < 0:
        raise ValueError("iteration must be a non-negative integer")

    if not isinstance(state["approved"], bool):
        raise ValueError("approved must be a boolean")


def load_state() -> Dict[str, Any]:
    """Load and validate the shared orchestrator state.

    Returns:
        Validated state object.
    """
    state = load_json_file(STATE_PATH)
    validate_state(state)
    return state


def save_state(state: Dict[str, Any]) -> None:
    """Persist state.json after refreshing the update timestamp.

    Args:
        state: State object to save.
    """
    state["last_updated_utc"] = utc_now_iso()
    save_json_file(STATE_PATH, state)


def load_config() -> Dict[str, Any]:
    """Load orchestrator configuration.

    Returns:
        Parsed configuration dictionary.
    """
    return load_json_file(CONFIG_PATH)


def build_agent_spec(config: Dict[str, Any], agent_key: str) -> AgentSpec:
    """Build an AgentSpec from config.json.

    Args:
        config: Full configuration dictionary.
        agent_key: Agent key, such as 'oa', 'ia', or 'ta'.

    Returns:
        Constructed AgentSpec.

    Raises:
        KeyError: If the requested agent configuration is missing.
        ValueError: If the configuration is malformed.
    """
    section = config[agent_key]
    command = section["command"]
    if not isinstance(command, list) or not command:
        raise ValueError(f"{agent_key}.command must be a non-empty list")

    return AgentSpec(
        label=section["label"],
        working_directory=section["working_directory"],
        command=command,
    )


def trim_log_file(path: Path, max_bytes: int) -> None:
    """Trim an oversized log file by keeping the newest bytes.

    Args:
        path: Log file path.
        max_bytes: Maximum size in bytes.
    """
    if not path.exists():
        return

    current_size = path.stat().st_size
    if current_size <= max_bytes:
        return

    with path.open("rb") as handle:
        handle.seek(max(0, current_size - max_bytes))
        content = handle.read()

    with path.open("wb") as handle:
        handle.write(content)


def execute_agent(
    agent_key: str,
    spec: AgentSpec,
    state: Dict[str, Any],
    max_log_bytes: int,
) -> int:
    """Run an agent command and capture stdout/stderr to a dedicated log file.

    Args:
        agent_key: Agent identifier, such as 'oa', 'ia', or 'ta'.
        spec: Agent process specification.
        state: Shared state object to update before launch.
        max_log_bytes: Maximum allowed size for the agent log.

    Returns:
        Process return code.
    """
    ensure_directories()
    log_path = RUNTIME_DIR / f"{agent_key}.last.log"

    if agent_key == "oa":
        state["current_owner"] = "OA"
        state["status"] = "oa_running"
    elif agent_key == "ia":
        state["current_owner"] = "IA"
        state["status"] = "ia_running"
    elif agent_key == "ta":
        state["current_owner"] = "TA"
        state["status"] = "ta_running"
    else:
        raise ValueError(f"Unsupported agent key: {agent_key}")

    save_state(state)
    log_message(f"Launching {spec.label}: {' '.join(spec.command)}")
    start_time = time.time()

    with log_path.open("w", encoding="utf-8") as handle:
        handle.write(f"[{utc_now_iso()}] START {spec.label}\n")
        handle.write(f"cwd={spec.working_directory}\n")
        handle.write(f"command={spec.command}\n\n")

        process = subprocess.run(
            spec.command,
            cwd=spec.working_directory,
            stdout=handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

        elapsed = round(time.time() - start_time, 2)
        handle.write(
            f"\n[{utc_now_iso()}] END returncode={process.returncode} elapsed={elapsed}s\n"
        )

    trim_log_file(log_path, max_log_bytes)
    log_message(f"{spec.label} finished with exit code {process.returncode}")
    return process.returncode


def handle_agent_start(config: Dict[str, Any], state: Dict[str, Any], agent_key: str) -> None:
    """Handle a request to start an agent from state.json.

    Args:
        config: Loaded config.json content.
        state: Current state object.
        agent_key: Agent identifier to launch.
    """
    spec = build_agent_spec(config, agent_key)
    max_log_bytes = int(config.get("max_log_bytes", 2_000_000))
    return_code = execute_agent(agent_key, spec, state, max_log_bytes=max_log_bytes)

    if return_code != 0:
        state["status"] = "error"
        state["halt_reason"] = f"{agent_key.upper()} exited with code {return_code}"
        state["next_action"] = "WAIT_USER"
        state["current_owner"] = "USER"
        save_state(state)


def route_action(config: Dict[str, Any], state: Dict[str, Any]) -> None:
    """Dispatch the current next_action to the correct handler.

    Args:
        config: Loaded configuration.
        state: Current orchestrator state.
    """
    next_action = state["next_action"]

    if next_action in {"OA_START", "OA_REVIEW"}:
        handle_agent_start(config, state, "oa")
        return

    if next_action == "IA_START":
        handle_agent_start(config, state, "ia")
        return

    if next_action == "TA_START":
        handle_agent_start(config, state, "ta")
        return

    if next_action in {"IDLE", "WAIT_USER", "DONE"}:
        return

    raise ValueError(f"Unhandled next_action: {next_action}")


def main() -> int:
    """Start the orchestrator loop.

    Returns:
        Process exit code.
    """
    ensure_directories()

    if not STATE_PATH.exists():
        log_message("Missing .orch/state.json")
        return 1

    if not CONFIG_PATH.exists():
        log_message("Missing .orch/config.json")
        return 1

    config = load_config()
    poll_interval = float(config.get("poll_interval_seconds", 2))

    log_message("Orchestrator started")

    try:
        while True:
            try:
                state = load_state()
                route_action(config, state)
            except Exception as exc:  # pylint: disable=broad-except
                log_message(f"ERROR: {exc}")
                try:
                    state = load_state()
                    state["status"] = "error"
                    state["next_action"] = "WAIT_USER"
                    state["halt_reason"] = str(exc)
                    state["current_owner"] = "USER"
                    save_state(state)
                except Exception as nested_exc:  # pylint: disable=broad-except
                    log_message(f"Failed to write error state: {nested_exc}")

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        log_message("Orchestrator stopped by user")
        return 0


if __name__ == "__main__":
    sys.exit(main())
