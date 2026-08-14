# Idea: AI-Powered Commit Message Assistant

**Issue:** [BLRID-19](https://redhat.atlassian.net/browse/BLRID-19)
**Phase:** ideate

## How Might We

How might we help MiniGit users write better, consistent commit messages
without the cognitive overhead of analyzing their own changes?

## User

MiniGit CLI and web UI users who stage files and create commits. They want
fast, conventional-commit-formatted messages that accurately describe their
changes.

## Success Criteria

- Users get a suggested commit message from staged diffs with one command/click
- Messages follow `type: subject` conventional commit format
- The suggestion is editable before commit (not auto-committed)
- Works seamlessly with the existing stage → commit flow

## Direction

Add a **commit message generator** module in `src/frontend/` that:

1. Computes a diff between the current HEAD tree and staged changes
2. Analyzes file paths, change patterns (add/delete/modify), and content
3. Produces a conventional-commit message via heuristics (MVP) with optional
   LLM integration as a stretch goal

Expose through:
- **CLI:** New `commit` subcommand with `--ai` flag (note: `commit` doesn't exist yet)
- **Web UI:** "Suggest message" button on the commit/staging page

## Assumptions

- Diffs are computable from staged entries vs HEAD tree (infrastructure exists
  in `Operations.get_diffs` and `_flatten_tree`)
- MVP uses rule-based/template heuristics (no external API dependency)
- The CLI currently lacks a `commit` subcommand — we must add it
- Conventional commit types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`

## MVP Scope

1. `CommitMessageGenerator` class in `src/frontend/commit_assistant.py`
   - Input: list of staged changes (path, action, old/new content)
   - Output: suggested commit message string
   - Heuristic: classify by file extension/path → pick type; summarize changes → subject
2. CLI `commit` command with `-m` (manual) and `--ai` (generated) flags
3. Web UI `/repo/<name>/suggest-message` API endpoint + button
4. Unit tests for generator logic and integration

## Not Doing (v1)

- LLM/API-based generation (stretch goal only)
- Multi-line commit body generation
- Git trailers or co-author handling
- Amend or interactive rebase
- Commit signing

## Existing Coverage

- **None.** No commit message generation code exists in the repo.
- The CLI has no `commit` subcommand (only web UI `POST /repo/<name>/commit`).
- Diff computation infrastructure exists and can be reused.
- The `Operations.create_new_commit(message, author)` method is the commit
  entry point in the frontend layer.

## Duplicates Check

- BLRID-17 (per-file commit history) — different scope (read-only log feature)
- BLRID-16 (interactive commit graph) — different scope (visualization)
- **No duplicates found.**

## Risks

- Heuristic message quality may be low for complex multi-file changes
  → Mitigation: user always reviews/edits before committing
- Adding the CLI `commit` subcommand is prerequisite work not in the original
  ticket scope but necessary for the `--ai` flag
  → Mitigation: treat as part of the feature (CLI commit is implied by the AC)
