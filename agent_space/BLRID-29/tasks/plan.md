# Plan: MiniGit safe reset (BLRID-29)

## Overview

PR branch: **`aiagent/BLRID-29`** (push to remote **`rajusem`**). Ancestor-only tip move with preview.

## Tasks

| ID | Task | Size | Files |
|----|------|------|-------|
| T1 | RED: tests for preview + soft/mixed/hard/errors | S | `tests/test_reset.py` |
| T2 | GREEN: `preview_reset` / `reset` in Operations | M | `operations.py` |
| T3 | Hard working-tree sync helper + dirty detection | M | `operations.py` |
| T4 | CLI flags `--soft/--mixed/--hard/--dry-run/--yes/--force` | S | `cli.py` |
| T5 | Optional web confirm panel | S | app/templates |
| T6 | `make check` + PR to upstream from fork | S | — |

## Checkpoints

- After T2: unit behavior solid
- After T4: demoable CLI
- After T6: `sdlc:agent-approved`

## Risks

| Risk | Mitigation |
|------|------------|
| Hard sync without full checkout feature | Implement minimal write/delete tracked paths only |
| Orphan detection wrong | Walk parent chain tip→target; stop at target |
| Accidental apply | Require `--yes` |
