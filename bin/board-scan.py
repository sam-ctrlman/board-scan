#!/usr/bin/env python3
"""board-scan — list open topics and open decisions that live outside BOARD.md.

Read-only. Scans plans, workspace memory, workspace docs and each repo's docs/
and .claude/ notes for open-item markers, and prints them as `file:line  text`,
grouped into DECISIONS and TOPICS.

Markers found:
  DECIDE: <text>          open decision (preferred form for new items)
  OPEN: <text>            open topic    (preferred form for new items)
  `OPEN` / OPEN 2026-…    older ledger forms
  "decision pending", unchecked "- [ ]" boxes
  list/table lines under a heading named Open decisions / Open questions /
  Open items / Open / Backlog / Later

Usage:
  board-scan               # open items, recent sources only
  board-scan --new         # only items whose file:line is not cited on BOARD.md
  board-scan --all         # also old plans (before release A) and DONE plans
  board-scan install       # symlink into ~/.local/bin + ~/.claude/commands
  board-scan uninstall     # remove those symlinks
  board-scan --help

An item counts as "on the board" when BOARD.md cites its source as
`<file name>:<line>` anywhere (an open row, a done row or the Dropped table).

Scaffolded by `forge`. The tool name is derived from the repo directory, so
nothing here is hardcoded — rename the repo and it follows.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess  # noqa: F401  (kept for convenience when adding workflow steps)
import sys
from datetime import datetime
from pathlib import Path


def log(tag: str, msg: str) -> None:
    print(f"[{tag}] {msg}", flush=True)


def die(msg: str, code: int = 1):
    log("error", msg)
    sys.exit(code)


TOOL_NAME = Path(__file__).resolve().parent.parent.name
SYMLINK_TARGET = Path.home() / ".local" / "bin" / TOOL_NAME
CLAUDE_COMMAND_TARGET = Path.home() / ".claude" / "commands" / f"{TOOL_NAME}.md"


def _command_source() -> Path:
    return Path(__file__).resolve().parent.parent / "commands" / f"{TOOL_NAME}.md"


# ---------- the workflow ----------

HOME = Path.home()
WORKSPACE = Path(os.environ.get("BOARD_SCAN_WORKSPACE", HOME / "workspace")).expanduser()
BOARD = WORKSPACE / "docs" / "BOARD.md"
# Claude Code names a project folder after its path, "/" -> "-"
MEMORY = HOME / ".claude" / "projects" / str(WORKSPACE).replace("/", "-") / "memory"
PLANS = HOME / ".claude" / "plans"
CUTOFF = datetime(2026, 9, 29)  # release A; older plans are history unless --all

RE_DECIDE = re.compile(r"\bDECIDE:|decision pending|^\s*- \[ \]", re.I)  # matched on code-stripped text
RE_OPEN_NEW = re.compile(r"(^|[\s|*-])OPEN:")                         # matched on code-stripped text
RE_OPEN_OLD = re.compile(r"`OPEN`|`OPEN \d{4}-\d{2}-\d{2}`|\bOPEN \d{4}-\d{2}-\d{2}")
RE_CODE = re.compile(r"`[^`]*`")
RE_HEADING = re.compile(r"^(#{1,6})\s+(.*)")
RE_OPEN_HEADING = re.compile(
    r"\b(open (decisions?|questions?|items?)|backlog|later)\b|^\W*open\b", re.I)
RE_LABEL = re.compile(r"^\*{0,2}(open|open decisions?|open questions?)\*{0,2}:\s*$", re.I)
RE_ITEM = re.compile(r"^\s*([-*]|\d+\.|\|)\s*\S")
RE_CLOSED = re.compile(r"✅|~~|\bresolved\b|\bcloses OPEN\b|\bDONE\b|\bdecided\b|- \[x\]", re.I)
RE_TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def sources(include_all: bool) -> list[Path]:
    files: list[Path] = []
    files += sorted(PLANS.glob("*.md"))
    files += sorted(p for p in MEMORY.glob("*.md") if p.name != "MEMORY.md")
    files += sorted(p for p in (WORKSPACE / "docs").glob("*.md") if p != BOARD)
    for repo in sorted((WORKSPACE / "project").glob("*")):
        if repo.name == "worktree" or not repo.is_dir():
            continue
        files += sorted((repo / "docs").glob("*.md"))
        files += sorted((repo / ".claude").glob("*.md"))
    if include_all:
        return files
    kept = []
    for f in files:
        if f.parent == PLANS:
            if datetime.fromtimestamp(f.stat().st_mtime) < CUTOFF:
                continue
            first = next((l for l in f.read_text(errors="replace").splitlines() if l.startswith("#")), "")
            if re.search(r"\b(DONE|CLOSED)\b", first):
                continue
        kept.append(f)
    return kept


def scan_file(path: Path) -> list[tuple[str, int, str]]:
    """Return (kind, line_no, text) for each open item; kind = decision | topic."""
    items: list[tuple[str, int, str]] = []
    section_kind: str | None = None   # set while inside an "open" heading or label
    section_level = 0
    in_code = False
    lines = path.read_text(errors="replace").splitlines()
    start = 0
    if lines and lines[0].strip() == "---":  # skip YAML frontmatter
        start = next((i + 1 for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
    for n, raw in enumerate(lines, 1):
        if n <= start:
            continue
        line = raw.rstrip()
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        h = RE_HEADING.match(line)
        if h:
            level, title = len(h.group(1)), h.group(2)
            if section_kind and level <= section_level:
                section_kind = None
            # a level-1 title describes the whole file, so only sub-headings open a section
            if level > 1 and RE_OPEN_HEADING.search(title) and not RE_CLOSED.search(title):
                section_kind = "decision" if re.search(r"decision|question", title, re.I) else "topic"
                section_level = level
            continue
        if RE_LABEL.match(line.strip()):
            section_kind = "decision" if re.search(r"decision|question", line, re.I) else "topic"
            section_level = 7  # a label ends at the next heading of any level
            continue
        if not line.strip() or RE_TABLE_SEP.match(line):
            continue
        if RE_CLOSED.search(line):
            continue
        bare = RE_CODE.sub("", line)
        if RE_DECIDE.search(bare):
            items.append(("decision", n, line.strip()))
        elif RE_OPEN_NEW.search(bare) or RE_OPEN_OLD.search(line):
            items.append(("topic", n, line.strip()))
        elif section_kind and RE_ITEM.match(line):
            if line.lstrip().startswith("|") and re.match(r"^\s*\|\s*(#|ID|Item)\s*\|", line):
                continue  # table header row
            items.append((section_kind, n, line.strip()))
    return items


def board_refs() -> set[str]:
    if not BOARD.exists():
        return set()
    return set(re.findall(r"[\w.@+-]+\.md:\d+", BOARD.read_text(errors="replace")))


def short(path: Path) -> str:
    return "~/" + str(path.relative_to(HOME)) if path.is_relative_to(HOME) else str(path)


def cmd_run(only_new: bool = False, include_all: bool = False) -> int:
    refs = board_refs() if only_new else set()
    found = {"decision": [], "topic": []}
    files = sources(include_all)
    for f in files:
        for kind, n, text in scan_file(f):
            if only_new and f"{f.name}:{n}" in refs:
                continue
            found[kind].append((f, n, text))
    for kind, title in (("decision", "DECISIONS (open)"), ("topic", "TOPICS (open)")):
        print(f"\n== {title}: {len(found[kind])}")
        last = None
        for f, n, text in found[kind]:
            if f != last:
                print(f"\n  {short(f)}")
                last = f
            print(f"    {f.name}:{n}  {text[:160]}")
    scope = "all sources" if include_all else f"sources since {CUTOFF:%Y-%m-%d}, DONE plans hidden"
    filt = ", not on BOARD.md" if only_new else ""
    print(f"\n[ok] scanned {len(files)} files ({scope}{filt}); "
          f"{len(found['decision'])} decisions, {len(found['topic'])} topics")
    return 0


# ---------- install / uninstall ----------

def cmd_install() -> int:
    script_path = Path(__file__).resolve()
    mode = script_path.stat().st_mode
    if not (mode & 0o111):
        script_path.chmod(mode | 0o755)
        log("ok", f"made script executable: {script_path}")
    else:
        log("skip", f"script already executable: {script_path}")
    _install_bin_symlink(script_path)
    _install_claude_command()
    return _install_check_path()


def _install_bin_symlink(script_path: Path) -> None:
    SYMLINK_TARGET.parent.mkdir(parents=True, exist_ok=True)
    if SYMLINK_TARGET.is_symlink():
        current = SYMLINK_TARGET.resolve()
        if current == script_path:
            log("skip", f"bin symlink already correct: {SYMLINK_TARGET} -> {script_path}")
            return
        log("info", f"replacing existing bin symlink ({SYMLINK_TARGET} -> {current})")
        SYMLINK_TARGET.unlink()
    elif SYMLINK_TARGET.exists():
        die(f"{SYMLINK_TARGET} exists and is not a symlink — refusing to overwrite")
    SYMLINK_TARGET.symlink_to(script_path)
    log("ok", f"bin symlink created: {SYMLINK_TARGET} -> {script_path}")


def _install_claude_command() -> None:
    source = _command_source()
    if not source.exists():
        log("notice", f"slash command source not found at {source} — skipping Claude integration")
        return
    CLAUDE_COMMAND_TARGET.parent.mkdir(parents=True, exist_ok=True)
    if CLAUDE_COMMAND_TARGET.is_symlink():
        current = CLAUDE_COMMAND_TARGET.resolve()
        if current == source:
            log("skip", f"slash command symlink already correct: {CLAUDE_COMMAND_TARGET} -> {source}")
            return
        log("info", f"replacing existing slash command symlink ({CLAUDE_COMMAND_TARGET} -> {current})")
        CLAUDE_COMMAND_TARGET.unlink()
    elif CLAUDE_COMMAND_TARGET.exists():
        die(f"{CLAUDE_COMMAND_TARGET} exists and is not a symlink — refusing to overwrite")
    CLAUDE_COMMAND_TARGET.symlink_to(source)
    log("ok", f"slash command symlink created: {CLAUDE_COMMAND_TARGET} -> {source}")


def _install_check_path() -> int:
    on_path = shutil.which(TOOL_NAME)
    if on_path:
        log("ok", f"{TOOL_NAME} on PATH: {on_path}")
        return 0
    log("notice", f"{SYMLINK_TARGET.parent} is not on PATH — add this to your shell rc:")
    log("notice", f'  export PATH="{SYMLINK_TARGET.parent}:$PATH"')
    return 0


def cmd_uninstall() -> int:
    script_path = Path(__file__).resolve()
    _uninstall_bin_symlink()
    _uninstall_claude_command()
    log("info", f"to reinstall: python3 {script_path} install")
    return 0


def _uninstall_bin_symlink() -> None:
    if not SYMLINK_TARGET.is_symlink() and not SYMLINK_TARGET.exists():
        log("info", f"no bin symlink at {SYMLINK_TARGET} to remove")
        return
    if not SYMLINK_TARGET.is_symlink():
        die(f"{SYMLINK_TARGET} exists but is not a symlink — refusing to remove")
    target = SYMLINK_TARGET.resolve()
    SYMLINK_TARGET.unlink()
    log("ok", f"removed bin symlink: {SYMLINK_TARGET} (was -> {target})")


def _uninstall_claude_command() -> None:
    if not CLAUDE_COMMAND_TARGET.is_symlink() and not CLAUDE_COMMAND_TARGET.exists():
        log("info", f"no slash command symlink at {CLAUDE_COMMAND_TARGET} to remove")
        return
    if not CLAUDE_COMMAND_TARGET.is_symlink():
        die(f"{CLAUDE_COMMAND_TARGET} exists but is not a symlink — refusing to remove")
    target = CLAUDE_COMMAND_TARGET.resolve()
    CLAUDE_COMMAND_TARGET.unlink()
    log("ok", f"removed slash command symlink: {CLAUDE_COMMAND_TARGET} (was -> {target})")


# ---------- entry point ----------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="List open topics and open decisions from plans, memory and docs (read-only).",
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="run",
        choices=["run", "install", "uninstall"],
        help="run (default) = do the work; install/uninstall = manage symlinks",
    )
    parser.add_argument("--new", action="store_true",
                        help="only items whose file:line is not cited on BOARD.md")
    parser.add_argument("--all", action="store_true",
                        help="include plans older than release A and DONE plans")
    args = parser.parse_args()
    if args.action == "install":
        return cmd_install()
    if args.action == "uninstall":
        return cmd_uninstall()
    return cmd_run(only_new=args.new, include_all=args.all)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("error", "interrupted")
        sys.exit(130)
