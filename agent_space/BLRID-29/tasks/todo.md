# Todo: BLRID-29 safe reset

## T1 — RED tests
- [ ] Acceptance: failing tests for dry-run, soft, mixed, hard, errors
- [ ] Verify: pytest fails on missing API
- [ ] Files: `tests/test_reset.py`

## T2 — GREEN ops preview + apply
- [ ] Acceptance: ancestor reset soft/mixed; preview accurate
- [ ] Verify: pytest green for those cases
- [ ] Files: `src/frontend/operations.py`

## T3 — Hard + dirty
- [ ] Acceptance: hard syncs files; dirty aborts without `--force`
- [ ] Verify: pytest
- [ ] Files: ops + tests

## T4 — CLI
- [ ] Acceptance: flags work; `--yes` required to apply
- [ ] Verify: manual/CLI smoke
- [ ] Files: `src/cli.py`

## T5 — Optional web
- [ ] Acceptance: shipped or explicitly deferred in PR
- [ ] Verify: N/A if deferred

## T6 — Gate
- [ ] Acceptance: `make check`; PR `aiagent/BLRID-29` on rajusem → upstream
- [ ] Verify: `make check`
