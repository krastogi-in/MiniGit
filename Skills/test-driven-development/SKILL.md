---
name: test-driven-development
description: >-
  Inner-loop TDD under sdlc-loop: RED-GREEN-REFACTOR and prove-it for bugs.
  Feature-agnostic; uses the repository’s test commands. Runs on branch
  aiagent/<ISSUE-KEY> after sdlc:human-ready plan. Accumulates sdlc:test.
  Escalates if the suite stays red. Perf gates only if the ticket/spec defines them.
---

# Test-Driven Development (inner loop)

Adapted from [test-driven-development](https://github.com/addyosmani/agent-skills/blob/main/skills/test-driven-development/SKILL.md).  
Orchestrated by `sdlc-loop`.

**Label:** `sdlc:test` · **Rubric:** `evals/rubrics/test.md`

## Deterministic

- [ ] Confirm maker gates still hold (`sdlc:agent-ready`, `sdlc:human-ready`) — else stop
- [ ] Discover stack first (MiniGit: `make test` / pytest / `tmp_path`)
- [ ] RED → GREEN → REFACTOR; bug fixes prove-it first
- [ ] Cover gaps called out as already-partial or risk areas in plan/spec
- [ ] No network; isolate fixtures per project norms
- [ ] Full suite green before claiming phase done
- [ ] Apply **perf (or other) gates only if the ticket/spec states them**
- [ ] Keep work on **`aiagent/<ISSUE-KEY>`** and push so the PR stays current

## Reasoning

Test state not interactions; prefer real implementations over mocks.

## Intervention

Escalate if required verifies stay red. Green/red oracles may stay lights-out ([loops](https://skills.addy.ie/loops/)).

## Jira

On pass → `jira-phase-gate` + `sdlc:test`. Human still reviews the PR before status **Review** / checker if not already approved.
