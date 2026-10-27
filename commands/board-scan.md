---
description: "List open topics + open decisions from plans, memory and docs that are not on BOARD.md (read-only)"
argument-hint: "[--new] [--all] [run|install|uninstall]"
---

Run `board-scan $ARGUMENTS` from the user's current directory using the Bash tool.

`board-scan` is a Python tool at `~/scripts/board-scan/bin/board-scan.py` (symlinked to `~/.local/bin/board-scan`). This slash command file is at `~/scripts/board-scan/commands/board-scan.md` (symlinked to `~/.claude/commands/board-scan.md`).

Actions:

- **`board-scan`** — open items from recent sources, grouped DECISIONS / TOPICS, as `file:line  text`.
- **`board-scan --new`** — only items whose `<file>:<line>` is not cited on `~/ws01/docs/BOARD.md`.
- **`board-scan --all`** — also plans older than release A and DONE plans.
- **`board-scan install`** — create both symlinks (bin + Claude command). Idempotent.
- **`board-scan uninstall`** — remove both symlinks. Idempotent.

After it returns, surface the `[ok]` / `[error]` / `[notice]` log lines to the user. Do NOT improvise steps the tool does not perform — the tool owns its workflow.

Pass through `$ARGUMENTS` verbatim. Valid args: `--new`, `--all`, `run`, `install`, `uninstall`, or empty (defaults to `run`). Never edit the board from the scan output without the user's choice per item (one question at a time).
