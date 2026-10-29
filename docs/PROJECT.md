# board-scan

<!-- created by /memlayout 2026-10-30 · board prefix TOOL-BSCAN · workspace tools -->

## Goal
Lists open topics (`OPEN:`) and open decisions (`DECIDE:`) from plans, memory and docs that are not on the workspace board yet. Read-only.

## Users
A developer who runs Claude Code on their own machine and wants this step done the same way every time.

## Scope
- In: the commands in `README.md`, `board-scan install` / `uninstall` (symlinks onto PATH and into `~/.claude`).
- Out (non-goals): anything that needs a server or a network service of its own.

## Depends on / used by
Other tools in the workspace only through their CLI. See `~/tools/docs/PROJECTS.md`.
