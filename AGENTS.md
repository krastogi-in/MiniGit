# Agent Instructions for MiniGit

## Project Overview

MiniGit is an educational Git clone in Python. It implements content-addressable
storage (blobs, trees, commits) backed by SQLite, exposed via a CLI and Flask web UI.

## Architecture

```
src/components/   -> Core immutable data objects (Blob, Tree, Commit)
src/backend/      -> Persistence layer (SQLite only)
src/frontend/     -> High-level operations orchestrating components + backend
src/cli.py        -> CLI entry point (thin layer over operations)
src/app.py        -> Flask web UI (thin layer over operations)
tests/            -> pytest test suite
```

## Dependency Rules

- `components/` must NOT import from `backend/` or `frontend/`
- `backend/` must NOT import from `frontend/` or `components/`
- `frontend/` may import from `components/` and `backend/`
- `cli.py` and `app.py` may import from `frontend/` only

## Development Commands

```bash
make setup          # Install dependencies
make lint           # Run ruff linter
make typecheck      # Run mypy
make test           # Run pytest with coverage
make check          # Run all checks (lint + typecheck + test)
make fmt            # Auto-format code
```

## Conventions

- All hashes are 64-character lowercase hex strings (SHA-256)
- Ref names match `^[A-Za-z0-9_.\-/]+$`
- Commits are full snapshots; diffs are computed at read time
- Use type annotations on all public functions
- Follow conventional commit messages: `feat:`, `fix:`, `docs:`, `test:`, `chore:`
- Keep functions under 50 lines; files under 300 lines

## Testing

- All new features require tests in `tests/`
- Use the `tmp_path` fixture for isolated repos
- Tests should not depend on network or filesystem outside tmp dirs

## Security

- Never execute user input as code
- Validate all hash inputs against `^[0-9a-f]{64}$`
- Validate ref names against `^[A-Za-z0-9_.\-/]+$`
- SQLite queries must use parameterized statements (never f-strings)
