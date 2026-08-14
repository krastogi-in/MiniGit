# Spec: Document single-file verification in AGENTS.md (BLRID-8)

## ASSUMPTIONS

- Scope is documentation only (`AGENTS.md`).
- `make verify FILE=...` in the Makefile is authoritative; spec does not change Makefile.
- Agents read `AGENTS.md` for product work; SDLC factory docs stay in `docs/ai-sdlc/`.
- Partial coverage: Makefile already implements verify; this ticket closes the documentation gap.

## Objective

Add agent-facing documentation so a single Python file can be linted and type-checked without `make check`.

## Commands

Document these (in order of preference):

```bash
make verify FILE=src/components/blob.py
ruff check src/components/blob.py
mypy src/components/blob.py
```

For test files, same pattern with `tests/` paths.

## Structure

Insert a **Single-file verification** subsection under `## Development Commands` in `AGENTS.md`, after the existing command block and before `## Conventions`.

Suggested content:

- When to use (agent editing one file, fast feedback)
- `make verify FILE=<path>` as primary
- Direct `ruff` / `mypy` alternatives
- Two copy-paste examples (`src/` + `tests/`)
- Note: full suite remains `make check`

## Style

- Match existing `AGENTS.md` tone (imperative, code blocks, short comments)
- No new dependencies or architecture changes

## Testing

| Check | Command |
|-------|---------|
| Docs smoke | `make verify FILE=src/components/blob.py` |
| Docs smoke | `make verify FILE=tests/test_blob.py` |
| Registry | `make eval-skills` |
| Optional full | `make check` (may fail on pre-existing lint; not in scope) |

## Boundaries

- **In scope:** `AGENTS.md` only
- **Out of scope:** `src/`, `tests/`, `.github/`, CI (BLRID-5), fixing repo-wide lint debt

## Success criteria

- [ ] `AGENTS.md` has **Single-file verification** section
- [ ] Documents `make verify FILE=...`, `ruff check`, `mypy`
- [ ] Examples are valid paths in this repo
- [ ] `make eval-skills` passes
- [ ] Ticket AC in Jira Description satisfied

## Open questions

- None — ticket AC is complete for docs-only MVP.
