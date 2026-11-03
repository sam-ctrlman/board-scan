---
name: board-scan
description: "List open topics + open decisions from plans, memory and docs that are not on BOARD.md (read-only)"
argument-hint: "[--new] [--all] [run|install|uninstall]"
disable-model-invocation: true
---

Run `board-scan $ARGUMENTS` from the user's current directory using the Bash tool.

`board-scan` is a Python tool at `~/tools/projects/board-scan/bin/board-scan.py` (symlinked to `~/.local/bin/board-scan`). This skill is at `~/tools/projects/board-scan/skills/board-scan/SKILL.md` (its folder is symlinked to `~/.claude/skills/board-scan`).

Actions:

- **`board-scan`** — open items from recent sources, grouped DECISIONS / TOPICS, as `file:line  text`.
- **`board-scan --new`** — only items whose `<file>:<line>` is not cited on `<workspace>/docs/BOARD.md` (`$BOARD_SCAN_WORKSPACE`, default `~/workspace`).
- **`board-scan --all`** — also plans older than release A and DONE plans.
- **`board-scan install`** — create both symlinks (bin + Claude skill). Idempotent.
- **`board-scan uninstall`** — remove both symlinks. Idempotent.

After it returns, surface the `[ok]` / `[error]` / `[notice]` log lines to the user. Do NOT improvise steps the tool does not perform — the tool owns its workflow.

Pass through `$ARGUMENTS` verbatim. Valid args: `--new`, `--all`, `run`, `install`, `uninstall`, or empty (defaults to `run`). Never edit the board from the scan output without the user's choice per item (one question at a time).
