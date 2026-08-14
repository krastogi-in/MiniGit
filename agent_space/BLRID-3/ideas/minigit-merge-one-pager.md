# BLRID-3 Idea One-Pager: MiniGit Merge

## Issue
- **Key:** `BLRID-3`
- **Summary:** feat: MiniGit merge - merge one branch into another
- **Source of scope:** User-provided Jira issue text in chat (summary/background/goal/AC/non-goals).

## Duplicate Ticket Check (Early)
- **Result:** Not fully verifiable from this runtime because Jira search APIs/connectivity are unavailable.
- **Risk callout:** A duplicate may exist in project `BLRID` for "merge", "fast-forward", or "two-parent commit".
- **Human follow-up:** Run a Jira JQL search for open/recent issues with those terms and link any overlaps before implementation lands.

## Already Covered in Code (Early)
- **Covered foundations (reuse):**
  - Branch creation, checkout, refs, commits, and history traversal exist in `src/frontend/operations.py`.
  - Diffing and tree/blob persistence already exist.
  - CLI and Flask wiring patterns exist for adding new commands/routes.
- **Not covered (build required):**
  - No merge operation in `Operations`.
  - Commit storage currently supports one parent only (`parent_hash`), but AC requires two-parent merge commits.
  - No CLI `merge` command and no Flask merge action.
  - No merge-focused tests.

## How Might We
How might we add a safe branch merge flow that supports fast-forward and true two-parent merge commits, while aborting on content conflicts and leaving refs unchanged on failure?

## User / Job
As a MiniGit user, I want to merge a source branch into the currently checked-out branch so I can integrate work without manually replaying commits.

## Success Criteria (from AC)
- `minigit merge <branch>` merges into current HEAD branch using:
  - fast-forward when current is ancestor of source
  - two-parent commit when histories diverged and conflict-free
- Missing source/ref errors are explicit; no partial updates.
- Conflicts abort merge; current tip unchanged.
- Already-up-to-date is detected and reported.
- Flask UI invokes the same backend behavior.
- Tests cover FF, diverged merge commit, missing ref, conflict abort, already-up-to-date.

## Direction
- Implement merge logic once in `Operations` and call it from both CLI and Flask.
- Use ancestry analysis via commit parent links to find merge base and relation cases.
- For diverged histories, perform a simplified file-level three-way merge by blob hash, with conflict detection and abort-only behavior.
- Extend commit persistence to represent two parents for merge commits.

## Assumptions
- "Current branch" means `Operations.branch` (active branch in current process/session).
- Ref input is a branch name initially; extend to commit hash/ref aliases only if needed by scope.
- No working-tree auto-edit or interactive resolution is required.

## MVP
1. Core merge operation with relation detection and guardrails.
2. Fast-forward + already-up-to-date handling.
3. Diverged merge commit with two parent pointers.
4. Conflict detection/abort with no ref mutation.
5. CLI + Flask integration and required tests.

## Not Doing
- Textual line-level auto-merge conflict resolution.
- Rebasing, squash merges, octopus merges, or full Git parity.
- New third-party dependencies.
