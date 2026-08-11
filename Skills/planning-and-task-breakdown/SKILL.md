---
name: planning-and-task-breakdown
description: >-
  Breaks the ticket’s spec into tasks/plan.md and tasks/todo.md (inner loop).
  Feature-agnostic under sdlc-loop. Accumulates sdlc:plan; harness then issues
  PLAN GATE to the outer loop.
---

# Planning and Task Breakdown (inner loop)

Adapted from [planning-and-task-breakdown](https://github.com/addyosmani/agent-skills/blob/main/skills/planning-and-task-breakdown/SKILL.md).  
Orchestrated by `sdlc-loop`.

**Label:** `sdlc:plan` · **Rubric:** `evals/rubrics/plan.md`

## Deterministic

- [ ] No feature code in this phase
- [ ] Tasks derived from **this ticket’s** approved-path spec (not a canned backlog)
- [ ] `tasks/plan.md` + `tasks/todo.md` with acceptance, verify, files, size
- [ ] Checkpoints every 2–3 tasks; vertical slices; high-risk early

## Reasoning

Dependency graph from the spec. Discover technical gaps (e.g. schema needs) from the codebase while planning — still ticket-scoped.

## Intervention

After Jira label, return to harness for **PLAN GATE**. Do not start implement.

## Jira

On pass → `jira-phase-gate` + `sdlc:plan`.
