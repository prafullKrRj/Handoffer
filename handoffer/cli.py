from __future__ import annotations

import argparse
import sys

import uvicorn

from .config import discover, load_settings, save_settings
from .background import install as install_background, status as background_status, stop as stop_background
from .capture import capture_claude, claude_statusline
from .handoff import run_hook


def main() -> None:
    parser = argparse.ArgumentParser(prog="handoffer")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("serve")
    setup = commands.add_parser("setup")
    setup.add_argument("--write-config", action="store_true")
    hook = commands.add_parser("hook")
    hook.add_argument("--agent", required=True)
    hook.add_argument("--repo")
    hook.add_argument("--summary", default="")
    background = commands.add_parser("background")
    background.add_argument("action", choices=["install", "stop", "status"])
    capture = commands.add_parser("capture")
    capture.add_argument("agent", choices=["claude"])
    commands.add_parser("claude-statusline")
    args = parser.parse_args()
    if args.command == "serve":
        uvicorn.run("handoffer.app:app", host="127.0.0.1", port=8765)
    elif args.command == "setup":
        settings = discover(load_settings())
        if args.write_config:
            save_settings(settings)
        print("Detected: " + ", ".join(item.name for item in settings.providers if __import__("shutil").which(item.executable)))
    elif args.command == "background":
        {"install": install_background, "stop": stop_background, "status": background_status}[args.action]()
    elif args.command == "capture":
        if args.agent == "claude":
            capture_claude(sys.stdin.read())
    elif args.command == "claude-statusline":
        claude_statusline()
    else:
        sys.exit(run_hook(args.agent, args.repo, args.summary))


if __name__ == "__main__":
    main()
