from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path


CLAUDE_LIMITS = Path.home() / ".config" / "handoffer" / "claude-limits.json"
CLAUDE_STATUSLINE = Path.home() / ".config" / "handoffer" / "claude-statusline-command.json"


def capture_claude(payload: str) -> bool:
    try:
        limits = json.loads(payload).get("rate_limits", {})
        five_hour = limits.get("five_hour") or {}
        weekly = limits.get("seven_day") or limits.get("weekly") or {}
        if five_hour.get("used_percentage") is None and weekly.get("used_percentage") is None:
            return False
        CLAUDE_LIMITS.parent.mkdir(parents=True, exist_ok=True)
        CLAUDE_LIMITS.write_text(json.dumps({
            "five_hour": {"used_percent": five_hour.get("used_percentage"), "resets_at": five_hour.get("resets_at")},
            "weekly": {"used_percent": weekly.get("used_percentage"), "resets_at": weekly.get("resets_at")},
        }) + "\n")
        return True
    except (json.JSONDecodeError, AttributeError):
        return False


def claude_statusline() -> None:
    payload = sys.stdin.read()
    capture_claude(payload)
    if not CLAUDE_STATUSLINE.exists():
        return
    command = json.loads(CLAUDE_STATUSLINE.read_text()).get("command")
    if command:
        result = subprocess.run(shlex.split(command), input=payload, text=True, capture_output=True, check=False)
        sys.stdout.write(result.stdout)
