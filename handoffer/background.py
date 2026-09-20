from __future__ import annotations

import os
import plistlib
import subprocess
from pathlib import Path

LABEL = "local.handoffer.server"
PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def _domain() -> str:
    return f"gui/{os.getuid()}"


def install() -> None:
    serve = Path.home() / ".config" / "handoffer" / "serve"
    if not serve.exists():
        raise RuntimeError("Run scripts/install.sh first.")
    PLIST.parent.mkdir(parents=True, exist_ok=True)
    with PLIST.open("wb") as file:
        plistlib.dump({
            "Label": LABEL,
            "ProgramArguments": [str(serve)],
            "RunAtLoad": True,
            "KeepAlive": {"SuccessfulExit": False},
            "StandardOutPath": "/tmp/handoffer-server.log",
            "StandardErrorPath": "/tmp/handoffer-server.log",
        }, file)
    subprocess.run(["launchctl", "bootout", _domain(), str(PLIST)], capture_output=True)
    subprocess.run(["launchctl", "bootstrap", _domain(), str(PLIST)], check=True)
    print(f"BACKGROUND_ENABLED {PLIST}")


def stop() -> None:
    subprocess.run(["launchctl", "bootout", _domain(), str(PLIST)], check=False)
    print("BACKGROUND_DISABLED")


def status() -> None:
    result = subprocess.run(["launchctl", "print", f"{_domain()}/{LABEL}"], capture_output=True, text=True)
    print("BACKGROUND_RUNNING" if result.returncode == 0 else "BACKGROUND_STOPPED")
