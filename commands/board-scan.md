---
description: "TODO: board-scan — describe what this slash command does"
argument-hint: "[run|install|uninstall]"
---

Run `board-scan $ARGUMENTS` from the user's current directory using the Bash tool.

`board-scan` is a Python tool at `~/scripts/board-scan/bin/board-scan.py` (symlinked to `~/.local/bin/board-scan`). This slash command file is at `~/scripts/board-scan/commands/board-scan.md` (symlinked to `~/.claude/commands/board-scan.md`).

Actions:

- **`board-scan`** or **`board-scan run`** — TODO: the workflow this tool automates (not implemented yet — edit `cmd_run()` in the script).
- **`board-scan install`** — create both symlinks (bin + Claude command). Idempotent.
- **`board-scan uninstall`** — remove both symlinks. Idempotent.

After it returns, surface the `[ok]` / `[error]` / `[notice]` log lines to the user. Do NOT improvise steps the tool does not perform — the tool owns its workflow.

Pass through `$ARGUMENTS` verbatim. Valid args: `run`, `install`, `uninstall`, or empty (defaults to `run`).
