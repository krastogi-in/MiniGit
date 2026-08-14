# BLRID-27 Spec: Create architecture.md

## Assumptions
- Scope is limited to creating an architecture document task.
- No implementation behavior changes are required.
- Existing repository structure and `AGENTS.md` conventions define the architecture baseline.

## Objective
Produce an `architecture.md` document that describes MiniGit architecture for maintainers and contributors.

## Deliverable
- One markdown file: `architecture.md` (final location decided in implementation stage).

## Content Requirements
- Project purpose and high-level design.
- Layer boundaries and allowed dependencies:
  - `components/`
  - `backend/`
  - `frontend/`
  - `cli.py` and `app.py`
- Data model concepts:
  - blob, tree, commit, refs
  - SQLite storage model
- Operation flow:
  - CLI/UI -> frontend operations -> backend persistence
- Testing and quality flow:
  - `make` commands and expected checks

## Style Requirements
- Concise and readable for new contributors.
- Aligned with current code (no speculative/future architecture).
- Use headings and short sections; avoid oversized prose.

## Boundaries
- No code behavior changes.
- No new dependencies.
- No architectural redesign proposal in this ticket.

## Success Criteria
- `architecture.md` is present and accurate.
- Document reflects current repository structure and dependency rules.
- Documentation task is reviewable and test/check process remains green.

## Open Questions
- Preferred final location: repo root vs `docs/`.
