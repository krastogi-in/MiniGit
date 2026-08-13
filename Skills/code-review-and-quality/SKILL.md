---
name: code-review-and-quality
description: >-
  Checker skill: five-axis review plus inline code comments for gaps, edge cases,
  and requirement soundness under sdlc-loop. Separate from maker. Honors
  aiagent-need-review-stage feedback. Accumulates sdlc:review; then VERDICT.
---

# Code Review and Quality (checker - inner loop)

Adapted from [code-review-and-quality](https://github.com/addyosmani/agent-skills/blob/main/skills/code-review-and-quality/SKILL.md).

**Role: Checker** -- separate pass from maker. Orchestrated by `sdlc-loop`.

**Label:** `sdlc:review` - **Rubric:** `evals/rubrics/review.md`

## Preconditions

- [ ] Implementation human-approved (label/comment) and status ideally **Review**
- [ ] If `aiagent-ready` or `human-approved` missing -> stop; summary comment; no fake LGTM
- [ ] If **`aiagent-need-review-stage`**: confirm harness stripped stale `human-approved` / `aiagent-approved`; treat human Jira/PR comments as required input; address or file findings; do not treat old approvals as still valid

## Severity taxonomy

Grade every finding by severity. Not everything is a blocker.

| Level | Label | Meaning |
|-------|-------|---------|
| P0 | **BLOCKER** | Must fix before merge -- breaks functionality, data loss, security issue, or violates design contract |
| P1 | **SHOULD FIX** | Significant concern -- pattern violation, missing error handling, missing test coverage |
| P2 | **SUGGESTION** | Improvement opportunity -- readability, naming, minor convention drift |
| P3 | **NOTE** | Observation -- no action required, informational for the author |

## Verdicts

| Verdict | When |
|---------|------|
| **APPROVE** | No P0s, P1s are minor and can ship with follow-up |
| **REQUEST CHANGES** | Any P0, or P1s that meaningfully affect correctness |
| **NEEDS DISCUSSION** | Ambiguity in design or requirements needs human input |

## Deterministic

- [ ] Context from **this issue's** spec/plan + diff (+ PR if present)
- [ ] Tests reviewed; five axes with severity labels (P0-P3)
- [ ] Verification story documented under `agent_space/<ISSUE-KEY>/reviews/` when useful
- [ ] **Inline review comments** (PR review comments and/or review doc with file:line anchors) when:
  - Logic is not validated by tests
  - Requirements / AC paths lack coverage
  - Edge cases, error paths, or abort behavior are missing
  - Sanity/soundness vs the ticket is weak
- [ ] If MiniGit: parameterized SQL, hash/ref validation, no secrets (`AGENTS.md`)

## Output format

When presenting a code review, use:

1. **Verdict** -- APPROVE / REQUEST CHANGES / NEEDS DISCUSSION (bold, prominent)
2. **Summary** -- 2-3 sentence overall assessment
3. **Stats** -- blockers, should-fix, suggestions, notes
4. **Findings table** -- severity, file:line, description (group by severity, blockers first)
5. **Design compliance checklist** -- `[x]` / `[ ]` checkboxes

## Reasoning

Improve code health; high-leverage findings first; propose remedies. Prefer concrete "add test for X" / "handle Y when Z" over vague nits. Be specific -- cite file paths and line numbers.

## Intervention

Critical -> **ESCALATE**.
Feedback label -> incorporate or leave open findings; do not clear `aiagent-need-review-stage` without human/harness agreement.
Otherwise complete review -> `sdlc:review` -> harness **VERDICT**.

## What You Are NOT

- You are NOT the Developer -- don't fix code, only identify issues
- You are NOT the Architect -- don't redesign, review against the existing design
- You are NOT a gatekeeper -- approve when it's good enough, not perfect
- You are NOT a nit-picker -- use P2/P3 for style, not P0

## Jira

On checker pass -> `sdlc:review` (status already Review when possible). `sdlc:done` only after outer-loop ship via `sdlc-loop`.
