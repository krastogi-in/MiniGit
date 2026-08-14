# Idea: MiniGit safe reset (BLRID-29)

## Problem Statement / How Might We

How Might We let MiniGit users move a branch tip to an earlier commit **without silently losing work**, by showing a short preview of what will be discarded?

## User

Learners and Innovation Day demos who need to undo bad commits safely—clearer than raw `reset --hard`.

## Success criteria

- Soft / mixed / hard reset move only the current branch tip.
- `--dry-run` (or equivalent preview) lists commits that leave the tip path and hard-mode path impact.
- Applying requires explicit `--yes` (or confirm); hard aborts on dirty tracked files unless `--force`.
- Tests + CLI; `make check` green.

## Duplicate check

- **None** — no BLRID ticket for reset (search empty). Related: BLRID-23 revert (new inverse commit, not tip move).

## Already covered

- **No reset** in `src/` / tests.
- Reuse: `get_commit_history`, `_flatten_tree`, `set_ref`, staging clear, hash validation.
- Gap: working-tree write on hard reset may need a small helper (checkout sync not shipped yet)—scope hard sync into this ticket or soft-fail hard if disk sync deferred; **prefer implement hard file sync** as part of value.

## Recommended direction

`Operations.reset(target, mode, *, dry_run, force)` returns preview struct; CLI prints it; apply only when not dry_run and confirmed.

## MVP

- Modes soft / mixed / hard; default mixed
- Preview: orphaned commits (tip→target walk) + hard path summary
- `--dry-run` / `--yes` / `--force`
- CLI + tests; web optional

## Not Doing

- Reflog, short-hash, interactive rebase, remote force-push
