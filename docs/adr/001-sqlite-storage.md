# ADR-001: Use SQLite for Object Storage

## Status

Accepted

## Date

2024-01-15

## Context

MiniGit needs a persistent storage layer for blobs, trees, commits, and refs.
Real Git uses flat files in `.git/objects/` with a pack-file format. We need to
choose a storage strategy appropriate for an educational project.

Options considered:
1. **Flat files** (like real Git) — closer to reality but complex to implement
2. **SQLite** — single-file database, zero configuration, ACID transactions
3. **JSON files** — simple but no concurrency safety, poor for large data

## Decision

Use SQLite (via Python's built-in `sqlite3` module) stored at
`.minigit/minigit.db` per repository.

## Consequences

### Positive
- Zero external dependencies (sqlite3 is in Python stdlib)
- ACID transactions prevent corruption from interrupted writes
- Single file per repo — easy to copy, backup, inspect
- SQL queries make debugging and inspection straightforward
- Schema enforces structure on stored objects

### Negative
- Diverges from Git's actual implementation (educational trade-off)
- Binary data stored as TEXT (base64 would be needed for true binary)
- Concurrent write access limited (acceptable for single-user tool)
- Database file is opaque vs. human-readable flat files
