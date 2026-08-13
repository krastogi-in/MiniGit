---
name: jira-phase-gate
description: >-
  Updates Jira issues used as SDLC state DB: posts evidence comments, accumulates
  sdlc:* labels (progress + gates), and transitions status (In Progress / Review).
  Feature-agnostic. Use after a phase rubric passes, on human gates, escalate,
  feedback, or when sdlc-loop advances fingerprints. Never overwrite the original
  issue Description with idea/spec/plan — post those as comments.
---

# Jira Phase Gate

State backend for `sdlc-loop`. Labels = progress + gates; comments = evidence;
status = workflow visibility. Works for **any** issue key.

## Deterministic layer (fail closed)

- [ ] Rubric pass **or** explicit gate/escalate/verdict/feedback action from `sdlc-loop`
- [ ] Issue key known
- [ ] Atlassian MCP available — else ESCALATE (connector); never fake an update
- [ ] Phase label ∈ `sdlc:ideate|spec|plan|implement|test|review|done|blocked` when advancing a phase
- [ ] Gate labels when required ∈ `sdlc:agent-ready|sdlc:human-ready|sdlc:agent-approved|sdlc:need-review-stage`
- [ ] Do **not** replace the ticket’s original Description with SDLC artifacts

## Label families

| Family | Examples | Rule |
|--------|----------|------|
| Progress | `sdlc:ideate` … `sdlc:done`, `sdlc:blocked` | **Accumulate**; never strip these |
| Gates | `sdlc:agent-ready`, `sdlc:human-ready`, `sdlc:agent-approved`, `sdlc:need-review-stage` | Accumulate when set; **exception:** on feedback start, strip stale `sdlc:human-ready` / `sdlc:agent-approved`. Never invent `sdlc:human-ready` |

## Status map (discover transitions each time)

| When | Target status name |
|------|--------------------|
| After ideate+spec+plan → `sdlc:agent-ready` | **In Progress** |
| After human approves implementation / PR (enter checker) | **Review** (aliases: In Review, Code Review, Peer Review) |

Steps:

1. `getTransitionsForJiraIssue`
2. Pick transition whose `to.name` matches target (case-insensitive) or alias list
3. `transitionJiraIssue` with that id
4. If missing: comment `Status <X> unavailable in workflow; left at <current>` — do not fail the whole phase solely for this

## Steps (typical phase advance)

1. Discover Atlassian MCP tools; authenticate if needed.
2. Read issue labels + status (state).
3. Post comment (`Skills/_templates/phase-comment.md`, gate packet, or escalate packet).
4. **Accumulate** required labels — never strip prior `sdlc:*`. Strip gate approvals only per **Feedback revocation** below.
5. Apply status transition when the contract says so.
6. Confirm write (re-read labels/status).

## Ready gate (after plan)

When `sdlc:ideate`, `sdlc:spec`, and `sdlc:plan` are all present:

1. Accumulate **`sdlc:agent-ready`**
2. Transition to **In Progress**
3. Post a **Jira comment** (do **not** edit Description) titled e.g. `## SDLC review package — idea / spec / plan` with:
   - Status line (labels + In Progress + waiting on `sdlc:human-ready`)
   - **1) Idea** — HMW, direction, MVP, Not doing, coverage/dup notes
   - **2) Spec** — objective, assumptions, acceptance criteria, surfaces
   - **3) Plan / tasks** — task table, architecture, PR branch `aiagent/<KEY>`, checkpoint
   - **What you should do now** — approve / change / stop
4. Keep full detail in `agent_space/<KEY>/` as agent working copies (comment = human view).
5. Include **HUMAN GATE** unblock instructions in the same or follow-up comment.
6. Return control to harness — do **not** start implement

Do **not** issue HUMAN GATE until that review-package **comment** exists.

### Plan refine

If the human requests changes before `sdlc:human-ready`: update `agent_space/<KEY>/`, then post a **new** comment with the revised package (do not overwrite Description).

## Missing-gate summary

If harness needs maker work but `sdlc:agent-ready` or `sdlc:human-ready` is absent:

1. Post a structured summary comment (completed phases, missing labels, how to unblock)
2. Do **not** transition into implementation
3. Stop for outer loop

## Feedback revocation (`sdlc:need-review-stage`)

When the issue gains **`sdlc:need-review-stage`** (human-added) or the harness detects it on resume:

1. **Agent removes** (do not ask the human to do this manually):
   - `sdlc:human-ready`
   - `sdlc:agent-approved`
2. **Keep:** `sdlc:agent-ready`, all `sdlc:*` progress labels, `sdlc:need-review-stage`.
3. Comment: feedback active; stale approvals cleared; maker blocked until re-approval.
4. Keep status at **Review** when possible (else leave current).
5. After feedback is addressed **and** human re-approves (`sdlc:human-ready` or `approved` comment):
   - Accumulate `sdlc:human-ready` if only a comment was given
   - **Agent removes** `sdlc:need-review-stage`
   - Comment evidence of what changed
   - Re-set `sdlc:agent-approved` only after a fresh PR update is ready for human again

## Blocked

On escalate: accumulate `sdlc:blocked` + failure comment. Resume after outer-loop unblock; keep historical labels.

## Related

`docs/ai-sdlc/README.md` · `docs/design/ai-sdlc-loop.md` · `Skills/sdlc-loop/SKILL.md`
