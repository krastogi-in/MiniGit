---
name: spec-driven-development
description: >-
  Writes a feature-agnostic spec from a Jira ticket before code (inner-loop
  design). Use under sdlc-loop after ideate. Notes already-covered areas and
  duplicate-ticket risks. Accumulates sdlc:spec. Escalates only on failure or
  ask-first boundaries.
---

# Spec-Driven Development (inner loop)

Adapted from [spec-driven-development](https://github.com/addyosmani/agent-skills/blob/main/skills/spec-driven-development/SKILL.md).
Orchestrated by `sdlc-loop`.

**Label:** `sdlc:spec` - **Rubric:** `evals/rubrics/spec.md`

## Deterministic

- [ ] Scope taken from the Jira issue (+ idea one-pager if present)
- [ ] Reaffirm **already covered** / partial coverage in ASSUMPTIONS or Boundaries (reuse vs build)
- [ ] If duplicates were flagged at ideate, reference them and avoid contradictory design
- [ ] ASSUMPTIONS listed before body; wait for corrections only via escalate/plan later
- [ ] Objective, Commands, Structure, Style, Testing, Boundaries, Success, Open Questions
- [ ] Saved under `agent_space/<ISSUE-KEY>/specs/` (name from ticket slug)
- [ ] If changing Project: include `make` commands and `AGENTS.md` constraints

## Reasoning

SPECIFY before PLAN. Reframe vague AC as testable success criteria. Do not bake in unrelated example features. Shrink Success Criteria when the codebase already satisfies parts of the ticket.

## Intervention

Escalate only. Human approval of *plan* is **HUMAN GATE** in `sdlc-loop` (after `aiagent-ready`).

## What You Are NOT

- You are NOT the Planner -- produce a spec, not a task breakdown
- You are NOT the Developer -- don't write code or implementation details
- You are NOT the Reviewer -- don't critique existing code quality
- You are NOT allowed to modify source code

## Jira

On pass -> `jira-phase-gate` + `sdlc:spec`.
