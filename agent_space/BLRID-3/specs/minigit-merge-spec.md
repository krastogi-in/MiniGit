# BLRID-3 Spec: MiniGit Branch Merge

## Assumptions
- Scope source is only the BLRID-3 issue text provided in chat.
- Duplicate Jira ticket validation is pending external Jira search (blocked in this runtime).
- Existing codebase is authoritative for implementation constraints in `AGENTS.md`.
- Merge is performed against the currently active branch in `Operations` as target.

## Objective
Add a merge capability that integrates a source branch/ref into the current branch, supporting:
1. Already up to date (no-op),
2. Fast-forward update (no merge commit),
3. Diverged true merge commit with two parents,
while failing safely for missing refs and conflicts.

## Commands / Surfaces
- **CLI:** `minigit merge <source_branch>`
  - Merges `<source_branch>` into current branch.
  - Prints outcome: already-up-to-date, fast-forward, or merge commit hash.
- **Flask UI:** Add merge action in repo view using source branch selection.
  - Calls same backend merge method and shows flash success/error.

## Structure

### Backend Data Model
- Extend commit persistence to support a second parent for merge commits.
- Backward compatibility: non-merge commits keep second parent empty/null.

### Frontend Operations API
- New public method, for example:
  - `merge(source_ref: str, author: str | None = None, message: str | None = None) -> dict[str, str]`
- Responsibilities:
  - Resolve and validate source ref/commit.
  - Determine relation between target HEAD and source tip.
  - Execute one of:
    - already-up-to-date
    - fast-forward
    - true merge commit
  - Ensure atomic safety: if error/conflict, target ref remains unchanged.

### Merge Algorithm (Simplified 3-way by file hash)
1. Resolve `target_head` and `source_head`.
2. Compute merge base via ancestor walk.
3. Case handling:
   - If `source_head` ancestor of `target_head` -> already-up-to-date.
   - If `target_head` ancestor of `source_head` -> fast-forward target ref to source.
   - Else diverged -> three-way merge required.
4. For diverged merge:
   - Flatten trees for base, target, source.
   - For each path compare `(base, target, source)` blob hashes:
     - only source changed -> take source
     - only target changed -> keep target
     - both changed to same hash -> take that hash
     - both changed differently (including delete-vs-modify) -> conflict
   - Any conflict -> abort with clear error, no ref update.
   - No conflict -> write merged tree, create commit with two parents `(target_head, source_head)`, update target ref.

## Error and Safety Rules
- Missing source ref/commit -> `ValueError` with explicit message.
- Invalid ancestry/base resolution -> explicit failure.
- Conflict -> explicit failure listing conflicting paths (or first conflict), and no target ref change.
- No partial write to refs on failure.

## Style / Constraints
- Keep layer boundaries from `AGENTS.md`:
  - backend holds persistence only,
  - merge orchestration in frontend operations,
  - CLI/app call frontend only.
- Use parameterized SQL only.
- Preserve 64-char lowercase hash and ref-name validation.

## Testing
- Add/extend tests under `tests/`:
  - FF merge path.
  - Diverged clean merge -> two-parent commit and updated tip.
  - Missing source ref -> error and unchanged tip.
  - Conflict abort -> unchanged tip.
  - Already-up-to-date detection.
  - CLI route path for merge command behavior.
  - Flask route uses same operations behavior.

## Boundaries / Non-goals
- No interactive/manual conflict resolution editor.
- No auto line merge conflict resolution.
- No additional third-party dependencies.

## Success Criteria (Mapped to AC)
- `minigit merge <branch>` works for FF and diverged merge commit.
- Missing/unknown source produces clear error and no ref mutation.
- Conflict abort keeps tip unchanged.
- Clean diverged merge creates two-parent commit and updates target branch.
- FF path avoids unnecessary merge commit.
- Already-up-to-date message returned.
- Flask merge path triggers same logic.
- `make check` passes.

## Open Questions
- Should source accept only branch names, or any ref/hash as goal text suggests?
- How should merge commit message default be formatted (`Merge branch '<src>' into '<target>'`)?
- Should conflict output include all paths or only first for MVP?
