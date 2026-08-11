---
name: incremental-implementation
description: >-
  Maker skill: thin vertical slices from the approved plan under sdlc-loop.
  Feature-agnostic; continues after plan gate; escalates on verify failure or
  ask-first boundaries. Accumulates sdlc:implement.
---

# Incremental Implementation (maker · inner loop)

Adapted from [incremental-implementation](https://github.com/addyosmani/agent-skills/blob/main/skills/incremental-implementation/SKILL.md).

**Role: Maker** — never run checker in this pass. Orchestrated by `sdlc-loop`.

**Label:** `sdlc:implement` · **Rubric:** `evals/rubrics/implement.md`

## Deterministic

- [ ] Only items from the approved plan/todo for **this issue**
- [ ] After each slice: relevant verifies; before done: project check command (MiniGit: `make check`)
- [ ] Scope discipline; follow `AGENTS.md` when editing MiniGit
- [ ] Commit only when user/harness policy allows

## Reasoning

Simplest correct slice for the planned tasks.

## Intervention

Continue tasks after plan approval. Escalate on red verify after retry, ask-first boundaries, or product ambiguity beyond the ticket.

## Jira

When plan slices complete + verify green → `jira-phase-gate` + `sdlc:implement`.
