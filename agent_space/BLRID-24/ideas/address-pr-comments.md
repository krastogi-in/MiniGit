# Idea one-pager — BLRID-24 Address PR Comments

**Issue:** [BLRID-24](https://redhat.atlassian.net/browse/BLRID-24) — Add a feature to address PR comments  
**Source:** Jira summary, description, and acceptance criteria only

## How Might We

How might we let MiniGit users **leave, view, and resolve review-style comments** on commit diffs so they can practice the “address PR feedback” workflow locally—without remotes, GitHub, or merge?

## User & success

| Who | Need | Success |
|-----|------|---------|
| MiniGit learner | Simulate PR review feedback on a diff | Can add a comment on a file/line in a commit diff, see it in CLI or web UI, and mark it addressed |
| SDLC workshop participant | A real product slice tied to “PR comments” wording | `make check` passes; feature verifiable on `aiagent/BLRID-24` |

## Direction

Add a **local review-comments** layer anchored to `(base_commit, head_commit, file_path, line_number)`:

1. **Add** a comment on a diff line between two commits.
2. **List** open comments for a commit pair (or single commit vs parent).
3. **Address** (resolve) a comment by id.

Expose via **CLI** (`comment add|list|address`) and **web UI** on the existing commit-detail diff view. Persist in SQLite (`review_comments` table).

## Assumptions

- “PR comments” means **review feedback on diffs**, not GitHub API integration or remote PRs (MiniGit is local-only per `AGENTS.md` / README).
- Comments anchor to **file path + line number** in the head commit’s diff (same granularity as `get_diffs`).
- MVP uses a single default reviewer identity (`USER` env or `"reviewer"`); no multi-user auth.
- “Address” = mark resolved in DB (soft status); does not auto-edit file content.

## MVP

1. SQLite `review_comments` table + backend CRUD.
2. `Operations.add_review_comment`, `list_review_comments`, `address_review_comment`.
3. CLI: `minigit comment add|list|address`.
4. Web UI: show open comments on commit detail; form to add; button to address.
5. Tests for operations + CLI + one web route smoke test.

## Not doing

- GitHub/GitLab PR API fetch or push.
- Inline reply threads / conversations.
- Suggested code fixes or auto-apply patches.
- Merge, remotes, or tags.
- SDLC-only skills changes (`skills/` factory layer) — ticket targets MiniGit **product** (`src/`).

## Duplicate check

| Key | Summary | Overlap |
|-----|---------|---------|
| — | — | **None found** — JQL for “PR comment” / “address PR” in BLRID returned no matching open tickets besides BLRID-24. |

## Already covered (repo scan)

| Area | Coverage |
|------|----------|
| `src/` product code | **None** — no review-comment tables, ops, CLI, or UI. |
| Diff display | **Partial reuse** — `get_diffs`, commit detail template, unified diff rendering already exist; comments attach to that surface. |
| SDLC `skills/` | **Out of scope** — `sdlc:need-review-stage` / checker skills handle agent PR feedback on real GitHub PRs; not MiniGit VCS behavior. |

## Risks

- Vague AC (“Add a feature to address PR comments”) — human should confirm **local diff comments** interpretation at **HUMAN GATE**.
- Line-number anchoring can drift if commits change — MVP documents “comments tied to commit pair + path + line at creation time”.
