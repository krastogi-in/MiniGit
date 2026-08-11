---
name: spec-driven-development
description: >-
  Writes a feature-agnostic spec from a Jira ticket before code (inner-loop
  design). Use under sdlc-loop after ideate. Accumulates sdlc:spec. Escalates
  only on failure or ask-first boundaries.
---

# Spec-Driven Development (inner loop)

Adapted from [spec-driven-development](https://github.com/addyosmani/agent-skills/blob/main/skills/spec-driven-development/SKILL.md).  
Orchestrated by `sdlc-loop`.

**Label:** `sdlc:spec` · **Rubric:** `evals/rubrics/spec.md`

## Deterministic

- [ ] Scope taken from the Jira issue (+ idea one-pager if present)
- [ ] ASSUMPTIONS listed before body; wait for corrections only via escalate/plan later
- [ ] Objective, Commands, Structure, Style, Testing, Boundaries, Success, Open Questions
- [ ] Saved under `docs/specs/` (name from ticket slug)
- [ ] If changing MiniGit: include `make` commands and `AGENTS.md` constraints

## Reasoning

SPECIFY before PLAN. Reframe vague AC as testable success criteria. Do not bake in unrelated example features.

## Intervention

Escalate only. Human approval of *plan* is **PLAN GATE** in `sdlc-loop`.

## Jira

On pass → `jira-phase-gate` + `sdlc:spec`.
