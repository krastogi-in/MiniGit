# Plan — BLRID-24 Address PR Comments

**PR branch:** `aiagent/BLRID-24`  
**Blocked until:** `sdlc:human-ready` (or comment `approved`)

## Architecture

```
CLI / Flask routes
        ↓
Operations (add_review_comment, list_review_comments, address_review_comment)
        ↓
SQLiteClient (review_comments table)
```

Comments attach to existing diff surfaces (`get_diffs`, commit detail). No new component types.

## Task table

| ID | Task | Type | Files | Size |
|----|------|------|-------|------|
| T1 | Add `review_comments` schema + CRUD | build | `src/backend/sqlite_client.py` | M |
| T2 | Operations: add / list / address | build | `src/frontend/operations.py` | M |
| T3 | CLI `comment` subcommand group | build | `src/cli.py` | M |
| T4 | Web UI: show comments on commit detail | build | `src/app.py`, `src/templates/commit_detail.html` | M |
| T5 | Web UI: POST add + address routes | build | `src/app.py` | S |
| T6 | Tests (ops + CLI + app) | build | `tests/test_review_comments.py`, `tests/test_app_comments.py` | M |
| T7 | `make check` + open PR | verify | — | S |

## Checkpoints

- **CP1 (after T2):** Manual ops test in pytest or REPL — add/list/address round-trip.
- **CP2 (after T3):** `minigit comment add|list|address` in tmp repo.
- **CP3 (after T5):** Browser smoke on commit detail with one open + one addressed comment.
- **CP4 (after T7):** `make check` green; PR on `aiagent/BLRID-24`; label `sdlc:agent-approved`.

## Risks

- Vague ticket AC — human confirms local-diff-comment scope at plan gate.
- Line drift on new commits — documented limitation; no auto-migration in MVP.

## Already covered

| Item | Action |
|------|--------|
| `get_diffs` / diff rendering | **reuse** — attach UI to existing output |
| SDLC PR-feedback skills | **out of scope** — not product code |
| GitHub PR integration | **not doing** |

All persistence, ops, CLI, and UI tasks are **build**.
