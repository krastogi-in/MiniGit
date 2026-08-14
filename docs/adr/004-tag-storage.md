# ADR-004: Dedicated `tags` Table for Tag Storage

## Status

Accepted

## Date

2026-08-14

## Context

MiniGit needs a way to mark a specific commit with a permanent, human-readable
name (a tag) — distinct from a branch, which moves as new commits are added.
We need to decide where and how to store this new pointer type.

Options considered:
1. **Dedicated `tags` table** — new table, independent of the existing `refs`
   table (which holds branches + `HEAD`)
2. **Reuse `refs` with a namespace prefix** (e.g. `tags/v1.0`) — same table as
   branches, disambiguated by name convention
3. **New hashed tag object** — a content-addressable `Tag` object (like
   `Commit`/`Tree`/`Blob`) that other objects could reference by hash
4. **Lightweight tags only** — a bare `name -> commit_hash` pointer with no
   metadata (closer to a Git lightweight tag)

## Decision

Use a dedicated `tags` table, separate from `refs`:

```sql
CREATE TABLE tags (
    name TEXT PRIMARY KEY,
    commit_hash TEXT NOT NULL,
    tagger TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
```

Tags are **annotated only** — every tag carries tagger/message/timestamp
metadata, mirroring the metadata style `Commit` already uses. There is no
separate lightweight-tag code path in v1.

Tags are **not** a new content-addressable object type: nothing else in
MiniGit needs to reference a tag by hash, so a tag is a named pointer row,
not a hashed object.

## Consequences

### Positive
- Zero risk to existing branch/`refs` logic — `get_all_branches()`, `HEAD`
  handling, and ref-name validation are completely untouched
- Additive-only schema change — no migration of `commits` or `refs`
- Consistent with MiniGit's existing metadata-rich object style (mirrors
  `Commit`'s author/message/timestamp), rather than a bare pointer
- Simple to test in isolation — a tag is fully independent of commit/tree/blob
  hashing (ADR-002) and full-snapshot commit semantics (ADR-003)

### Negative
- A second "named pointer" table exists alongside `refs` instead of one
  unified ref table — acceptable given tags and branches have genuinely
  different mutability semantics (immutable vs. moving) that a single table
  would otherwise need a discriminator column to express
- Only annotated tags are supported; a future lightweight-tag mode would need
  a nullable metadata path if ever requested
