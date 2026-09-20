from __future__ import annotations

import asyncio
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import AgentStatus, ProviderConfig, Window


def _window(raw: dict[str, Any] | None) -> Window:
    raw = raw or {}
    used = raw.get("used_percent")
    remaining = raw.get("remaining_percent")
    if used is None and remaining is not None:
        used = 100 - float(remaining)
    if remaining is None and used is not None:
        remaining = 100 - float(used)
    reset = raw.get("resets_at")
    if isinstance(reset, (int, float)):
        reset = datetime.fromtimestamp(reset).isoformat()
    return Window(used_percent=used, remaining_percent=remaining, resets_at=reset)


def _decode(raw: Any) -> tuple[Window, Window]:
    """Accept Handoffer JSON plus Codex-style rate-limit response shapes."""
    if isinstance(raw, dict) and "rateLimits" in raw:
        raw = raw["rateLimits"]
    raw = raw or {}
    short = raw.get("five_hour") or raw.get("fiveHour") or raw.get("primary")
    week = raw.get("weekly") or raw.get("week") or raw.get("secondary")
    return _window(short), _window(week)


async def _command(command: list[str]) -> Any:
    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=12)
    if process.returncode:
        raise RuntimeError(stderr.decode().strip() or f"exit {process.returncode}")
    return json.loads(stdout)


async def status(provider: ProviderConfig) -> AgentStatus:
    installed = bool(shutil.which(provider.executable))
    base = AgentStatus(
        id=provider.id, name=provider.name, kind=provider.executable, installed=installed,
        available=False, detail="Configure a JSON source in Settings.",
    )
    if not installed:
        base.detail = f"{provider.executable} not found"
        return base
    try:
        if provider.source == "command" and provider.command:
            raw = await _command(provider.command)
        elif provider.source == "json_file" and provider.json_file:
            raw = json.loads(Path(provider.json_file).expanduser().read_text())
        else:
            return base
        base.five_hour, base.weekly = _decode(raw)
        base.available = base.five_hour.used_percent is not None or base.weekly.used_percent is not None
        base.detail = None if base.available else "Source returned no supported usage windows."
        return base
    except Exception as error:  # no provider failure may take dashboard down
        base.detail = str(error)
        return base


async def all_status(providers: list[ProviderConfig]) -> list[AgentStatus]:
    return await asyncio.gather(*(status(provider) for provider in providers))
