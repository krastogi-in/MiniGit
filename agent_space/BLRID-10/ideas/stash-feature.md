# Idea: Stash uncommitted work (BLRID-10)

## How Might We
How might we let a MiniGit user temporarily set aside uncommitted changes and restore them later so they can switch context without making a throwaway commit?

## User
Developer (CLI or web UI) working in a MiniGit repo who has staged and/or modified files they are not ready to commit.

## Success criteria
- User can **save** current uncommitted changes into a stash entry.
- User can **list** stash entries.
- User can **restore** the most recent stash (pop) and continue work from that state.
- Behavior is covered by tests; CLI and Flask surfaces expose the MVP.

## Duplicate-ticket check
JQL `project = BLRID AND (summary ~ stash OR description ~ stash)` → only **BLRID-10**. **None found** besides this issue.

## Already covered / partial coverage
Repo scan (`stash` in `src/`, `tests/`, docs): **no stash implementation**.
Reusable building blocks (not a substitute for the feature):
- Staging table + `add` / `delete_file` / `get_staged` / `clear_staging`
- Blobs for content; tree flatten/rebuild for snapshots
- Branch refs / HEAD (context for “clean” after stash)
- Diff helpers between commit trees (not WD↔HEAD status)

**Coverage: none for stash; build required.** Partial reuse of staging + blob storage.

## Recommended direction
Add a **LIFO stash stack** stored in SQLite (new table), MVP aligned with real Git’s educational subset:

1. **`stash` / `stash push`** — capture staged entries (and working-directory content for those paths); clear staging; restore working files for stashed paths to HEAD tree content where applicable.
2. **`stash list`** — show stack (index, message, timestamp).
3. **`stash pop`** — apply top entry (re-stage + rewrite WD files), then drop it. Abort with a clear error if applying would overwrite divergent WD content (no textual merge).

Surfaces: **CLI + Flask** (parity with existing stage/commit UI).

## Assumptions
- “Uncommitted changes” for MVP = **staging area** plus **working-dir file bytes for staged paths** (tracked add/delete). Untracked-only files are out of MVP unless already staged via `add`.
- Single-parent commits stay as today; stash is **not** a commit object (optional message string only).
- No remotes; stash is local to `.minigit` SQLite.
- `AGENTS.md` rules apply (parameterized SQL, hash/ref validation, layer boundaries).

## MVP
| In | Out |
|----|-----|
| `stash push` (default message ok) | `stash branch`, `stash drop <n>` beyond pop |
| `stash list` | Stash of arbitrary untracked trees |
| `stash pop` (top only) | Conflict auto-merge / 3-way merge |
| Persist stack in SQLite | Multiple named stashes / reflog |
| CLI + web UI | Full `git stash show -p` |

## Not Doing
- Merge / multi-parent commits
- Status command as a prerequisite product (may add a small helper used only by stash)
- Rebase, tags, remotes
- Binary / ignored-extension files beyond current Tree ignore rules

## Open questions (for plan/spec; escalate only if blocking)
- Should `push` also include **unstaged** modifications to tracked files not in the index? **Proposal for MVP: no** — only staging (+ WD for staged paths), matching MiniGit’s stage-centric model; note as follow-up if human wants parity with full Git.
