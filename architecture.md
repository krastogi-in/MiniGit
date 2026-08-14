# MiniGit Architecture

## Overview

MiniGit is an educational Git-like system in Python. It models Git concepts using
content-addressable objects and stores repository data in SQLite. The project
offers two user surfaces:

- CLI (`src/cli.py`)
- Flask web UI (`src/app.py`)

Both surfaces call the same operations layer to keep behavior consistent.

## Layered Design

### Components Layer (`src/components/`)

Core immutable domain objects:

- `Blob`: file content with SHA-256 identity
- `Tree`: directory snapshot of blobs/subtrees
- `Commit`: snapshot metadata pointing to tree and parent(s)

This layer does not depend on persistence or UI.

### Backend Layer (`src/backend/`)

Persistence implementation:

- `SQLiteClient` stores and retrieves blobs, trees, commits, refs, and staging
  records
- Input validation enforces hash and ref constraints before DB operations

This layer is storage-focused and does not depend on frontend orchestration.

### Frontend Layer (`src/frontend/`)

High-level orchestration:

- `Operations` coordinates components and backend
- Exposes workflows such as init, branch, checkout, stage, commit, diff, and merge
- Contains tree flatten/build helpers and merge logic used by both CLI and Flask

### Interface Layer

- `src/cli.py`: command parser and terminal output
- `src/app.py`: Flask routes, templates, and form handling

Both are thin adapters over `Operations`.

## Dependency Rules

Project boundary rules:

- `components/` must not import `backend/` or `frontend/`
- `backend/` must not import `frontend/` or `components/`
- `frontend/` may import `components/` and `backend/`
- `cli.py` and `app.py` may import `frontend/` only

## Data Model

MiniGit stores content by hash:

- **Blob**: raw file content
- **Tree**: serialized entries `{name, type, hash}`
- **Commit**: points to root tree and parent hashes
- **Refs**: branch name -> commit hash mappings (plus `HEAD`)
- **Staging**: pending add/delete operations for next commit

Commits are full snapshots; diffs are computed on demand by comparing trees.

## Runtime Flow

Typical write flow:

1. User action enters CLI/Flask route.
2. Interface calls `Operations`.
3. `Operations` reads current refs/commit state from `SQLiteClient`.
4. `Operations` computes updated tree/commit state.
5. `SQLiteClient` persists objects and ref updates.
6. Interface returns success/error to user.

Typical read flow:

1. Interface requests history/tree/blob/diff.
2. `Operations` fetches commit/tree/blob data via backend.
3. `Operations` computes presentation data (for example diff payloads).
4. Interface renders response.

## Merge Behavior

Merge is implemented in `Operations` with three outcomes:

- already up to date
- fast-forward (target ref moves to source tip)
- diverged merge commit with two parents

Conflict handling is conservative: conflicting paths abort the merge and keep the
target branch tip unchanged.

## Testing and Quality

Primary quality commands:

- `make lint`
- `make typecheck`
- `make test`
- `make check`

Tests live under `tests/` and validate component behavior, persistence, operations,
and interface-level wiring.

## Notes for Contributors

- Keep changes aligned with layer boundaries.
- Prefer implementing behavior once in `Operations` and reusing from both interfaces.
- Validate hashes/refs and keep SQL parameterized.
