# Example only: Merge feature (not part of the factory)

This folder is an **optional sample** of what a *ticket-driven* run might produce for one MiniGit feature.  
The AI SDLC skills do **not** hardcode Merge. Use a real BLRID issue + `sdlc-loop` for live work.

## Sample intent (if you filed such a ticket)

Implement branch merge in MiniGit:

- Fast-forward when possible; otherwise a merge commit with **two parents**
- On content conflict: **abort and report** (no textual merge)
- Surfaces: **CLI + Flask**
- Verify with project tests; define any perf expectations **in the ticket/spec**, not in skills

## Where real artifacts would live after a loop run

| Artifact | Typical path |
|----------|----------------|
| Idea one-pager | `docs/ideas/…` |
| Feature spec | `docs/specs/merge-feature.md` (created by spec skill) |
| Plan / tasks | `tasks/` (from plan skill; issue-scoped) |
| Code / tests | `src/`, `tests/` |

## Note on two parents

MiniGit today stores a single `parent_hash`. A Merge **feature** ticket would discover that in the spec/plan and schedule a schema task. That discovery is ticket-specific — not a registry requirement.
