# Plan: Stash feature (BLRID-10)

**PR branch (implement phase):** `aiagent/BLRID-10`  
**Spec:** `agent_space/BLRID-10/specs/stash-feature.md`  
**Already covered:** none for stash — all tasks **build** except reuse of staging/blob APIs (**reuse**).

## Architecture
1. SQLite `stashes` table for LIFO stack (payload JSON).
2. `Operations.stash_push|list|pop` using existing stage/blob/tree helpers.
3. CLI `stash` subcommands + Flask buttons on working-dir view.
4. Tests first where practical (TDD in implement/test phases).

## Task table

| ID | Task | Size | Type | Depends |
|----|------|------|------|---------|
| T1 | Schema: `stashes` table + CRUD in `sqlite_client` | M | build | — |
| T2 | `stash_push` / `stash_list` / `stash_pop` in `operations` | L | build | T1 |
| T3 | Unit/integration tests for stash ops | M | build | T2 |
| T4 | CLI `stash` (push/list/pop) | S | build | T2 |
| T5 | Flask routes + template affordances | M | build | T2 |
| T6 | README CLI usage + `make check` | S | build | T3–T5 |

## Checkpoints
- **CP1** after T1–T2: push/list/pop work via Python API in a tmp repo.
- **CP2** after T3: pytest covers happy/empty/conflict.
- **CP3** after T4–T6: CLI + UI + README; open PR on `aiagent/BLRID-10`.

## High-risk early
T1/T2 — payload shape and pop conflict rules; get these right before UI polish.

## Verify (overall)
```bash
make check
```
