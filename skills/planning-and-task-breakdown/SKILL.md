---
name: planning-and-task-breakdown
description: >-
  Breaks the ticket’s spec into agent_space/<ISSUE-KEY>/tasks/plan.md and
  todo.md (inner loop). Feature-agnostic under sdlc-loop. After pass: harness
  sets sdlc:agent-ready, posts idea/spec/tasks as a Jira comment (never
  overwrites Description), In Progress, then HUMAN GATE. Accumulates sdlc:plan.
---

# Planning and Task Breakdown (inner loop)

Adapted from [planning-and-task-breakdown](https://github.com/addyosmani/agent-skills/blob/main/skills/planning-and-task-breakdown/SKILL.md).  
Orchestrated by `sdlc-loop`.

**Label:** `sdlc:plan` · **Rubric:** `evals/rubrics/plan.md`

## Deterministic

- [ ] No feature code in this phase
- [ ] Tasks derived from **this ticket’s** approved-path spec (not a canned backlog)
- [ ] Mark tasks **already covered** / partial with “reuse / verify only” vs “build”
- [ ] `agent_space/<ISSUE-KEY>/tasks/plan.md` + `todo.md` with acceptance, verify, files, size
- [ ] Checkpoints every 2–3 tasks; vertical slices; high-risk early
- [ ] Note PR branch will be `aiagent/<ISSUE-KEY>` when implement starts

## Reasoning

Dependency graph from the spec. Discover technical gaps (e.g. schema needs) from the codebase while planning — still ticket-scoped. Prefer verify-only slices when coverage exists.

## Intervention

After Jira label, return to harness. Harness / `jira-phase-gate` must:

1. Ensure `sdlc:agent-ready` + status **In Progress**
2. Post **SDLC review package** as a **Jira comment** (idea + spec + plan/tasks) — **do not overwrite Description**
3. Issue **HUMAN GATE** — do **not** start implement until `sdlc:human-ready` or an `approved` comment

## Jira

On pass → `jira-phase-gate` + `sdlc:plan`, then ready-gate handling in `jira-phase-gate` / `sdlc-loop`.
