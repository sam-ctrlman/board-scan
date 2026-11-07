# board-scan

**Read-only CLI tool and Claude Code skill to scan Markdown plans, project docs, and AI agent memory for untracked open decisions (`DECIDE:`) and tasks (`OPEN:`).**

When managing complex software projects with **Claude Code** or Markdown-based documentation, architecture decisions, follow-up tasks, and unchecked action items quickly scatter across dozens of implementation plans (`~/.claude/plans/*.md`), session ledgers, AI memory notes, and repository `docs/` folders. `board-scan` parses all of these Markdown sources in a single pass, extracts every unresolved decision and open topic, and filters out items already tracked on your central `BOARD.md`.

---

## Why Use `board-scan`?

- **100% Read-Only & Safe:** Scans Markdown files and prints structured `file:line` references without modifying your plans, docs, or task board.
- **Zero-Config Delta Mode (`--new`):** Automatically cross-references `<file>:<line>` citations against `<workspace>/docs/BOARD.md` so you only see untracked items.
- **Multi-Source Discovery:** Scans `~/.claude/plans/*.md`, Claude Code project memory (`~/.claude/projects/*/memory/*.md`), workspace `docs/*.md`, and per-repository `docs/*.md` + `.claude/*.md` files.
- **Smart Markdown Parser:** Understands explicit inline markers (`DECIDE:`, `OPEN:`), unchecked task checkboxes (`- [ ]`), and bullet/table items nested under open-item headings while ignoring fenced code blocks, YAML frontmatter, and completed items (`✅`, `~~`, `DONE`, `resolved`, `- [x]`).
- **Dual Interface:** Run `board-scan` from any terminal shell, or invoke `/board-scan` directly inside Claude Code.
- **Zero External Dependencies:** Pure Python 3 standard library.

---

## Example Output

```text
$ board-scan --new

== DECISIONS (open): 2

  ~/.claude/plans/auth-session-redesign.md
    auth-session-redesign.md:42  - DECIDE: session token rotation window — options: 15m vs 1h — recommend: 15m

  ~/workspace/project/api-server/docs/ARCHITECTURE.md
    ARCHITECTURE.md:118  - [ ] Confirm rate-limit storage backend before v2 cutover

== TOPICS (open): 1

  ~/workspace/docs/ROADMAP.md
    ROADMAP.md:64  - OPEN: add end-to-end webhook retry metrics

[ok] scanned 38 files (sources since 2026-09-29, DONE plans hidden, not on BOARD.md); 2 decisions, 1 topics
```

---

## Installation

Clone the repository and run the built-in installer to symlink both the CLI binary (`~/.local/bin/board-scan`) and the Claude Code skill (`~/.claude/skills/board-scan`):

```sh
git clone <remote-url> ~/tools/projects/board-scan
python3 ~/tools/projects/board-scan/bin/board-scan.py install
```

Once installed:
1. Run `board-scan` from **any terminal shell**.
2. Run `/board-scan` directly **inside Claude Code**.

To remove the symlinks at any time:
```sh
board-scan uninstall
```

---

## Core Commands & Flags

| Command / Flag | Description |
| :--- | :--- |
| `board-scan` or `board-scan run` | Scan recent Markdown sources for open decisions and topics (plans marked `DONE` or `CLOSED` in their title are skipped). |
| `board-scan --new` | Show **only** open items whose `<file>:<line>` reference is not yet cited anywhere in `<workspace>/docs/BOARD.md`. |
| `board-scan --all` | Include older historical plans and plans marked `DONE` or `CLOSED`. |
| `board-scan install` | Create the `~/.local/bin/board-scan` binary symlink and `~/.claude/skills/board-scan` skill symlink. |
| `board-scan uninstall` | Remove both symlinks cleanly. |
| `board-scan --help` | Print CLI usage and options. |

### Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `BOARD_SCAN_WORKSPACE` | `~/workspace` | Root workspace directory containing `docs/BOARD.md`, `docs/*.md`, and `project/<repo>/`. |

---

## What It Scans & How Markers Work

### Scanned Locations
1. **Claude Code Plans:** `~/.claude/plans/*.md`
2. **Workspace AI Memory:** `~/.claude/projects/<workspace-slug>/memory/*.md` (excluding `MEMORY.md` index)
3. **Workspace Docs:** `<workspace>/docs/*.md` (excluding `BOARD.md` itself)
4. **Project Repositories:** `<workspace>/project/<repo>/docs/*.md` and `<workspace>/project/<repo>/.claude/*.md` (skipping `worktree` directories)

### Open Marker Syntax

| Category | Recognized Markdown Patterns |
| :--- | :--- |
| **Decision (`DECISIONS`)** | • Inline `DECIDE: <question>` marker<br>• `"decision pending"` phrase<br>• Unchecked Markdown task box (`- [ ] ...`)<br>• List or table rows under a sub-heading (`##`–`######`) or label named *Open decisions* or *Open questions* |
| **Topic (`TOPICS`)** | • Inline `OPEN: <topic>` marker<br>• Ledger markers (`` `OPEN` `` or `OPEN YYYY-MM-DD`)<br>• List or table rows under a sub-heading (`##`–`######`) or label named *Open items*, *Open*, *Backlog*, or *Later* |

**Automatically Ignored:**
- Any line containing `✅`, strikethrough `~~`, `resolved`, `closes OPEN`, `DONE`, `decided`, or `- [x]`.
- Content inside fenced code blocks (`` ``` ``), YAML frontmatter (`---`), Markdown table separator rows, and table header rows (`| # |`, `| ID |`, `| Item |`).

---

## Workflow: Taking an Item Off the Scan List

To mark an open item as tracked without editing the original plan or ledger:

1. Run `board-scan --new` to find untracked items and note the printed `<file.md>:<line>` citation.
2. Add a row to `<workspace>/docs/BOARD.md` (under *Now*, *Next*, *Parked*, *Decisions open*, *Done*, or *Dropped*) and include `<file.md>:<line>` in the **Source** column.
3. Re-run `board-scan --new` — the cited item is now filtered out automatically.

> **Note:** Because line numbers shift when a source file is edited, re-run `board-scan --new` after modifying a cited plan or doc.

---

## Exit Codes & Project Layout

### Exit Codes
- `0` — Scan or symlink action completed successfully.
- `1` — Runtime or filesystem error.
- `130` — Interrupted by user (`Ctrl-C`).

### Directory Structure
```text
~/tools/projects/board-scan/
├── LICENSE
├── README.md
├── bin/board-scan.py           # CLI executable & Markdown scanner
├── docs/
│   ├── PROJECT.md
│   └── STATUS.md
└── skills/board-scan/SKILL.md  # Claude Code /board-scan skill definition
```

---

## Frequently Asked Questions (FAQ)

**How do I find forgotten TODOs and open architectural decisions across Claude Code plans?**  
Run `board-scan --new`. It scans `~/.claude/plans/*.md`, AI memory files, and repository documentation for `DECIDE:`, `OPEN:`, and unchecked `- [ ]` tasks that are not yet referenced on your workspace `BOARD.md`.

**Does `board-scan` modify my Markdown files or `BOARD.md`?**  
No. `board-scan` is strictly read-only. Even when invoked via `/board-scan` inside Claude Code, the skill is configured to report findings first and never edit `BOARD.md` without your explicit confirmation.

**How do I point `board-scan` at a different workspace directory?**  
Set the `BOARD_SCAN_WORKSPACE` environment variable (for example, `export BOARD_SCAN_WORKSPACE=~/my-workspace`) in your shell profile before running `board-scan`.
