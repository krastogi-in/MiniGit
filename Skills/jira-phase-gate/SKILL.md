---
name: jira-phase-gate
description: >-
  Updates Jira issues used as SDLC state DB: posts evidence comments, accumulates
  sdlc:* and aiagent-* labels, and transitions status (In Progress / Review).
  Feature-agnostic. Use after a phase rubric passes, on human gates, escalate,
  feedback, or when sdlc-loop advances fingerprints.
---

# Jira Phase Gate

State backend for `sdlc-loop`. Labels = progress + gates; comments = evidence;
status = workflow visibility. Works for **any** issue key.

## Deterministic layer (fail closed)

- [ ] Rubric pass **or** explicit gate/escalate/verdict/feedback action from `sdlc-loop`
- [ ] Issue key known
- [ ] Atlassian MCP available — else ESCALATE (connector); never fake an update
- [ ] Phase label ∈ `sdlc:ideate|spec|plan|implement|test|review|done|blocked` when advancing a phase
- [ ] Gate labels when required ∈ `aiagent-ready|human-approved|aiagent-approved|aiagent-need-review-stage`

## Label families

| Family | Examples | Rule |
|--------|----------|------|
| Progress | `sdlc:ideate` … `sdlc:done`, `sdlc:blocked` | **Accumulate**; never strip prior `sdlc:*` |
| Agent/human gates | `aiagent-ready`, `human-approved`, `aiagent-approved`, `aiagent-need-review-stage` | Accumulate when set; **exception:** on feedback start, strip stale approvals (below). Never invent `human-approved` |

## Status map (discover transitions each time)

| When | Target status name |
|------|--------------------|
| After ideate+spec+plan → `aiagent-ready` | **In Progress** |
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

1. Accumulate **`aiagent-ready`**
2. Transition to **In Progress**
3. Comment that maker is blocked until **`human-approved`** or an `approved` comment
4. Return control to harness (**HUMAN GATE**) — do not start implement

## Missing-gate summary

If harness needs maker work but `aiagent-ready` or `human-approved` is absent:

1. Post a structured summary comment (completed phases, missing labels, how to unblock)
2. Do **not** transition into implementation
3. Stop for outer loop

## Feedback revocation (`aiagent-need-review-stage`)

When the issue gains **`aiagent-need-review-stage`** (human-added) or the harness detects it on resume:

1. **Agent removes** (do not ask the human to do this manually):
   - `human-approved`
   - `aiagent-approved`
2. **Keep:** `aiagent-ready`, all `sdlc:*` progress labels, `aiagent-need-review-stage`.
3. Comment: feedback active; stale approvals cleared; maker blocked until re-approval.
4. Keep status at **Review** when possible (else leave current).
5. After feedback is addressed **and** human re-approves (`human-approved` or `approved` comment):
   - Accumulate `human-approved` if only a comment was given
   - **Agent removes** `aiagent-need-review-stage`
   - Comment evidence of what changed
   - Re-set `aiagent-approved` only after a fresh PR update is ready for human again

## Blocked

On escalate: accumulate `sdlc:blocked` + failure comment. Resume after outer-loop unblock; keep historical labels.

## Related

`docs/ai-sdlc/README.md` · `docs/design/ai-sdlc-loop.md` · `Skills/sdlc-loop/SKILL.md`
