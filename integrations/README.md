# Deterministic hooks

`check-limit <agent-id>` exits `42` when it writes `HANDOFF.md`; use it as a blocking pre-action hook. The threshold comes only from Handoffer settings. Agents do not decide when to hand off.

Merge `claude-code-settings.json` into `~/.claude/settings.json`. Claude Code then checks before every tool use.

Codex and Muse currently expose no documented per-tool local hook API. Wrap their launch command or call this same executable from their supported lifecycle notification setting. The backend remains agent-agnostic: any agent with a configured JSON source and this hook gets identical deterministic behavior.
