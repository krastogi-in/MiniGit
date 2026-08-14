# Plan: BLRID-8 — Single-file verification docs

## Overview

Docs-only vertical slice: add **Single-file verification** to `AGENTS.md`, smoke-test documented commands, verify skill registry.

**PR branch (implement phase):** `aiagent/BLRID-8`

## Architecture

No code architecture changes. Single file edit: `AGENTS.md`.

## Task graph

```
T1 (draft section) → T2 (smoke verify) → T3 (eval-skills)
```

## Checkpoints

| After | Verify |
|-------|--------|
| T1 | Section readable; commands match Makefile |
| T2 | Both example `make verify` commands succeed |
| T3 | `make eval-skills` OK |

## Risk

- **Low** — documentation only; Makefile target already exists.

## Duplicates / coverage

- Reuse existing `make verify` — no Makefile changes unless smoke reveals doc/Makefile drift (escalate if so).
