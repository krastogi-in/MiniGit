# Plan: MiniGit clone + clone count (BLRID-22)

**PR branch (implement):** `aiagent/BLRID-22`  
**Spec:** `agent_space/BLRID-22/specs/minigit-clone-count.md`

## Architecture notes

- Add SQLite meta/stats for `clone_count` (default 0) in `SQLiteClient`.
- `Operations.clone_repo(source_path, dest_path) -> int` (returns new count) and `get_clone_count() -> int`.
- Clone = filesystem copy of a MiniGit repo into an empty dest; open source DB to increment after copy succeeds.
- CLI thin wrappers only.

## Task breakdown

| ID | Task | Build vs reuse | Size |
|----|------|----------------|------|
| T1 | Schema + `get_clone_count` / `increment_clone_count` in backend | **build** (new table/API; reuse SQLiteClient patterns) | S |
| T2 | `clone_repo` in frontend/operations (or `clone.py`) | **build** | M |
| T3 | CLI `clone` + `clone-stats` | **build** (reuse argparse style) | S |
| T4 | Tests `tests/test_clone.py` | **build** | M |
| T5 | Optional Flask display — only if T1–T4 green and time | **build** / skip if risk | S |

## Checkpoints

- After T1–T2: unit/integration can call Operations in tmp_path.
- After T3–T4: `make check` green → open PR.
- T5 only if AC already met without it (AC allows CLI-only).

## Risks (early)

- Copying open SQLite file — clone should copy DB file with connection closed or use backup API; fail closed on lock errors.
- Dest collision — validate before write.

## Out of scope reminders

No remotes, no new deps, no Description overwrite on Jira.
