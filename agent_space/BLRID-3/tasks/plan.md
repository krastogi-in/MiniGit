# BLRID-3 Plan: MiniGit Merge

## Scope Lock
- Use BLRID-3 issue content only.
- Implement after plan approval gates only.
- Reuse existing commit/tree/diff/branch primitives where possible.

## Coverage and Reuse Strategy
- **Reuse / verify-only**
  - Existing commit/tree flatten/build helpers in `Operations`.
  - Existing ref read/write and commit retrieval in `SQLiteClient`.
  - Existing CLI + Flask command/route patterns.
- **Build**
  - Merge ancestry + base resolution helpers.
  - Diverged three-way merge file-hash resolver with conflict detection.
  - Two-parent commit persistence.
  - CLI `merge` command and Flask merge route/form.
  - Merge tests.

## Task Breakdown

| ID | Task | Type | Files | Acceptance | Verify |
|---|---|---|---|---|---|
| T1 | Extend commit schema for second parent | build | `src/backend/sqlite_client.py`, tests | Commit rows can store/retrieve `parent_hash2` for merge commits; non-merge unaffected | targeted pytest for sqlite client |
| T2 | Add ancestry/base helpers in operations | build | `src/frontend/operations.py`, tests | Can detect ancestor relation and common base commit | targeted pytest for operations |
| T3 | Implement merge decision flow (up-to-date/FF/diverged) | build | `src/frontend/operations.py`, tests | Returns deterministic outcomes and keeps tip unchanged on errors | targeted pytest for operations |
| T4 | Implement conflict detection + merge tree build | build | `src/frontend/operations.py`, tests | Diverged clean merge succeeds; conflicting paths abort safely | targeted pytest for operations |
| T5 | Create two-parent merge commit write path | build | `src/frontend/operations.py`, `src/backend/sqlite_client.py`, tests | Merge commit records parent1=current HEAD and parent2=source tip | targeted pytest for operations/sqlite |
| T6 | Add CLI merge command | build | `src/cli.py`, tests | `minigit merge <source>` invokes operations merge and prints outcome/error | targeted pytest CLI coverage |
| T7 | Add Flask merge action | build | `src/app.py`, templates, tests | UI can pick source branch and trigger same merge behavior | targeted pytest app coverage |
| T8 | End-to-end regression + quality | verify | `tests/`, maybe fixtures | AC scenarios all pass; no regressions in existing operations | `make check` |

## Vertical Slice Checkpoints
- **Checkpoint A (T1-T3):** safe relation detection and no-op/FF behavior done.
- **Checkpoint B (T4-T6):** diverged merge path + conflicts + CLI done.
- **Checkpoint C (T7-T8):** Flask integration and full checks done.

## Risk-First Notes
- Highest risk: schema change for two-parent commit and compatibility with existing commit readers.
- Next risk: merge-base logic with currently linear-history assumptions.
- Mitigation: land tests for each risk before broad integration.

## Branch and PR
- Implementation branch: `aiagent/BLRID-3`
- PR opens after maker phase only and before checker phase.

## Gate Reminder
- Do not start implementation until both are present:
  - `sdlc:agent-ready`
  - `sdlc:human-ready`
