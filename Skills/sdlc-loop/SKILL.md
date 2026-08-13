---
name: sdlc-loop
description: >-
  Orchestrates a feature-agnostic AI SDLC inner loop while keeping the human on
  the outer loop. Use when running the factory on any Jira ticket, for supervised
  autonomy, or to continue until escalate or verdict. Resumes from existing
  sdlc:* / aiagent-* labels; runs phase skills; maker then separate checker;
  pauses on human gates, missing labels, failures, and final verdict.
---

# SDLC Loop Orchestrator

You are the **loop harness**, not the feature author. Keep the human on the **outer loop**; agents run the **inner loop**.

Model: [skills.addy.ie/loops](https://skills.addy.ie/loops/).  
People guide: `docs/ai-sdlc/README.md`. Design: `docs/design/ai-sdlc-loop.md`.

## When to use

- User says: run SDLC loop, supervised build, factory mode, outer-loop mode
- Any Jira issue that should move through AI SDLC phases
- Continue after human unblocks an escalate or adds gate labels

## Inputs

- **Jira issue key** (required) — e.g. `BLRID-123`
- Autonomy: default **supervised**; `interactive` only if user asks

Do **not** assume a specific feature. Read the issue (summary, description, AC, links). All scope comes from the ticket and phase artifacts.

## Run artifacts (`agent_space`)

Write ticket scratch **only** under `agent_space/<ISSUE-KEY>/` — never under product `docs/` or repo-root `tasks/`.

| Phase output | Path |
|--------------|------|
| Idea | `agent_space/<KEY>/ideas/` |
| Spec | `agent_space/<KEY>/specs/` |
| Plan / todo | `agent_space/<KEY>/tasks/` |
| Review notes | `agent_space/<KEY>/reviews/` |

Product code/tests stay in `src/` / `tests/`. People guides stay in `docs/ai-sdlc/`. See `agent_space/README.md`.

## Resume (pluggable start)

**Never re-run finished phases.** On start (and on every resume):

1. Read labels + recent comments.
2. Compute next phase from the highest completed `sdlc:*` progress label (table below).
3. Honor **gate labels** before advancing past plan into maker work.
4. If `aiagent-need-review-stage` is present → prefer **feedback incorporation** (see below) over starting from scratch.
5. Post a short Jira comment: `Resuming at <phase> (labels: …)`.

| Latest progress label | Next skill |
|-----------------------|------------|
| (none) | `idea-refine` |
| `sdlc:ideate` | `spec-driven-development` |
| `sdlc:spec` | `planning-and-task-breakdown` |
| `sdlc:plan` + missing `aiagent-ready` | Finish ready gate (below) — do not implement |
| `sdlc:plan` + `aiagent-ready` + missing `human-approved` | **HUMAN GATE** — stop |
| `sdlc:plan` + `aiagent-ready` + `human-approved` | `incremental-implementation` (maker) |
| `sdlc:implement` | `test-driven-development` |
| `sdlc:test` + awaiting human PR approval | **HUMAN GATE** — stop (keep PR link in summary) |
| `sdlc:test` + human approved implementation | Status → **Review**; then `code-review-and-quality` |
| `sdlc:review` | **VERDICT GATE** → on ship: `sdlc:done` |
| `sdlc:done` | Stop; summarize evidence |
| `sdlc:blocked` | Do not advance; wait for outer-loop instructions |

`human-approved` may be a **label** or a Jira/Cursor comment whose body clearly says `approved` (case-insensitive) for the current gate.

## Label + status contract

| Event | Labels (accumulate) | Status |
|-------|---------------------|--------|
| Each phase rubric pass | matching `sdlc:*` | — |
| Ideate + spec + plan all present | add **`aiagent-ready`** | **In Progress** |
| Human accepts plan (label or “approved” comment) | add **`human-approved`** if missing | stay In Progress |
| Maker finishes slices + opens PR | add **`aiagent-approved`** | stay In Progress |
| Human accepts implementation / PR | keep approvals; note in comment | **Review** (or closest available) |
| Checker pass | `sdlc:review` | Review |
| Human wants more agent work on feedback | add **`aiagent-need-review-stage`**; **agent removes** `human-approved` and `aiagent-approved` (stale approvals) | Review |
| Feedback addressed + human re-approves | restore **`human-approved`** (label or `approved` comment); agent removes **`aiagent-need-review-stage`** after confirm | Review / In Progress as appropriate |
| Escalate | `sdlc:blocked` | — |
| Ship verdict | `sdlc:done` | optional Closed if workflow allows |

**Exception to accumulate-only:** gate approvals are revoked automatically when feedback starts (see below). Progress `sdlc:*` labels are never stripped.

### Hard stop (missing gates)

Before **any** maker work (`incremental-implementation` / code commits for the ticket):

- Require **`aiagent-ready`** and **`human-approved`**.
- If either is missing → **do not implement**. Post a Jira **summary comment** (what is done, what is blocked, how to unblock) and stop for the outer loop.

### Status transitions

Use `getTransitionsForJiraIssue` + `transitionJiraIssue`. Match by destination **name** (case-insensitive):

- Prefer exact: `In Progress`, `Review`
- Aliases for Review: `In Review`, `Code Review`, `Peer Review`
- If the workflow lacks the target status: post a comment explaining the miss; do **not** fake success; continue phase work unless the skill says otherwise

## Boot checks (every start / resume)

1. **Duplicates** — JQL search same project for similar summary/keywords; if likely duplicates, **highlight** in a Jira comment (keys + why) before continuing. Do not auto-close others.
2. **Already covered** — skim repo for existing behavior matching the ticket; note full/partial coverage in phase artifacts and a short comment so later phases can narrow or skip work.
3. **Feedback flag** — if `aiagent-need-review-stage` is present (or just added):
   - Via `jira-phase-gate`: **remove** `human-approved` and `aiagent-approved` immediately (do not wait for the human to do this).
   - Keep `aiagent-ready` and all `sdlc:*` progress labels.
   - Collect human comments (Jira + PR), incorporate (plan refine and/or code), re-verify.
   - Stop for **HUMAN GATE** again until `human-approved` / `approved` returns.
   - After re-approval: remove `aiagent-need-review-stage` and comment evidence (agent does this — human need not edit labels by hand).

## Inner loop (without asking each step)

For each phase until gate/escalate:

1. Load phase skill from `Skills/<name>/SKILL.md`
2. Ground work in **this issue** + repo conventions (`AGENTS.md` if changing MiniGit)
3. Deterministic checks → reasoning → rubric
4. On pass → `jira-phase-gate` (comment + accumulate label; status when required)
5. On fail → one mechanical retry if obvious; else **ESCALATE**

After **human-approved** plan gate, continue maker tasks without pausing between slices (supervised). Still open the PR and wait for human before Review status / checker.

## Outer-loop packets

### HUMAN GATE (plan / PR)

Replaces casual chat approvals. Prefer Jira labels.

```markdown
## OUTER LOOP — HUMAN GATE
Issue: <KEY>
Stage: <plan | implementation-PR>
Evidence: <artifact paths and/or PR URL>
Labels now: …
Unblock: add label `human-approved` OR comment `approved`
(For plan stage, `aiagent-ready` must already be present.)
```

### ESCALATE

```markdown
## OUTER LOOP — ESCALATE
Issue: <KEY>
Phase: …
Trigger: <deterministic|verify|ask-first|checker-critical|connector|product|missing-gate>
Evidence: …
Tried: …
Ask: redirect / fix constraint / abort
Action: accumulate sdlc:blocked + comment
```

### VERDICT

```markdown
## OUTER LOOP — VERDICT
Issue: <KEY>
Evidence: diff summary, PR, verify commands, review checklist
Ask: ship | block | redirect | narrow
On ship: jira-phase-gate → sdlc:done
```

### FEEDBACK (`aiagent-need-review-stage`)

```markdown
## OUTER LOOP — FEEDBACK INCORPORATION
Issue: <KEY>
Sources: Jira comments + PR review threads
Agent already: removed human-approved + aiagent-approved (stale)
Action: address feedback; re-verify; comment evidence
Unblock: human re-adds human-approved OR comments approved
Then agent: removes aiagent-need-review-stage
```

### PLAN REFINE (human comments before implement)

If `aiagent-ready` is set and the human comments changes (not yet `approved`):

1. Update `agent_space/<ISSUE-KEY>/tasks/plan.md` / `todo.md` (and spec/idea only if comments require it).
2. Comment what changed; keep `aiagent-ready`; do **not** invent `human-approved`.
3. Re-issue **HUMAN GATE** until approval.

## Maker ≠ checker

- Maker: `incremental-implementation` (+ TDD as needed); branch/PR `aiagent/<ISSUE-KEY>`
- Checker: separate pass with **only** `code-review-and-quality` (inline findings)
- Never self-LGTM in the maker pass

## Autonomy rungs

| Rung | Behavior |
|------|----------|
| Supervised (default) | Human gates + escalate + verdict |
| Interactive | Also pause after each phase |
| Unattended | Forbidden in v1 |

## Related

- `Skills/REGISTRY.md` · `Skills/jira-phase-gate/SKILL.md` · `evals/rubrics/loop.md`
