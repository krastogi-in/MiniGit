---
name: jira-phase-gate
description: >-
  Updates Jira issues used as SDLC state DB: posts evidence comments and
  accumulates sdlc:* labels (including sdlc:blocked). Feature-agnostic. Use
  after a phase rubric passes, on escalate, or when sdlc-loop advances
  fingerprints.
---

# Jira Phase Gate

State backend for `sdlc-loop`. Labels = progress; comments = evidence. Works for **any** issue key.

## Deterministic layer (fail closed)

- [ ] Rubric pass **or** explicit escalate/verdict action from `sdlc-loop`
- [ ] Issue key known
- [ ] Atlassian MCP available — else ESCALATE (connector); never fake an update
- [ ] Label ∈ `sdlc:ideate|spec|plan|implement|test|review|done|blocked`

## Steps

1. Discover Atlassian MCP tools; authenticate if needed.
2. Read issue labels (state).
3. Post comment (`Skills/_templates/phase-comment.md` or escalate packet).
4. **Accumulate** the label — do not strip prior `sdlc:*`.
5. Confirm write.

## Blocked

On escalate: accumulate `sdlc:blocked` + failure comment. Resume after outer-loop unblock; keep historical labels.

## Related

`docs/ai-sdlc/README.md` · `docs/design/ai-sdlc-loop.md`
