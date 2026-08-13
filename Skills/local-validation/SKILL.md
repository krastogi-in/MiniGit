---
name: local-validation
description: >-
  Validate code changes locally before committing. Pre-declare expected outcomes,
  run verification commands, and compare actual results. Use after implementing
  a phase, before committing, or when verifying that changes work correctly.
---

# Local Validation

"All tests pass" does not mean "the code is correct." This skill forces
observable validation: pre-declare what you expect, run it, compare.

## When to use

- After each implementation slice (before commit)
- Before claiming a phase is done
- When the `incremental-implementation` skill says "relevant verifies"

## MiniGit verification commands

| Goal | Command | What to check |
|------|---------|---------------|
| All quality checks | `make check` | Exit code 0 |
| Lint only | `make lint` | No new ruff errors |
| Type check only | `make typecheck` | No new mypy errors |
| Tests only | `make test` | All tests pass; coverage not regressed |
| Boundaries | `make boundaries` | All contracts kept |
| Skill registry | `make eval-skills` | All skill evals pass |

## Validation checklist

### Step 1: Pre-declare expected outcomes

Before running anything, write down:
- Which tests you expect to pass/fail
- What CLI commands should produce
- What behavior the web UI should show
- Any edge cases that should be handled

### Step 2: Run verification

```bash
make check          # lint + typecheck + test + boundaries
make eval-skills    # skill registry integrity
```

### Step 3: Compare and document

| Test case | Expected | Actual | Status |
|-----------|----------|--------|--------|
| `make lint` | No new errors | ... | PASS/FAIL |
| `make test` | All green | ... | PASS/FAIL |
| CLI: `python src/cli.py init` | Creates .minigit/ | ... | PASS/FAIL |

### Step 4: Smoke test (when changing app behavior)

For CLI changes:
```bash
cd /tmp && mkdir test-repo && cd test-repo
python src/cli.py init
python src/cli.py log
python src/cli.py branch feature
```

For Flask changes:
```bash
python src/app.py &
curl -s http://localhost:5000/ | head -20
kill %1
```

## Rules

- **Pre-declare before running.** Don't run first and rationalize after.
- **"No exceptions" is not "correct."** Zero errors may mean the code path
  was never reached. Check positive outcomes, not just absence of failure.
- **Document what you checked.** The validation table becomes evidence for
  the phase report.
- **Fresh state for each run.** Use `tmp_path` or `/tmp` directories to
  avoid stale data from previous test runs.

## Deterministic

- [ ] Expected outcomes pre-declared
- [ ] `make check` run (or equivalent)
- [ ] Actual vs expected comparison documented
- [ ] No regressions in lint, type, test, or boundary checks
- [ ] Smoke test run if app behavior changed

## What You Are NOT

- You are NOT a substitute for the test suite — run the real tests
- You are NOT done when "no errors" — verify positive outcomes too
