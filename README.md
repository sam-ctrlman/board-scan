# board-scan

List **open topics and open decisions** that live outside `~/ws01/docs/BOARD.md`. Read-only.

## Why
Open items were spread over 50+ plans, review-run ledgers, memory and repo docs, so a decision could sit forgotten in an old plan. `board-scan` collects them; `--new` shows only what the board doesn't cite yet.

## Install

```sh
git clone <remote-url> ~/scripts/board-scan
python3 ~/scripts/board-scan/bin/board-scan.py install
```

After install, `board-scan` works in any shell and `/board-scan` works in Claude Code.

## Actions

| Action | What it does |
|--------|-------------|
| `board-scan` | Open items from sources changed since release A (2026-09-29); DONE plans hidden |
| `board-scan --new` | Only items whose `<file>:<line>` is not cited anywhere on BOARD.md |
| `board-scan --all` | Also old and DONE plans |
| `board-scan install` | Create bin + Claude command symlinks |
| `board-scan uninstall` | Remove both symlinks |

## What it reads
`~/.claude/plans/*.md`, workspace memory `*.md` (not MEMORY.md), `~/ws01/docs/*.md` (not BOARD.md), and each repo's `docs/*.md` and `.claude/*.md` under `~/ws01/project/`.

## What counts as open
| Kind | Marker |
|---|---|
| decision | `DECIDE: …` (new form), "decision pending", an unchecked `- [ ]` box, list/table lines under a sub-heading named *Open decisions* / *Open questions* |
| topic | `OPEN: …` (new form), `` `OPEN` `` / `OPEN 2026-…` (ledger form), list/table lines under *Open items* / *Open* / *Backlog* / *Later* sub-headings or an `Open:` label |

Skipped: lines with ✅, `~~`, resolved, DONE, decided, `- [x]`; code blocks; YAML frontmatter; table headers. A level-1 title never opens a section.

## Taking an item off the list
Cite its source on BOARD.md as `<file name>:<line>`: in an open row, a done row, or the **Dropped** table.
Line numbers move when a file is edited, so re-run `--new` after editing a source.

## Layout

```
~/scripts/board-scan/
├── README.md
├── bin/board-scan.py
└── commands/board-scan.md
```
