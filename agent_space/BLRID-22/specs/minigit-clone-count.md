# Spec: MiniGit clone + clone count (BLRID-22)

## ASSUMPTIONS

- Scope = Jira **BLRID-22** description/AC only (+ idea one-pager).
- Local filesystem clone only; no remotes.
- Clone counter is stored in the **source** repository’s SQLite DB and increments only after a successful clone completes.
- Dest path must not already contain `.minigit`; if it exists and is non-empty with a repo, fail.
- CLI is required; Flask UI is **optional** for MVP (include only if it fits a thin slice without blocking AC).
- Follow `AGENTS.md` layers: persistence in `backend/`, orchestration in `frontend/`, thin `cli.py` / `app.py`.
- **Already covered:** none for clone/counter — all build. Duplicates: none besides BLRID-22.

## Objective

Add `minigit clone` to copy a MiniGit repo and a durable counter so users can see how many times clone succeeded.

## Commands / surfaces

| Surface | Behavior |
|---------|----------|
| CLI `minigit clone <source> [dest]` | Copy source MiniGit repo to dest; print success + current clone count |
| CLI `minigit clone-stats` | Print clone count for current repo (or error if not a repo) |
| Flask (optional) | Display clone count on repo page / simple clone form — defer if time |

## Structure

```
src/backend/sqlite_client.py   # meta/stats table: get/set clone_count
src/frontend/clone.py          # OR methods on Operations — clone_repo + get_clone_count
src/frontend/operations.py     # thin wrappers if separate module
src/cli.py                     # clone, clone-stats subcommands
tests/test_clone.py            # success, missing source, bad dest, counter
```

Prefer mirroring existing patterns (`Operations` + optional dedicated module like merge if present on implement branch).

## Style

- Type annotations on public functions; parameterized SQL; validate paths (no shelling user input).
- Conventional commits: `feat: …`
- Keep functions < 50 lines / files < 300 lines per `AGENTS.md`.

## Testing

- Success: init repo A → clone to B → B is usable (`log`/`ls`); counter == 1 on A.
- Second clone → counter == 2.
- Missing source → clear error; counter unchanged.
- Dest already a MiniGit repo → clear error; counter unchanged.
- `make check` green.

## Boundaries

- **In:** local clone copy of `.minigit` DB (+ working tree files if repo layout requires); counter R/W; CLI.
- **Out / ask-first:** network remotes, shallow clone, new dependencies, deploy.
- **Reuse vs build:** no reuse for clone; reuse SQLiteClient patterns and CLI argparse style.

## Success criteria (testable)

1. `minigit clone` creates a working MiniGit copy.
2. Successful clones increment the counter; failures do not.
3. User can see the count via CLI.
4. Tests under `tests/` cover happy path + errors.
5. `make check` passes.

## Open questions (non-blocking for plan)

- Exact copy strategy: full directory copy of repo root vs `.minigit` only — **decide in implement**: prefer copying entire source tree when dest is empty, ensuring `.minigit` is included; document in PR.
- Whether counter should also appear in Flask — **MVP = CLI first**.
