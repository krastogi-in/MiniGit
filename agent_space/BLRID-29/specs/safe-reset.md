# Spec: MiniGit safe reset (BLRID-29)

## ASSUMPTIONS

1. Scope = BLRID-29 only; not revert (BLRID-23) or reflog.
2. Single-parent history; target must be an ancestor of current tip (safer MVP). If target is not ancestor → clear error (no arbitrary tip jump in v1) **unless** we allow any commit on same repo—**MVP: ancestor-only** for safety.
3. No existing reset; reuse flatten/history/refs/staging.
4. Hard mode includes writing blob contents to working tree for tracked paths.
5. Author/`$USER` unchanged; no new auth.

## Objective

Add safe `reset` that moves the current branch tip to a target commit with a **loss preview**, supporting soft/mixed/hard.

## Commands / surfaces

| Surface | Behavior |
|---------|----------|
| Ops | `preview_reset(...)` + `reset(..., dry_run=False)` |
| CLI | `minigit reset [--soft\|--mixed\|--hard] [--dry-run] [--yes] [--force] <commit-hash>` |
| Web | Optional confirm UI |

Default mode: **mixed**. Apply requires `--yes` unless `--dry-run`.

## Structure

- `src/frontend/operations.py` — preview + apply
- `src/cli.py` — subcommand
- `tests/test_reset.py`
- Optional `app.py` / templates

### Semantics

| Mode | Tip | Staging | Working tree |
|------|-----|---------|--------------|
| soft | → target | unchanged | unchanged |
| mixed | → target | cleared | unchanged |
| hard | → target | cleared | synced to target tree |

### Preview contents

- Mode, current tip, target
- List of commits on tip that are not reachable after reset (walk tip until target)
- Hard: counts of paths overwritten / deleted / created vs current disk for tracked files
- Warning if dirty staging / dirty tracked files

### Safety

1. Validate 64-hex hash; commit must exist.
2. Target must be ancestor of tip (inclusive: no-op if equal).
3. hard + dirty tracked vs tip tree → abort unless `--force`.
4. Apply without `--yes` → error telling user to pass `--yes` or `--dry-run`.
5. Update only current branch ref + HEAD if stored; never other branches.

## Style

`AGENTS.md`; parameterized SQL; type hints; conventional commit `feat: add safe reset with preview`.

## Testing

| Case | Expect |
|------|--------|
| dry-run | tip unchanged; preview lists commits |
| soft | tip moved; staging retained |
| mixed | tip moved; staging empty |
| hard | tip moved; files match target; staging empty |
| unknown hash | error |
| non-ancestor | error |
| hard dirty without force | error |
| missing --yes on apply | error |

Verify: `make check`. PR: `aiagent/BLRID-29` via `rajusem` fork.

## Boundaries

In: CLI+ops+tests (+ optional web). Out: reflog, short hash, rebase.

## Success Criteria

Ticket AC met; tests green; `make check`.

## Open Questions

1. Ancestor-only vs any commit? **Default ancestor-only.**
2. Web in same PR? **Optional stretch.**
