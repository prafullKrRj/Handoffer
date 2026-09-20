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
exec "$venv/bin/handoffer" serve
EOF
chmod +x "$HOME/.config/handoffer/serve"
cat > "$HOME/.config/handoffer/hooks/check-limit" <<EOF
#!/bin/zsh
exec "$venv/bin/handoffer" hook --agent "\${1:?agent id}" --repo "\${PWD}" --summary "\${2:-}"
EOF
chmod +x "$HOME/.config/handoffer/hooks/check-limit"
mkdir -p "$HOME/.claude"
python3 - "$HOME/.claude/settings.json" "$HOME/.config/handoffer/hooks/check-limit claude" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
command = sys.argv[2]
settings = json.loads(path.read_text()) if path.exists() else {}
hooks = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
if not any(item.get("matcher") == ".*" and any(hook.get("command") == command for hook in item.get("hooks", [])) for item in hooks):
    hooks.append({"matcher": ".*", "hooks": [{"type": "command", "command": command, "timeout": 30}]})
path.write_text(json.dumps(settings, indent=2) + "\n")
PY
echo "Installed. Start dashboard: $venv/bin/handoffer serve"
echo "Open menu app: open $root/dist/Handoffer.app"
echo "Hook command: $HOME/.config/handoffer/hooks/check-limit claude"
