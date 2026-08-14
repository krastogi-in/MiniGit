# Idea: MiniGit status (BLRID-11)

## How Might We

HMW let a MiniGit user see **which branch is current** and **what is staged** in one place (CLI + web), without inventing full Git porcelain?

## User + success

- **User:** Developer or learner using MiniGit CLI or Flask UI.
- **Success:** `minigit status` (and a Flask status view) shows current branch name and staged files (or “nothing staged”); invalid/missing repo fails clearly; tests cover the AC in the ticket.

## Direction

Add a thin `Operations.status()` (or equivalent) that returns `{branch, staged[]}`, wired to:

1. CLI: `minigit status`
2. Flask: status section/page using the same operation

Persist / read **HEAD** so current branch is correct across process invocations (today `Operations.branch` defaults to `"main"` in memory and `checkout_branch` does not update the HEAD ref).

## MVP

- Resolve current branch from persisted HEAD (fix/update HEAD on checkout as needed)
- List staged entries via existing `get_staged()` (path + short hash OK)
- Empty staging → clear “nothing staged” message
- Bad/missing repo → clear error; CLI non-zero exit
- Flask shows the same info
- Tests: branch display, empty staged, staged with files, bad repo

## Not Doing

- Untracked / modified / deleted porcelain (full Git status)
- New third-party dependencies
- Deploy beyond `make check`

## Assumptions

- Ticket Description is the sole scope source.
- Staged data already exists in SQLite staging table; no schema change required for staging.
- HEAD ref may need to be written on checkout and read on Operations init for AC “current branch” to be meaningful across CLI runs.
- Short blob hash display (e.g. 8–12 chars) is acceptable.

## Duplicate-ticket check

- **None found** for a dedicated `status` command.
- JQL `summary/description ~ status` hit BLRID-5 (CI pipeline) and BLRID-6 (branch vs base **diff** view) — different features; not duplicates.
- BLRID-9 (cherry-pick), BLRID-10 (stash) are unrelated.

## Already covered / partial

| Area | Coverage |
|------|----------|
| `Operations.get_staged()` / DB staging | **Partial** — reuse |
| Branch list / checkout / `self.branch` | **Partial** — in-memory only; HEAD not updated on checkout |
| CLI `status` | **Missing** |
| Dedicated Flask status view | **Missing** (working-dir page shows staged for staging UX, not a status summary) |
| Tests for `status` | **Missing** |

Prefer **build** CLI + Flask + thin status API; **reuse** `get_staged`; **verify/fix** HEAD persistence so branch is correct.
