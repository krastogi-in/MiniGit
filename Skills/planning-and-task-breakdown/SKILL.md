---
name: planning-and-task-breakdown
description: >-
  Breaks the ticket's spec into agent_space/<ISSUE-KEY>/tasks/plan.md and
  todo.md (inner loop). Feature-agnostic under sdlc-loop. Marks already-covered
  tasks; after pass the harness sets aiagent-ready + In Progress and HUMAN GATE.
  Accumulates sdlc:plan.
---

# Planning and Task Breakdown (inner loop)

Adapted from [planning-and-task-breakdown](https://github.com/addyosmani/agent-skills/blob/main/skills/planning-and-task-breakdown/SKILL.md).
Orchestrated by `sdlc-loop`.

**Label:** `sdlc:plan` - **Rubric:** `evals/rubrics/plan.md`

## Deterministic

- [ ] No feature code in this phase
- [ ] Tasks derived from **this ticket's** approved-path spec (not a canned backlog)
- [ ] Mark tasks **already covered** / partial with "reuse / verify only" vs "build"
- [ ] `agent_space/<ISSUE-KEY>/tasks/plan.md` + `todo.md` with acceptance, verify, files, size
- [ ] Checkpoints every 2-3 tasks; vertical slices; high-risk early
- [ ] Note PR branch will be `aiagent/<ISSUE-KEY>` when implement starts

## Reasoning

Dependency graph from the spec. Discover technical gaps (e.g. schema needs) from the codebase while planning -- still ticket-scoped. Prefer verify-only slices when coverage exists.

## Intervention

After Jira label, return to harness. Harness must:

1. Ensure `aiagent-ready` + status **In Progress** (via `jira-phase-gate`)
2. Issue **HUMAN GATE** -- do **not** start implement until `human-approved` or an `approved` comment

## What You Are NOT

- You are NOT the Developer -- don't write code, produce a plan
- You are NOT the Architect -- don't redesign, plan against the spec
- You are NOT allowed to modify source code in this phase

## Jira

On pass -> `jira-phase-gate` + `sdlc:plan`, then ready-gate handling in `jira-phase-gate` / `sdlc-loop`.
