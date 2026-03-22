"""Core runner: parse talons, check schedule, spawn Claude."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from . import talon as talon_mod
from .scheduler import is_due
from .notify import notify


TALONS_DIR = Path.home() / ".kisstalon" / "talons"
LOGS_DIR = Path.home() / ".kisstalon" / "logs"
CONFIG_PATH = Path.home() / ".kisstalon" / "config.toml"


def _load_config() -> dict:
    config_path = CONFIG_PATH
    if not config_path.exists():
        return {}
    try:
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib  # type: ignore
        return tomllib.loads(config_path.read_text())
    except Exception:
        return {}


def _build_claude_cmd(talon: talon_mod.Talon, path: Path, config: dict) -> list[str]:
    allowed = ",".join(talon.permissions)
    prompt = (
        f"You are a KISStalon agent. Read the talon file at {path}. "
        f"Do the task described in the prompt body. "
        f"Append your findings under '# Invocations' with today's date as a ## heading. "
        f"If something urgent is found, output a line starting with 'NOTIFY:' followed by the message."
    )
    cmd = [
        "claude",
        "--print",
        "--allowedTools", allowed,
        "--prompt", prompt,
    ]
    extra = config.get("claude", {}).get("extra_flags", "")
    if extra:
        cmd.extend(extra.split())
    return cmd


def run_talon(talon: talon_mod.Talon, path: Path, config: dict) -> None:
    """Run a single talon: spawn Claude, handle output, update state."""
    print(f"Running talon: {talon.id}")
    cmd = _build_claude_cmd(talon, path, config)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout
    except subprocess.TimeoutExpired:
        output = "ERROR: Claude timed out after 5 minutes"
    except FileNotFoundError:
        print("Error: 'claude' CLI not found in PATH")
        return

    # Log output
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"{talon.id}_{timestamp}.log"
    log_file.write_text(output)

    # Append invocation to the talon file
    talon_mod.append_invocation(path, output)

    # Check for NOTIFY: lines
    notify_config = config.get("notify", {})
    for line in output.splitlines():
        if line.startswith("NOTIFY:"):
            msg = line[len("NOTIFY:"):].strip()
            notify(talon.notify, f"KISStalon: {talon.id}", msg, {
                "ntfy_url": notify_config.get("ntfy", {}).get("url", ""),
                "ntfy_topic": notify_config.get("ntfy", {}).get("topic", "kisstalon"),
            })

    # Update last_run
    talon.last_run = datetime.now()
    talon_mod.save(talon, path)
    print(f"  Finished: {talon.id}")


def tick() -> None:
    """Walk all talons, run any that are due."""
    if not TALONS_DIR.exists():
        print("No talons directory found. Run 'kisstalon init' first.")
        return

    config = _load_config()
    talon_files = sorted(TALONS_DIR.glob("*.md"))

    if not talon_files:
        print("No talons found.")
        return

    ran = 0
    for path in talon_files:
        try:
            t = talon_mod.parse(path)
        except Exception as e:
            print(f"  Skipping {path.name}: {e}")
            continue

        if is_due(t.schedule, t.last_run):
            run_talon(t, path, config)
            ran += 1

    if ran == 0:
        print("No talons due.")
