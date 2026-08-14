# TODO: BLRID-19 — AI-Powered Commit Message Assistant

| # | Task | Status | Files | Size | Checkpoint |
|---|------|--------|-------|------|------------|
| T1 | Add `get_staged_diffs()` to Operations | pending | `src/frontend/operations.py` | S | 1 |
| T2 | Create `CommitMessageGenerator` module | pending | `src/frontend/commit_assistant.py` | M | 1 |
| T3 | Add CLI `commit` subcommand | pending | `src/cli.py` | M | 2 |
| T4 | Add web UI suggest-message endpoint | pending | `src/app.py` | S | 2 |
| T5 | Comprehensive tests | pending | `tests/test_commit_assistant.py` | L | 3 |

## Checkpoints

- **CP1:** T1 + T2 → generator works in isolation
- **CP2:** T3 + T4 → all surfaces wired up
- **CP3:** T5 → all tests pass, `make check` green → PR ready
