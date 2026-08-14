# Spec — BLRID-24 Address PR Comments

**Status:** Draft for human review (plan gate)  
**Ticket:** BLRID-24 — Add a feature to address PR comments

## Assumptions

1. Scope is **local review comments on commit diffs** inside MiniGit (not GitHub PR API).
2. Comments are scoped to a **commit pair** `(base_hash, head_hash)` plus `file_path` and `line_number` (1-based, in head file).
3. `base_hash` may be empty string or sentinel for “no parent” on initial commit — use parent from commit metadata when listing on commit detail page.
4. Reviewer identity is a plain string (`author` column); default from `USER` env or `"reviewer"`.
5. “Address” sets `status = 'addressed'` and `addressed_at` timestamp; comment row retained for audit.
6. No new `components/` types — persistence via `backend/` only; orchestration in `frontend/operations.py`.
7. SDLC skills layer (`skills/`, `evals/feedback/`) is **not** in scope for this ticket.

## Objective

Enable users to simulate addressing pull-request review feedback by adding, listing, and resolving line-anchored comments on diffs between two commits—via CLI and web UI—with SQLite persistence.

## Commands & surfaces

| Surface | Command / route | Behavior |
|---------|-----------------|----------|
| CLI | `minigit comment add <base> <head> <path> <line> <body>` | Create open comment; print new comment id |
| CLI | `minigit comment list <base> <head> [--status open\|addressed\|all]` | List comments for commit pair |
| CLI | `minigit comment address <comment_id>` | Mark comment addressed; error if unknown or already addressed |
| Web UI | `GET /repo/<name>/commit/<hash>` | Show open comments overlaid on diff lines |
| Web UI | `POST /repo/<name>/commit/<hash>/comments` | Add comment (form: path, line, body, base_hash) |
| Web UI | `POST /repo/<name>/comments/<id>/address` | Mark addressed; redirect back to commit |

## Structure

```
src/backend/sqlite_client.py     # review_comments table + CRUD
src/frontend/operations.py       # add/list/address review comment methods
src/cli.py                       # comment subcommand group
src/app.py                       # routes + forms for comment add/address
src/templates/commit_detail.html # display comments; add/address controls
tests/test_review_comments.py    # backend + operations + CLI coverage
tests/test_app_comments.py       # optional Flask route tests (if pattern exists)
```

Dependency rules per `AGENTS.md`: `backend/` has no frontend imports; CLI/app stay thin.

## Data model

**Table `review_comments`**

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK AUTOINCREMENT | Comment id |
| base_hash | TEXT | 64-char hex or empty for root diff |
| head_hash | TEXT NOT NULL | 64-char hex |
| file_path | TEXT NOT NULL | Repo-relative path |
| line_number | INTEGER NOT NULL | ≥ 1 |
| author | TEXT NOT NULL | Reviewer name |
| body | TEXT NOT NULL | Comment text, max 10k chars |
| status | TEXT NOT NULL | `open` \| `addressed` |
| created_at | TEXT NOT NULL | ISO timestamp |
| addressed_at | TEXT NULL | Set when addressed |

Indexes: `(base_hash, head_hash, status)`, `(head_hash, file_path)`.

Validation: all hashes via existing `_validate_hash`; paths via safe string validation; parameterized SQL only.

## Style

- Type annotations on all new public functions.
- Functions ≤ 50 lines; files ≤ 300 lines (split helpers if needed).
- Conventional commits: `feat:` prefix.
- Match existing CLI argparse and Flask route patterns.

## Testing

- Unit: create comment, list filtered by status, address idempotency errors.
- Integration: comment survives repo re-open; invalid hash/path rejected.
- CLI: subprocess or handler tests for add/list/address happy path.
- Web: POST add + address returns redirect and updates DB.
- Gate: `make check`.

## Boundaries

| In | Out |
|----|-----|
| Line-anchored comments on diffs | GitHub/GitLab API |
| Open / addressed status | Threaded replies |
| CLI + commit-detail web UI | Comments on working tree (uncommitted) |
| SQLite persistence | Email/notification |
| List by commit pair | Full-text search across repos |

## Success criteria

1. User can `minigit comment add` on a diff line and `minigit comment list` shows it as `open`.
2. User can `minigit comment address <id>` and list shows `addressed`.
3. Commit detail page displays open comments and allows add + address.
4. Invalid inputs (bad hash, line 0, empty body) fail with clear errors.
5. `make check` passes; PR on `aiagent/BLRID-24`.

## Open questions

- Anchor line on **head** side only? **Decision:** Yes — aligns with “address feedback on the proposed change.”
- Show addressed comments in UI? **Decision:** Yes, visually distinct (muted) but default list filter is `open` on CLI.
- Cross-repo comments? **Decision:** No — comments live in repo’s `.minigit/minigit.db`.

## Duplicate / coverage notes

- No duplicate BLRID tickets for PR comments.
- Reuse existing `get_diffs` and commit detail template; **build** new persistence + comment workflow.
