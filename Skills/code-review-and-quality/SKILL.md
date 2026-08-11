---
name: code-review-and-quality
description: >-
  Checker skill: five-axis review in a separate pass from the maker under
  sdlc-loop. Feature-agnostic. Accumulates sdlc:review; harness then issues
  VERDICT to the outer loop. Escalates on Critical findings.
---

# Code Review and Quality (checker · inner loop)

Adapted from [code-review-and-quality](https://github.com/addyosmani/agent-skills/blob/main/skills/code-review-and-quality/SKILL.md).

**Role: Checker** — separate pass from maker. Orchestrated by `sdlc-loop`.

**Label:** `sdlc:review` · **Rubric:** `evals/rubrics/review.md`

## Deterministic

- [ ] Context from **this issue’s** spec/plan + diff
- [ ] Tests reviewed; five axes with severity labels
- [ ] Verification story documented
- [ ] If MiniGit: parameterized SQL, hash/ref validation, no secrets (`AGENTS.md`)

## Reasoning

Improve code health; high-leverage findings first; propose remedies.

## Intervention

Critical → **ESCALATE**. Otherwise complete review → `sdlc:review` → harness **VERDICT**.

## Jira

On checker pass → `sdlc:review`. `sdlc:done` only after outer-loop ship via `sdlc-loop`.
