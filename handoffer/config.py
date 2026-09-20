from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from .models import ProviderConfig, Settings

CONFIG_PATH = Path(os.environ.get("HANDOFF_CONFIG", Path.home() / ".config" / "handoffer" / "config.json"))
DEFAULTS = [
    ProviderConfig(id="codex", name="Codex", executable="codex", source="codex_app_server"),
    ProviderConfig(id="claude", name="Claude Code", executable="claude"),
    ProviderConfig(id="muse", name="Muse Code", executable="muse"),
    ProviderConfig(id="gemini", name="Gemini CLI", executable="gemini"),
    ProviderConfig(id="aider", name="Aider", executable="aider"),
]


def load_settings() -> Settings:
    if not CONFIG_PATH.exists():
        return Settings(providers=DEFAULTS)
    settings = Settings.model_validate_json(CONFIG_PATH.read_text())
    for provider in settings.providers:
        if provider.id == "codex" and provider.source == "disabled" and not provider.command and not provider.json_file:
            provider.source = "codex_app_server"
    return settings


def save_settings(settings: Settings) -> Settings:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(settings.model_dump(mode="json"), indent=2) + "\n")
    return settings


def discover(settings: Settings) -> Settings:
    known = {provider.id for provider in settings.providers}
    for provider in DEFAULTS:
        if provider.id not in known and shutil.which(provider.executable):
            settings.providers.append(provider)
    return settings
