# Idea: MiniGit clone + clone count (BLRID-22)

## How Might We

How might we let a MiniGit user **copy an existing local repo** and **see how many times clone has succeeded**, without inventing remotes or Git-compatible network clone?

## User

Developer / workshop participant using MiniGit CLI (and optionally Flask UI) who already has a `.minigit` repo and wants a second working copy plus a visible clone counter.

## Success criteria

- User can run `minigit clone <source> [dest]` and get a usable MiniGit repo at dest.
- Each successful clone increments a persisted counter.
- User can read the counter (CLI at minimum; UI optional in MVP).
- Missing/invalid source fails clearly with no partial dest + no counter bump.
- Tests + `make check` pass per `AGENTS.md`.

## Recommended direction

**Local filesystem clone** of the MiniGit store (copy `.minigit` / SQLite DB and enough working tree if present), plus a small **repo-level meta counter** (SQLite `meta`/`stats` table or key-value) incremented only after a successful clone. Expose via `Operations` → CLI (`clone`, `clone-stats` or print-after-clone). Mirror merge’s thin-vertical-slice pattern: frontend ops + backend persistence + CLI; Flask only if cheap in the same slice.

## Assumptions

- Clone is **local path → local path** only (ticket non-goals: no network remotes).
- Counter lives in the **source** repo’s store (how many times *this* repo was cloned from), unless plan discovers a cleaner “global” option — default: source repo.
- Dest must not already be a MiniGit repo (or must be empty) — fail closed.
- No new third-party dependencies.

## MVP

1. `Operations.clone_repo(source, dest)` + SQLite counter increment/read.
2. CLI: `clone` + show count (`clone-stats` and/or post-clone line).
3. Tests: success, missing source, counter increments, invalid dest.

## Not doing

- Network / remote clone, shallow clone, sparse checkout.
- Conflict/merge semantics during clone.
- Auto-deploy beyond `make check`.
- Full Git-compatible clone UX parity.

## Duplicate-ticket check

JQL on BLRID for clone / clone count → **none found** besides **BLRID-22**.

## Already covered

`src/` has **no** clone or clone-counter APIs (grep empty). Init/branch/checkout/log/diff/(merge on other branch) exist; clone is **build**, not reuse.
