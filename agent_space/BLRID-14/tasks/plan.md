# Plan: Tag Support for MiniGit

**Issue:** [BLRID-14](https://redhat.atlassian.net/browse/BLRID-14) · **Spec:** [tag-support.md](../specs/tag-support.md)

## Overview

Add annotated tags (immutable named pointers to commits) to MiniGit: backend storage,
operations-layer logic, CLI subcommand, and Flask web UI, following the layering in
[AGENTS.md](../../../AGENTS.md). Six tasks, two checkpoints, PR branch `aiagent/BLRID-14`.

## Architecture

```
tags table (new, additive)          Operations                Surfaces
┌─────────────────────┐      ┌─────────────────────┐   ┌──────────────────┐
│ name (PK)            │──────▶ create_tag()         │──▶│ CLI: tag         │
│ commit_hash          │      │ delete_tag()         │   │ (create/list/del)│
│ tagger, message,     │      │ get_all_tags()        │   ├──────────────────┤
│ timestamp            │      │ resolve_ref()  (new,  │──▶│ Flask: /tags     │
└─────────────────────┘      │   extends existing    │   │ (list/create/del)│
                              │   hash/branch lookup) │   └──────────────────┘
                              └─────────────────────┘
```

No changes to `commits` or `refs` tables. No new `components/` object — tags are
metadata rows, not hashed content-addressable objects.

## Already covered vs build

Nothing in this scope is already covered (confirmed in ideate + spec repo scans) — all
six tasks are **build**, not reuse/verify.

## Task list

| # | Task | Size | Files |
|---|------|------|-------|
| 1 | `tags` table + SQLiteClient CRUD | M | `src/backend/sqlite_client.py`, `tests/test_sqlite_client.py` |
| 2 | `Operations.create_tag` / `delete_tag` / `get_all_tags` | M | `src/frontend/operations.py`, `tests/test_tags.py` |
| 3 | `resolve_ref()` helper — tag name resolves alongside commit hash / branch name in `show`/`diff` paths | S | `src/frontend/operations.py`, `tests/test_tags.py` |
| 4 | CLI `tag` subcommand (create / list / delete) | S | `src/cli.py` |
| 5 | Flask routes + template (list / create / delete) | M | `src/app.py`, `src/templates/` |
| 6 | AC close-out: full `make check`, PR | S | — (verification only) |

### Task 1 — `tags` table + SQLiteClient CRUD

- **Acceptance:** `tags` table created on init (mirrors existing `_init_tables` pattern);
  `store_tag(name, commit_hash, tagger, message, timestamp)`, `get_tag(name)`,
  `get_all_tags()`, `delete_tag(name)`; all inputs validated (reuse `_validate_ref_name`,
  `_validate_hash`, `_validate_str`); duplicate `store_tag` on existing name raises
  (no silent `INSERT OR IGNORE`/`OR REPLACE` — tags must not overwrite)
- **Verify:** `pytest tests/test_sqlite_client.py -k tag`
- **Size:** M

### Task 2 — `Operations.create_tag` / `delete_tag` / `get_all_tags`

- **Acceptance:** `create_tag(name, commit_hash=None, tagger=None, message=None)` — resolves
  `commit_hash` to current branch tip when omitted; rejects if `name` collides with an
  existing branch name or existing tag name; rejects invalid commit hash (must exist);
  `delete_tag(name)` raises if tag doesn't exist; `get_all_tags()` returns list of dicts
- **Verify:** `pytest tests/test_tags.py -k "create or delete or list"`
- **Size:** M

### Task 3 — `resolve_ref()` helper

- **Acceptance:** given a string that could be a commit hash, branch name, or tag name,
  returns the resolved commit hash (or raises if none match); wire into whichever existing
  method(s) currently accept "a hash or branch name" for `show`/diff so tags work there too
  without duplicating resolution logic
- **Verify:** `pytest tests/test_tags.py -k resolve`
- **Size:** S

### Task 4 — CLI `tag` subcommand

- **Acceptance:** `minigit tag <name> [<commit_hash>]` creates; `minigit tag` (no args)
  lists; `minigit tag -d <name>` deletes; errors printed consistently with existing CLI
  error style (see `cmd_branch`, `cmd_checkout`)
- **Verify:** manual smoke (`python src/cli.py tag ...`) — project has no existing CLI
  test harness; consistent with current test coverage gaps
- **Size:** S

### Task 5 — Flask routes + template

- **Acceptance:** list tags (repo overview or dedicated `/repo/<name>/tags` page — decide
  at implementation time per spec's open question), `POST /repo/<name>/tag` (create),
  `POST /repo/<name>/tag/<tag_name>/delete`; flash messages consistent with existing
  stage/unstage pattern in `app.py`
- **Verify:** manual smoke — project has no existing Flask test harness, consistent with
  current test coverage gaps
- **Size:** M

### Task 6 — AC close-out

- **Acceptance:** every acceptance criterion in the Jira ticket checked off; `make check`
  green; PR opened
- **Verify:** `make check`
- **Size:** S

## Checkpoints

- **Checkpoint 1** (after Task 2): Core tag semantics (storage + creation/deletion/collision
  rules) proven by tests — highest-risk logic is done before surfaces are built
- **Checkpoint 2** (after Task 5): Both surfaces (CLI + web) wired — ready for final
  AC verification pass

## PR

Branch: `aiagent/BLRID-14`. Opens after implementation + tests complete (Task 6), for
human PR-gate review per `skills/sdlc-loop/SKILL.md`.

## Risks

| Risk | Mitigation |
|------|------------|
| Tag/branch name collision ambiguity in existing commands | `resolve_ref()` centralizes lookup order (commit hash → branch → tag) with a single documented precedence |
| `sqlite_client.py` / `operations.py` approaching 300-line file limit | Extract tag logic into a focused section; split into a helper module if the limit is hit (flag in Task 1/2 if so) |
| No existing CLI/Flask test harness to extend | Explicitly scoped as manual smoke per current project convention; not blocking `make check` |
