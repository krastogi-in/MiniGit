# BLRID-3 TODO

Status key: `todo` | `doing` | `done` | `blocked`

| ID | Status | Task | Notes |
|---|---|---|---|
| T1 | done | Extend commit persistence to support second parent | Added `parent_hash2` with compatibility migration |
| T2 | done | Add ancestor/common-base helpers in operations | Added ancestor collection + merge-base selection |
| T3 | done | Implement merge flow cases (up-to-date, FF, diverged) | Merge now returns deterministic status payload |
| T4 | done | Implement conflict detection and abort path | Conflicts raise and preserve target tip |
| T5 | done | Write merge commit with two parents | Parent order is current tip then source tip |
| T6 | done | Add CLI `merge` command wiring | Added `minigit merge <source-branch>` |
| T7 | done | Add Flask merge trigger and messages | Added merge route + UI form in repo detail |
| T8 | done | Add tests for all AC scenarios | Added operations/sqlite/cli/flask merge tests |
| T9 | blocked | Run full quality checks | `pytest tests/ -v` passes; `make check` blocked by pre-existing repo lint baseline |

## Current Gate
- Maker implementation complete; awaiting human implementation review gate.
