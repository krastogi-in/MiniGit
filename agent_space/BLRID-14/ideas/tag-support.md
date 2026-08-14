# Idea: Tag Support for MiniGit

**Issue:** [BLRID-14](https://redhat.atlassian.net/browse/BLRID-14)

## How Might We

How might we let a MiniGit user mark a specific commit with a permanent, human-readable
name that never moves — the way a release or milestone is remembered — when today only
mutable branches exist?

## Who is this for

A MiniGit user who wants to bookmark a meaningful point in history (e.g. "v1.0",
"before-refactor") and return to it later by name, without that name silently drifting
as new commits land (as a branch would).

## Success criteria

- A tag can be created against any existing commit (defaults to current branch tip)
- A tag never moves once created — distinguishes it from a branch
- Tags are listable, deletable, and resolvable anywhere a commit hash or branch name
  is currently accepted (`show`, `diff`, history views)
- Both CLI and Flask web UI expose the same capability

## Duplicate check

Searched BLRID for related/duplicate tickets:

| Ticket | Summary | Overlap |
|--------|---------|---------|
| BLRID-15 | "Add tag support to MiniGit" | **Same request**, untouched (status New, no labels). This ticket (BLRID-14) proceeds as the vehicle; BLRID-15 should be closed/linked as duplicate by the human once this ships. |
| BLRID-16 | Interactive commit graph view | Related area (history visualization) but distinct feature; not a duplicate |
| BLRID-17 | Per-file commit history (`log --file`) | Distinct feature; not a duplicate |
| BLRID-18 | `git status` | Distinct; duplicates BLRID-11 instead (already in flight) |

No duplicate of *this exact* scope exists other than BLRID-15, which is unclaimed and can
be superseded by this ticket's delivery.

## Already covered (repo scan)

- `src/backend/sqlite_client.py`: only `blobs`, `trees`, `commits`, `refs`, `staging` tables. No `tags` table.
- `src/frontend/operations.py`: no tag-related methods.
- `src/cli.py`: no `tag` subcommand.
- `src/app.py`: no tag routes.
- **Nothing in the codebase satisfies any part of this ticket.** Full build required.

## Recommended direction

Add a dedicated `tags` table (parallel to how `commits` carries its own metadata) rather
than overloading the existing `refs` table used for branches/HEAD:

- Keeps `get_all_branches()` and branch-ref logic completely untouched (no risk of tags
  leaking into branch listings or vice versa)
- Mirrors the existing object-model pattern (`Commit` already carries author/message/timestamp)
  by giving tags their own tagger/message/timestamp — consistent house style over a bare pointer
- Additive-only schema change; no migration of existing tables

## Assumptions

- Lightweight vs. annotated: going **annotated-only** (tagger + message + timestamp) for
  consistency with MiniGit's existing metadata-rich objects (Commit) — simpler than
  supporting two tag kinds side-by-side, and more educational (mirrors how commits work)
- Tags share the same name pattern as refs (`^[A-Za-z0-9_.\-/]+$`) and must not collide
  with existing branch names (avoids ambiguity in commands that accept "a name")
- No new hashed content-addressable object type is required — a tag is a named pointer
  with metadata, not something else needs to reference it by hash

## MVP scope

1. Create tag (CLI `minigit tag <name> [<commit_hash>]`, Flask form)
2. List tags (CLI `minigit tag`, Flask list)
3. Delete tag (CLI `minigit tag -d <name>`, Flask action)
4. Resolve tag name in existing read paths (`show`, `diff`) alongside commit hash / branch name
5. Validation: name pattern, branch-name collision, duplicate tag rejection

## Not doing (and why)

- **Signed/GPG tags** — no cryptographic identity model in MiniGit; out of scope for an
  educational clone
- **Push/fetch of tags** — MiniGit has no remote concept at all
- **Retagging (moving a tag)** — tags are immutable by definition; delete + recreate covers
  the rare need to fix a mistake, without introducing "moving pointer" semantics that would
  blur the branch/tag distinction
