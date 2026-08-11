---
name: test-driven-development
description: >-
  Inner-loop TDD under sdlc-loop: RED-GREEN-REFACTOR and prove-it for bugs.
  Feature-agnostic; uses the repository’s test commands. Accumulates sdlc:test.
  Escalates if the suite stays red. Perf gates only if the ticket/spec defines them.
---

# Test-Driven Development (inner loop)

Adapted from [test-driven-development](https://github.com/addyosmani/agent-skills/blob/main/skills/test-driven-development/SKILL.md).  
Orchestrated by `sdlc-loop`.

**Label:** `sdlc:test` · **Rubric:** `evals/rubrics/test.md`

## Deterministic

- [ ] Discover stack first (MiniGit: `make test` / pytest / `tmp_path`)
- [ ] RED → GREEN → REFACTOR; bug fixes prove-it first
- [ ] No network; isolate fixtures per project norms
- [ ] Full suite green before claiming phase done
- [ ] Apply **perf (or other) gates only if the ticket/spec states them**

## Reasoning

Test state not interactions; prefer real implementations over mocks.

## Intervention

Escalate if required verifies stay red. Green/red oracles may stay lights-out ([loops](https://skills.addy.ie/loops/)).

## Jira

On pass → `jira-phase-gate` + `sdlc:test`.
