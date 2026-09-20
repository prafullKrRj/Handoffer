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
echo "Installed. Start dashboard: $venv/bin/handoffer serve"
echo "Open menu app: open $root/dist/Handoffer.app"
echo "Hook command: $HOME/.config/handoffer/hooks/check-limit claude"
