# Idea: Single-file verification in AGENTS.md (BLRID-8)

## How Might We

How might we help AI agents and contributors verify a **single changed file** quickly, without running the full `make check` suite?

## User

- **Primary:** Cursor agents editing MiniGit product code (`src/`, `tests/`)
- **Secondary:** Human contributors following `AGENTS.md` during PR prep

## Success criteria

- AgentReady **Single-File Verification** attribute passes on re-assess
- An agent can copy-paste commands from `AGENTS.md` and lint/typecheck one file in under ~10s
- `make eval-skills` still passes (no registry breakage)

## Recommended direction

Add a **Single-file verification** section to `AGENTS.md` under Development Commands that documents:

1. `make verify FILE=<path>` (preferred — matches Makefile)
2. Direct equivalents: `ruff check <file>` and `mypy <file>`
3. One example each for `src/` and `tests/`

## Assumptions

- `make verify` in the Makefile is correct and stays the source of truth
- Docs-only change; no `src/` or `tests/` edits required for MVP
- BLRID-5 (CI pipeline) is a separate ticket; out of scope here

## MVP

- One new section in `AGENTS.md` (~15–25 lines)
- Manual smoke: run documented commands on `src/components/blob.py` and `tests/test_blob.py`

## Not doing

- CI workflow changes (BLRID-5)
- Fixing existing `make check` lint failures repo-wide
- Adding `CLAUDE.md` (AGENTS.md is the project agent instruction file)
- Pre-commit hook changes

## Duplicate check

| Key | Summary | Overlap |
|-----|---------|---------|
| BLRID-5 | GitHub Actions CI | Related SDLC test; different deliverable (CI vs docs) |
| — | None other | No open ticket targets AGENTS.md single-file docs |

## Already covered (repo scan)

| Area | Status |
|------|--------|
| `Makefile` `verify` target | **Exists** — `ruff check` + `mypy` on `$(FILE)` |
| `AGENTS.md` Development Commands | Lists `make lint`, `typecheck`, `check` — **no per-file docs** |
| AgentReady reports | Gap flagged (30/100 partial — Makefile exists, AGENTS.md missing) |

**Conclusion:** Build = document existing `make verify`; no new tooling.
