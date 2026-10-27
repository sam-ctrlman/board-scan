# board-scan

TODO: one-line description of what board-scan automates.

## Install

```sh
git clone <remote-url> ~/scripts/board-scan
python3 ~/scripts/board-scan/bin/board-scan.py install
```

After install, `board-scan` works in any shell and `/board-scan` works in Claude Code.

## Actions

| Action | What it does |
|--------|-------------|
| `board-scan` / `board-scan run` | TODO: the automated workflow |
| `board-scan install` | Create bin + Claude command symlinks |
| `board-scan uninstall` | Remove both symlinks |

## Layout

```
~/scripts/board-scan/
├── README.md
├── bin/board-scan.py
└── commands/board-scan.md
```

## Next steps after scaffolding

1. Edit `bin/board-scan.py` — replace the `cmd_run()` body with the deterministic
   steps this tool should automate. Keep each step idempotent (start with a
   `[skip]` fast-path when the work is already done).
2. Update this README and the `description:` in `commands/board-scan.md`.
3. `git add -A && git commit` the changes.
4. (Optional) add a remote and `git push -u origin main`.
