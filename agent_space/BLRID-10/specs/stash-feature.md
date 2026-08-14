# Spec: Stash feature (BLRID-10)

## ASSUMPTIONS
- Scope is only BLRID-10 (save uncommitted work and restore later).
- No duplicate tickets; no existing stash code — **build**, reuse staging/blobs.
- MVP stash payload = staging entries + working-dir content for staged paths only (not full Git WD/index).
- Stash is a SQLite stack, not a commit; single-parent model unchanged.
- On `pop`, if a target path’s working file differs from both HEAD and the stash payload in a conflicting way, **abort** (no textual merge).
- CLI + Flask both required; follow `AGENTS.md` layer rules and `make check`.

## Objective
Implement MiniGit stash so users can push uncommitted staged work onto a LIFO stack, list entries, and pop the top entry back into staging + working directory.

## Commands / API
| Surface | Behavior |
|---------|----------|
| CLI `stash` / `stash push [-m msg]` | Save staging (+ WD for those paths); clear staging; reset those WD paths toward HEAD where applicable |
| CLI `stash list` | Print stack (newest first): index, short id/message, timestamp |
| CLI `stash pop` | Apply top; drop on success; error if empty or conflict |
| Flask | Working-dir / staging area: Stash / List / Pop actions + flash messages |

Ops methods (names suggestive): `stash_push`, `stash_list`, `stash_pop` on `Operations`.

## Structure
- **Backend:** new `stashes` table (e.g. `id`, `created_at`, `message`, `payload_json`) — parameterized SQL only.
- **Frontend:** `operations.py` orchestrates capture/restore; may use private helpers to compare path content to HEAD tree.
- **CLI:** `cli.py` subcommands under `stash`.
- **Web:** routes + templates near existing stage/commit UI.
- **Tests:** `tests/test_stash.py` (or extend operations tests) with `tmp_path`.
- Scratch only under `agent_space/BLRID-10/`; product code in `src/` / `tests/`.

Payload JSON sketch (illustrative): list of `{path, action, blob_hash?, wd_content?}`.

## Style
- Type annotations on public functions; conventional commits `feat:` / `test:`.
- Validate paths; never execute user input; keep functions &lt;50 lines / files &lt;300 where practical.
- Layers: `components` ← no backend; `backend` ← no frontend; `cli`/`app` ← frontend only.

## Testing
- Push with empty staging → clear error.
- Push then list → one entry; staging empty.
- Pop restores staging (+ WD content); stack empty.
- Pop on empty stack → error.
- Conflict on pop → abort, stash retained.
- `make check` green on branch `aiagent/BLRID-10`.

## Boundaries
| In scope | Out of scope |
|----------|--------------|
| LIFO push / list / pop | `stash apply` keep, `drop <n>`, `branch` |
| Staged-path MVP | Unstaged-only WD changes, untracked bulk |
| Abort on conflict | Merge conflict UI / auto-merge |
| CLI + Flask | Remotes, tags, rebase |

## Success criteria
1. User can stash non-empty staging and get a clean staging area afterward.
2. User can list stashes and pop the latest to continue work.
3. Tests prove empty/conflict/happy paths; `make check` passes.
4. Docs: README CLI usage line(s) for stash (minimal).

## Open questions
- Confirm MVP excludes unstaged-only modifications (default **yes** unless human gate says otherwise).
- Optional message flag on push (default yes, small).
