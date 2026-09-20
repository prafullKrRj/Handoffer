from __future__ import annotations

import asyncio
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .config import load_settings
from .providers import all_status


def _percent(agent) -> float:
    return max(value or 0 for value in (agent.five_hour.used_percent, agent.weekly.used_percent))


async def create_if_needed(agent_id: str, repo: Path, summary: str = "") -> tuple[bool, str]:
    settings = load_settings()
    agents = await all_status(settings.providers)
    agent = next((item for item in agents if item.id == agent_id), None)
    if not agent or not agent.available:
        return False, f"HANDOFF_SKIP agent={agent_id} reason=usage-unavailable"
    if _percent(agent) < settings.threshold_percent:
        return False, f"HANDOFF_SKIP agent={agent_id} usage={_percent(agent):.0f}% threshold={settings.threshold_percent:.0f}%"

    stamp = datetime.now(timezone.utc).isoformat()
    path = repo / "HANDOFF.md"
    if path.exists():
        path = repo / f"HANDOFF-{agent_id}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.md"
    content = f"""# Handoff\n\nCreated automatically by Handoffer hook.\n\n- Agent: {agent.name}\n- Created: {stamp}\n- Trigger: usage reached {settings.threshold_percent:.0f}%\n- 5-hour remaining: {agent.five_hour.remaining_percent}%\n- Weekly remaining: {agent.weekly.remaining_percent}%\n\n## Continue from here\n\n{summary or 'Record current task state, changed files, verification, and next command before transferring.'}\n\n<!-- handoffer:auto:{agent_id}:{stamp} -->\n"""
    path.write_text(content)
    message = f"HANDOFF_CREATED file={path} agent={agent.name}"
    if settings.auto_delegate:
        candidates = [item for item in agents if item.id != agent_id and item.available and _percent(item) < settings.threshold_percent]
        candidate = max(candidates, key=lambda item: min(item.five_hour.remaining_percent or 0, item.weekly.remaining_percent or 0), default=None)
        target = next((item for item in settings.providers if candidate and item.id == candidate.id), None)
        if target and target.delegate_command:
            environment = os.environ | {"HANDOFF_FILE": str(path), "HANDOFF_REPO": str(repo), "HANDOFF_FROM": agent_id}
            subprocess.run(target.delegate_command, env=environment, check=False, timeout=20)
            message += f" delegated_to={target.name}"
    return True, message


def run_hook(agent_id: str, repo: str | None = None, summary: str = "") -> int:
    created, message = asyncio.run(create_if_needed(agent_id, Path(repo or os.getcwd()), summary))
    print(message)
    return 42 if created else 0
