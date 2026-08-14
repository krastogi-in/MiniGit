# Todo — BLRID-24 Address PR Comments

## T1 — SQLite review_comments table

- [ ] **Acceptance:** Table created on init; `insert_review_comment`, `list_review_comments`, `get_review_comment`, `address_review_comment`; validated hashes/paths; parameterized queries.
- **Verify:** `pytest tests/test_review_comments.py -k sqlite -v`
- **Files:** `src/backend/sqlite_client.py`
- **Size:** M

## T2 — Operations layer

- [ ] **Acceptance:** `add_review_comment`, `list_review_comments`, `address_review_comment` delegate to DB; default author from env; raise on invalid input.
- **Verify:** `pytest tests/test_review_comments.py -k operations -v`
- **Files:** `src/frontend/operations.py`
- **Size:** M

## T3 — CLI comment commands

- [ ] **Acceptance:** `minigit comment add|list|address` registered; help text; prints human-readable output; exit codes on error.
- **Verify:** `pytest tests/test_review_comments.py -k cli -v`
- **Files:** `src/cli.py`
- **Size:** M

## T4 — Commit detail UI (display)

- [ ] **Acceptance:** Open comments shown per file/line on commit detail; addressed comments muted; empty state when none.
- **Verify:** Manual browser check; optional Flask test.
- **Files:** `src/app.py`, `src/templates/commit_detail.html`
- **Size:** M

## T5 — Web POST routes

- [ ] **Acceptance:** Add comment form on commit page; address button per comment; CSRF-safe POST pattern matching existing forms; redirect after success.
- **Verify:** `pytest tests/test_app_comments.py -v`
- **Files:** `src/app.py`
- **Size:** S

## T6 — Test suite

- [ ] **Acceptance:** Coverage for happy path, invalid hash, address unknown id, list status filter.
- **Verify:** `pytest tests/test_review_comments.py tests/test_app_comments.py -v`
- **Files:** `tests/test_review_comments.py`, `tests/test_app_comments.py`
- **Size:** M

## T7 — Gate + PR

- [ ] **Acceptance:** `make check` passes; PR on `aiagent/BLRID-24`; Jira label `sdlc:agent-approved`.
- **Verify:** `make check`
- **Files:** —
- **Size:** S
