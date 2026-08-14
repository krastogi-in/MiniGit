# Checker review: BLRID-11 MiniGit status

**PR:** https://github.com/krastogi-in/MiniGit/pull/9  
**Role:** Checker (separate from maker)  
**Rubric:** evals/rubrics/review.md — pass (Suggestions only; no Critical)

## Five axes

| Axis | Severity | Notes |
|------|----------|-------|
| Correctness vs AC | Pass | Branch + staged/empty + Flask + HEAD persistence covered |
| Tests | Suggestion | CLI path covered for empty staged + find_repo; no CLI test with staged files; bad-repo is find_repo-level not full `sys.exit` |
| Security | Pass | Reuses validated `get_ref`/`set_ref`/`get_staged`; no new SQL/secrets |
| Maintainability | Suggestion | `create_branch` also writes HEAD (matches prior in-memory switch); document or keep as intentional MiniGit quirk |
| Completeness | Suggestion | Full `make check` still red on **pre-existing** cov-fail-under=60 (app/cli); not introduced by this PR |

## Inline findings (PR)

1. **Suggestion** `src/cli.py` `cmd_status` — add a test that stages a file then asserts CLI output lists the path (Operations already covered).
2. **Suggestion** `src/frontend/operations.py` `create_branch` — now persists HEAD when creating (side effect of switching); worth a one-line docstring note.
3. **Suggestion** AC “non-zero exit” — `get_ops` already exits; consider asserting `SystemExit` via CLI entry for missing repo if you want strict AC proof.

## Security checklist

- [x] Parameterized SQL (no new queries)
- [x] Hash/ref validation via existing backend
- [x] No secrets

## Verdict input

No Critical. Ready for outer-loop **VERDICT**: ship | block | redirect | narrow.
