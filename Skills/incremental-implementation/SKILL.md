---
name: incremental-implementation
description: >-
  Maker skill: thin vertical slices from the human-approved plan under sdlc-loop.
  Requires aiagent-ready + human-approved. Opens PR on aiagent/<ISSUE-KEY>, sets
  aiagent-approved. Feature-agnostic; escalates on verify failure or ask-first.
  Accumulates sdlc:implement.
---

# Incremental Implementation (maker · inner loop)

Adapted from [incremental-implementation](https://github.com/addyosmani/agent-skills/blob/main/skills/incremental-implementation/SKILL.md).

**Role: Maker** — never run checker in this pass. Orchestrated by `sdlc-loop`.

**Label:** `sdlc:implement` · **Rubric:** `evals/rubrics/implement.md`

## Gate (fail closed)

Before any product code for this ticket:

- [ ] Labels include **`aiagent-ready`** and **`human-approved`** (or harness confirmed an `approved` comment and applied `human-approved`)
- [ ] If either missing → stop; ask harness to post missing-gate summary — **do not code**

Also check for **`aiagent-approved`** only as “agent already marked ready”: if present with an open PR, prefer resume/fixup over a second PR unless human asks.

## Deterministic

- [ ] Only items from the approved plan/todo for **this issue** (skip or verify-only for already-covered tasks)
- [ ] Work on branch **`aiagent/<ISSUE-KEY>`** (create from default branch if needed)
- [ ] After each slice: relevant verifies; before done: project check command (MiniGit: `make check`)
- [ ] Scope discipline; follow `AGENTS.md` when editing MiniGit
- [ ] Open / update a **GitHub PR** from that branch for human review (`gh pr create` when ready)
- [ ] Commit only when user/harness policy allows

## Reasoning

Simplest correct slice for the planned tasks. Call out reused existing code in PR description.

## After slices + green verify

1. Ensure PR exists and links the Jira key
2. Via `jira-phase-gate`: accumulate **`sdlc:implement`** and **`aiagent-approved`**
3. Comment PR URL + ask human to review; **do not** move status to Review yourself until human approves implementation
4. Hand back to harness for **HUMAN GATE** (implementation)

## Intervention

Continue tasks only after plan human gate. Escalate on red verify after retry, ask-first boundaries, or product ambiguity beyond the ticket. If `aiagent-need-review-stage` appears mid-flight, pause new scope and incorporate feedback first.
