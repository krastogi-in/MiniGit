# Implementation Plan: AI-Powered Commit Message Assistant

**Issue:** [BLRID-19](https://redhat.atlassian.net/browse/BLRID-19)
**Phase:** plan
**PR branch:** `aiagent/BLRID-19`

## Task Dependency Graph

```
T1 (get_staged_diffs) ─► T2 (CommitMessageGenerator) ─► T3 (CLI commit)
                                                       ─► T4 (Web endpoint)
                                                       ─► T5 (Tests)
```

## Tasks

### T1: Add `get_staged_diffs()` to Operations

**Build** (no existing coverage)

- Add method `Operations.get_staged_diffs()` → `list[dict]`
- Computes diff between staged entries and current HEAD tree
- Returns list of `{path, action, old_content, new_content}` dicts
- Reuses `_flatten_tree`, `get_staged`, `get_blob_content`
- **Files:** `src/frontend/operations.py`
- **Acceptance:** method returns correct diffs for staged adds, modifies, deletes
- **Verify:** unit test in T5
- **Size:** S

### T2: Create `CommitMessageGenerator` module

**Build** (no existing coverage)

- New file `src/frontend/commit_assistant.py`
- `GenerationResult` dataclass: `message`, `commit_type`, `summary`, `file_count`, `change_types`
- `CommitMessageGenerator.__init__(ops: Operations)`
- `CommitMessageGenerator.generate() -> GenerationResult`
- Heuristic classification by file path/extension + change patterns
- Template-based summary generation
- Message capped at 72 chars, conventional-commit format
- **Files:** `src/frontend/commit_assistant.py`
- **Acceptance:** generates correct type + summary for single/multi file scenarios
- **Verify:** unit tests in T5
- **Size:** M

---
**Checkpoint 1:** T1 + T2 complete → generator works in isolation

---

### T3: Add CLI `commit` subcommand

**Build** (no existing coverage — CLI has no commit command)

- Add `commit` subcommand to argparse in `main()`
- Flags: `-m MESSAGE` (manual), `--ai` (generate), `--yes` (auto-accept with `--ai`)
- `--author` optional
- `cmd_commit()` implementation:
  - With `-m`: call `ops.create_new_commit(message, author)`
  - With `--ai`: call generator, print suggestion, prompt accept/edit/reject (unless `--yes`)
  - Validate: require either `-m` or `--ai`
- **Files:** `src/cli.py`
- **Acceptance:** `minigit commit -m "msg"` and `minigit commit --ai` both work
- **Verify:** manual + unit test in T5
- **Size:** M

### T4: Add web UI suggest-message endpoint

**Build** (no existing coverage)

- Add `GET /repo/<name>/suggest-message` to Flask app
- Returns JSON `{"message": "...", "commit_type": "...", "summary": "...", "file_count": N, "change_types": {...}}`
- Error case: no staged changes → `{"error": "Nothing staged"}, 400`
- **Files:** `src/app.py`
- **Acceptance:** endpoint returns valid JSON with a generated message
- **Verify:** unit test in T5
- **Size:** S

---
**Checkpoint 2:** T3 + T4 complete → all surfaces wired up

---

### T5: Comprehensive tests

**Build** (no existing coverage)

- New file `tests/test_commit_assistant.py`
- Test cases:
  1. Single file added → `feat: add <filename>`
  2. Test file added → `test: add test_<name>`
  3. Docs file modified → `docs: update <filename>`
  4. Config file added → `chore: add <filename>`
  5. Multiple files added → correct type + count
  6. Mixed add/modify/delete → correct classification
  7. No staged changes → ValueError or empty
  8. Message length ≤ 72 chars
  9. Integration: generate → commit → verify in history
  10. `get_staged_diffs()` returns correct structure
  11. Web endpoint returns valid JSON
- All tests use `tmp_path`
- **Files:** `tests/test_commit_assistant.py`
- **Acceptance:** all tests pass, `make check` green
- **Verify:** `make check`
- **Size:** L

---
**Checkpoint 3:** All tests pass → ready for PR

---

## Architecture Notes

- `commit_assistant.py` imports from `operations.py` only (follows dependency rules)
- No new external dependencies
- No changes to `components/` or `backend/` layers
- Security: no user input executed; all hash validation via existing validators
