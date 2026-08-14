# Spec: AI-Powered Commit Message Assistant

**Issue:** [BLRID-19](https://redhat.atlassian.net/browse/BLRID-19)
**Phase:** spec
**Idea:** `agent_space/BLRID-19/ideas/ai-commit-assistant.md`

## Assumptions

1. The MVP uses **rule-based heuristics** only (no external API calls, no LLM).
2. The CLI currently has no `commit` subcommand — adding one is prerequisite work
   implied by the acceptance criteria.
3. Diff computation between staged changes and HEAD is achievable using existing
   `Operations._flatten_tree` + `SQLiteClient.get_staged` + blob content retrieval.
4. Conventional commit types are limited to: `feat`, `fix`, `docs`, `refactor`,
   `test`, `chore`, `style`.
5. The generator module lives in `src/frontend/` (it orchestrates components + backend).
6. No existing code covers this feature — building from scratch.
7. `make check` (lint + typecheck + test) must pass before the feature is complete.

## Objective

Provide a commit message suggestion engine that analyzes staged diffs and
produces a conventional-commit-formatted message, exposed via both CLI and
web UI, with user review before committing.

## Commands / Surfaces

### CLI

```
minigit commit -m "message"       # commit with explicit message
minigit commit --ai                # generate message, print, prompt accept/edit/reject
minigit commit --ai --yes          # auto-accept generated message (no prompt)
```

The `commit` subcommand replaces the missing CLI entry point for committing.
It calls `Operations.create_new_commit(message, author)`.

### Web UI

- **Endpoint:** `GET /repo/<name>/suggest-message`
  - Returns JSON: `{"message": "feat: ...", "details": {...}}`
  - Called via JavaScript from the commit page
- **UI:** "Suggest message" button next to the commit message textarea on
  the working-dir/staging page

### Python API

```python
from frontend.commit_assistant import CommitMessageGenerator

gen = CommitMessageGenerator(ops)
result = gen.generate()
# result.message -> "feat: add new configuration file"
# result.commit_type -> "feat"
# result.summary -> "add new configuration file"
# result.file_count -> 1
# result.change_types -> {"added": 1}
```

## Structure

### New files

| File | Purpose |
|------|---------|
| `src/frontend/commit_assistant.py` | `CommitMessageGenerator` class |
| `tests/test_commit_assistant.py` | Unit tests for the generator |

### Modified files

| File | Change |
|------|--------|
| `src/cli.py` | Add `commit` subcommand with `-m` and `--ai` flags |
| `src/app.py` | Add `GET /repo/<name>/suggest-message` endpoint |
| `src/frontend/operations.py` | Add `get_staged_diffs()` method (diff staged vs HEAD) |

### Architecture

```
User (CLI --ai / Web button)
  └─► CommitMessageGenerator(ops)
        ├─► ops.get_staged_diffs()    # new method
        │     ├─► ops.get_staged()
        │     ├─► ops._flatten_tree(HEAD tree)
        │     └─► ops.get_blob_content(hash)
        ├─► _classify_change_type()    # feat/fix/docs/... heuristic
        ├─► _build_summary()           # concise subject line
        └─► GenerationResult           # dataclass with message + metadata
```

## Heuristic Rules (MVP)

1. **Type classification** — based on file paths and change patterns:
   - `test` files (`tests/`, `*_test.py`, `test_*.py`) → `test:`
   - Documentation files (`.md`, `docs/`) → `docs:`
   - Config files (`.toml`, `.cfg`, `.ini`, `.yml`, `.yaml`, `Makefile`) → `chore:`
   - Style-only changes (whitespace, formatting) → `style:`
   - Deletions-only → `refactor:` or `chore:`
   - New files added → `feat:`
   - Existing files modified → `fix:` (if small change) or `feat:` (if substantial)
   - Mixed changes → majority vote, default `feat:`

2. **Summary generation** — template-based:
   - Single file: `"<action> <filename>"` (e.g., "add config.toml")
   - Single directory: `"<action> <dirname> files"` (e.g., "update tests/ files")
   - Multiple files: `"<action> <count> files in <dir>"` or `"<action> <main-file> and <N> others"`
   - Action words: add, update, remove, rename (based on diff status)

3. **Output format:** `"<type>: <summary>"` (lowercase, no period, max 72 chars)

## Style

- Type annotations on all public functions
- Functions under 50 lines; `commit_assistant.py` under 300 lines
- Dataclass for `GenerationResult`
- No external dependencies beyond stdlib + structlog (already used)
- Parameterized SQLite queries only (no f-strings in queries)
- Validate all hash inputs per `AGENTS.md` security rules

## Testing

- `tests/test_commit_assistant.py`:
  - Single file added → `feat: add <filename>`
  - Test file added → `test: add test_<name>`
  - Docs file modified → `docs: update <filename>`
  - Multiple files → correct type + count summary
  - No staged changes → raises `ValueError` or returns empty result
  - Mixed add/modify/delete → correct classification
  - Message length ≤ 72 chars
  - Integration: generate → commit → verify commit message in history
- All tests use `tmp_path` fixture for isolation
- `make check` must pass

## Boundaries

- **In scope:** Heuristic-based message generation, CLI commit command, web UI
  suggest endpoint, unit tests
- **Out of scope:** LLM integration, multi-line bodies, git trailers, amend,
  commit signing, interactive rebase
- **No existing coverage** to reuse — building from scratch
- **No duplicate tickets** conflict with this design

## Success Criteria

1. `minigit commit --ai` produces a valid conventional-commit message from staged diffs
2. The web UI "Suggest message" button returns a JSON suggestion
3. Generated messages are grammatically reasonable and ≤ 72 chars
4. Users can accept, edit, or reject before committing (CLI interactive prompt)
5. Empty staging area produces a clear error, not a crash
6. `make check` passes (lint + typecheck + test)

## Open Questions

1. Should `--ai` be the default behavior when no `-m` is given? (Current design: no,
   require explicit `--ai` flag)
2. Should the web UI auto-fill the textarea or show a separate preview? (Current
   design: JSON API endpoint, JS fills textarea)
