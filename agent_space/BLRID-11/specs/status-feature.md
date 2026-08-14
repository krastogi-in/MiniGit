# Spec: MiniGit status (BLRID-11)

## ASSUMPTIONS

1. Scope is only BLRID-11 Description (status = current branch + staged files; CLI + Flask).
2. Reuse `SQLiteClient.get_staged()` / `Operations.get_staged()` — no staging schema change.
3. For “current branch” to work across CLI process boundaries, Operations must **read HEAD** from the DB on init and **write HEAD** on checkout (today checkout only mutates in-memory `self.branch`).
4. Short hash display (first 8–12 hex chars) is OK for staged blob hashes.
5. Invalid/missing repo: no `.minigit` / unreadable DB → clear error; CLI exits non-zero.
6. AGENTS.md layers: status logic in `frontend/`; CLI/app thin; no new deps.
7. Duplicates: none for status; BLRID-5/6 are unrelated (CI / branch-diff).
8. Human approval of this spec is deferred to plan **HUMAN GATE** (`sdlc:human-ready`).

## Objective

Deliver `minigit status` and a Flask status surface that report the current branch and staged files (or that nothing is staged), failing clearly on a missing/invalid repo.

## Commands

```bash
make check          # lint + typecheck + test
# manual / tests:
minigit status      # after init; with and without staged files
```

## Structure

| Layer | Change |
|-------|--------|
| `frontend/operations.py` | Load branch from HEAD; update HEAD on checkout; add `status()` → `{branch, staged}` |
| `cli.py` | `status` subcommand |
| `app.py` + template | Status route or section on repo page |
| `tests/test_status.py` | AC coverage |

## Style

- Type annotations on public functions
- Parameterized SQL only (no new SQL unless HEAD helpers already exist)
- Conventional commits: `feat:` / `test:`
- Keep functions under 50 lines; files under 300 lines

## Testing

- Current branch after init / after checkout
- Empty staged → “nothing staged” (or equivalent clear message)
- Staged files listed (path present)
- Missing/invalid repo → error path
- Prefer `tmp_path` fixtures; no network

## Boundaries

- **In:** FF-style thin vertical slice for status only; HEAD persistence fix as required for AC
- **Out / ask first:** full Git porcelain (untracked/modified/deleted); new deps; deploy beyond `make check`
- **Reuse:** `get_staged`; existing branch/checkout APIs
- **Build:** `status()` API, CLI, Flask, tests, HEAD read/write

## Success criteria

- [ ] `minigit status` shows current branch name
- [ ] `minigit status` lists staged files or clearly says none
- [ ] Missing/invalid repo → clear error; non-zero CLI exit
- [ ] Flask UI exposes the same status info
- [ ] Tests under `tests/` for branch, empty staged, staged with files, bad repo
- [ ] `make check` / `AGENTS.md` followed

## Open questions

- None blocking; HEAD persistence is an in-scope technical gap, not a product ambiguity.
