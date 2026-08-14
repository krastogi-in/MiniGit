# Todo: BLRID-8

| ID | Task | Size | Type | Acceptance | Verify |
|----|------|------|------|------------|--------|
| T1 | Add **Single-file verification** section to `AGENTS.md` | S | build | Section under Development Commands; documents `make verify FILE=`, `ruff check`, `mypy`; includes `src/` and `tests/` examples | Visual review vs spec |
| T2 | Smoke-test documented commands | S | verify | `make verify` succeeds on one src + one test file | `make verify FILE=src/components/blob.py` and `make verify FILE=tests/test_blob.py` |
| T3 | Confirm skill registry healthy | S | verify | No SDLC registry regression | `make eval-skills` |

## Checkpoint 1 (after T1)

- [ ] `AGENTS.md` diff is docs-only
- [ ] Commands match `Makefile` `verify` target

## Checkpoint 2 (after T2–T3)

- [ ] Both verify commands exit 0
- [ ] `make eval-skills` passes
