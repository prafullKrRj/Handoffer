#!/bin/zsh
set -euo pipefail
root=${0:A:h:h}
venv="$root/.venv"
python3 -m venv "$venv"
"$venv/bin/pip" install --upgrade pip
"$venv/bin/pip" install -e "$root"
zsh "$root/scripts/build-mac-app.sh"
mkdir -p "$HOME/.config/handoffer/hooks"
cat > "$HOME/.config/handoffer/serve" <<EOF
#!/bin/zsh
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
exec "$venv/bin/handoffer" serve
EOF
chmod +x "$HOME/.config/handoffer/serve"
"$venv/bin/handoffer" background install
ditto "$root/dist/Handoffer.app" "/Applications/Handoffer.app"
cat > "$HOME/.config/handoffer/hooks/check-limit" <<EOF
#!/bin/zsh
payload=\$(cat)
printf '%s' "\$payload" | "$venv/bin/handoffer" capture claude
exec "$venv/bin/handoffer" hook --agent "\${1:?agent id}" --repo "\${PWD}" --summary "\${2:-}"
EOF
chmod +x "$HOME/.config/handoffer/hooks/check-limit"
mkdir -p "$HOME/.claude"
python3 - "$HOME/.claude/settings.json" "$HOME/.config/handoffer/hooks/check-limit claude" "$venv" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
command = sys.argv[2]
settings = json.loads(path.read_text()) if path.exists() else {}
hooks = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
if not any(item.get("matcher") == ".*" and any(hook.get("command") == command for hook in item.get("hooks", [])) for item in hooks):
    hooks.append({"matcher": ".*", "hooks": [{"type": "command", "command": command, "timeout": 30}]})
status_line = settings.get("statusLine")
wrapper = f"{Path(sys.argv[3])}/bin/handoffer claude-statusline"
if status_line and status_line.get("command") != wrapper:
    config = Path.home() / ".config" / "handoffer" / "claude-statusline-command.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(json.dumps({"command": status_line["command"]}) + "\n")
    settings["statusLine"] = {"type": "command", "command": wrapper}
path.write_text(json.dumps(settings, indent=2) + "\n")
PY
echo "Installed. Background server: $venv/bin/handoffer background status"
echo "Open menu app: open /Applications/Handoffer.app"
echo "Hook command: $HOME/.config/handoffer/hooks/check-limit claude"
