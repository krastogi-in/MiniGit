---
name: code-review-and-quality
description: >-
  Checker skill: five-axis review plus inline code comments for gaps, edge cases,
  and requirement soundness under sdlc-loop. Separate from maker. Honors
  sdlc:need-review-stage feedback. Accumulates sdlc:review; then VERDICT.
---

# Code Review and Quality (checker · inner loop)

Adapted from [code-review-and-quality](https://github.com/addyosmani/agent-skills/blob/main/skills/code-review-and-quality/SKILL.md).

**Role: Checker** — separate pass from maker. Orchestrated by `sdlc-loop`.

**Label:** `sdlc:review` · **Rubric:** `evals/rubrics/review.md`

## Preconditions

- [ ] Implementation sdlc:human-ready (label/comment) and status ideally **Review**
- [ ] If `sdlc:agent-ready` or `sdlc:human-ready` missing → stop; summary comment; no fake LGTM
- [ ] If **`sdlc:need-review-stage`**: confirm harness stripped stale `sdlc:human-ready` / `sdlc:agent-approved`; treat human Jira/PR comments as required input; address or file findings; do not treat old approvals as still valid

## Deterministic

- [ ] Context from **this issue’s** spec/plan + diff (+ PR if present)
- [ ] Tests reviewed; five axes with severity labels
- [ ] Verification story documented under `agent_space/<ISSUE-KEY>/reviews/` when useful
- [ ] **Inline review comments** (PR review comments and/or review doc with file:line anchors) when:
  - Logic is not validated by tests
  - Requirements / AC paths lack coverage
  - Edge cases, error paths, or abort behavior are missing
  - Sanity/soundness vs the ticket is weak
- [ ] If MiniGit: parameterized SQL, hash/ref validation, no secrets (`AGENTS.md`)

## Reasoning

Improve code health; high-leverage findings first; propose remedies. Prefer concrete “add test for X” / “handle Y when Z” over vague nits.

## Intervention

Critical → **ESCALATE**.  
Feedback label → incorporate or leave open findings; do not clear `sdlc:need-review-stage` without human/harness agreement.  
Otherwise complete review → `sdlc:review` → harness **VERDICT**.

## Jira

On checker pass → `sdlc:review` (status already Review when possible). `sdlc:done` only after outer-loop ship via `sdlc-loop`.
