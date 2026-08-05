# ADR-003: Full-Snapshot Commits (No Delta Storage)

## Status

Accepted

## Date

2024-01-20

## Context

Real Git uses a complex delta compression scheme (pack files) to avoid storing
redundant data across commits. We need to decide whether MiniGit should implement
delta storage or use full snapshots.

Options considered:
1. **Full snapshots** — each commit stores complete tree; unchanged blobs are shared
2. **Delta compression** — store diffs between versions (like Git pack files)
3. **Copy-on-write with refcounting** — more complex GC model

## Decision

Use full-snapshot commits where each commit points to a complete root tree.
Content deduplication happens naturally through content-addressable storage:
if a file hasn't changed, its blob hash is identical and the blob is stored
only once.

## Consequences

### Positive
- Dramatically simpler implementation (no delta encoding/decoding)
- Each commit is self-contained — easy to understand and debug
- Natural deduplication via content-addressing reduces actual storage
- Diffs are computed on-the-fly by comparing two tree snapshots
- No garbage collection needed (no orphaned deltas)

### Negative
- Tree objects are duplicated even when most entries unchanged
- Storage overhead for tree metadata (acceptable at educational scale)
- Diff computation is O(n) in number of files per commit
- No `git gc` equivalent — database grows monotonically
