# Handoffer

Local FastAPI service, localhost dashboard, and macOS menu-bar monitor for agent capacity.

## Run

```sh
./scripts/install.sh
.venv/bin/handoffer setup --write-config
.venv/bin/handoffer serve
open dist/Handoffer.app
```

Verify: `.venv/bin/python tests/self_check.py`

Dashboard: `http://127.0.0.1:8765`.

The menu app is an accessory app: closing its dashboard leaves its top-bar icon running. Use **Quit Handoffer** to stop it.

## Connect real limits

Usage access differs per vendor and local install; no portable CLI endpoint exists for Codex, Claude, and Muse. Configure each provider with a deterministic JSON command or JSON file in `~/.config/handoffer/config.json`. See `config.example.json`.

Expected source output:

```json
{"five_hour":{"used_percent":95,"resets_at":"2026-09-20T18:00:00Z"},"weekly":{"remaining_percent":60}}
```

`source: "command"` executes an argv list without a shell. `json_file` never executes code.

## Handoff policy

`handoffer hook --agent claude --repo /repo` reads current configured usage. At or above `threshold_percent` it deterministically writes `/repo/HANDOFF.md` and returns exit code `42`; below it returns `0`. An existing handoff is never overwritten. Default policy never delegates. Set `auto_delegate: true` only with a `delegate_command` configured on target provider; it picks agent with greatest minimum remaining window and passes `HANDOFF_FILE`, `HANDOFF_REPO`, and `HANDOFF_FROM`.

Hook adapters: [integrations/README.md](integrations/README.md).

Setup safely merges the Claude Code pre-tool hook into `~/.claude/settings.json`.
