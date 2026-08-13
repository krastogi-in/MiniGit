# Handoff: {Feature Name}

## Status: {READY FOR IMPLEMENTATION | IN PROGRESS | READY FOR REVIEW | CHANGES REQUESTED | APPROVED | DONE}
## Issue: {ISSUE-KEY}
## Feature: {feature-slug}

---

## Architect (idea + spec + plan)
- **Idea:** `agent_space/{ISSUE-KEY}/ideas/{slug}.md`
- **Spec:** `agent_space/{ISSUE-KEY}/specs/{slug}.md`
- **Plan:** `agent_space/{ISSUE-KEY}/tasks/plan.md`
- **Todo:** `agent_space/{ISSUE-KEY}/tasks/todo.md`
- **Approved:** {date or pending}
- **Start with:** Phase 1, Tasks {task-ids}
- **Total phases:** {N}

## Developer (maker)
- **Branch:** `aiagent/{ISSUE-KEY}`
- **Current phase:** {Phase N of M}
- **Commits:**
  - {sha} — {one-line message} (Phase N)
- **PR:** #{number}
- **Phase reports:**
  - `agent_space/{ISSUE-KEY}/reports/PHASE_{N}_REPORT.md`
- **Validation evidence:**
  - `make check` — {PASS/FAIL}
  - Smoke test — {summary}

## Reviewer (checker)
- **Review:** `agent_space/{ISSUE-KEY}/reviews/{slug}.md`
- **Verdict:** {APPROVE | REQUEST CHANGES | pending}
- **Reviewed:** {date or pending}
- **Findings:** {N blockers, N should-fix, N suggestions}
- **Changes requested:** {summary if applicable}

## Investigator (if applicable)
- **RCA:** `agent_space/{ISSUE-KEY}/investigations/{slug}.md`
- **Root cause:** {one-line summary}
- **Fix status:** {pending | handed to maker}
