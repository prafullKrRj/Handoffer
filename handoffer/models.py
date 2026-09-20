from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Window(BaseModel):
    used_percent: float | None = Field(default=None, ge=0, le=100)
    remaining_percent: float | None = Field(default=None, ge=0, le=100)
    resets_at: datetime | None = None


class AgentStatus(BaseModel):
    id: str
    name: str
    kind: str
    installed: bool
    available: bool
    detail: str | None = None
    five_hour: Window = Field(default_factory=Window)
    weekly: Window = Field(default_factory=Window)


class ProviderConfig(BaseModel):
    id: str
    name: str
    executable: str
    source: Literal["codex_app_server", "command", "json_file", "disabled"] = "disabled"
    command: list[str] | None = None
    json_file: str | None = None
    delegate_command: list[str] | None = None


class Settings(BaseModel):
    threshold_percent: float = Field(default=95, ge=1, le=100)
    auto_delegate: bool = False
    providers: list[ProviderConfig] = Field(default_factory=list)


class SettingsPatch(BaseModel):
    threshold_percent: float | None = Field(default=None, ge=1, le=100)
    auto_delegate: bool | None = None


class StatusResponse(BaseModel):
    agents: list[AgentStatus]
    policy: dict[str, float | bool]
