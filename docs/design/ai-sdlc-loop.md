# AI SDLC Loop Design

Based on [Loop engineering](https://skills.addy.ie/loops/): **skills run inside the loop; you stay on the outer loop.**

People-facing overview: [docs/ai-sdlc/README.md](../ai-sdlc/README.md).

## Mental model

| Loop | Who | Job |
|------|-----|-----|
| **Inner** | Agents | Read ticket → act (skill) → check (rubric / verify) → advance Jira state |
| **Outer** | You | Constraints, sample evidence, verdict on escalate, own ship decision |

**Input:** any Jira issue. **State:** accumulated `sdlc:*` labels + comments.  
Feature design is **not** hardcoded in skills; it emerges from the ticket via idea/spec/plan.

## Five primitives (mapped)

| Primitive ([Addy](https://skills.addy.ie/loops/)) | This factory |
|--------------------------------------------------|--------------|
| Skills | `Skills/*` |
| Connectors | Atlassian MCP → Jira |
| Subagents | Maker ≠ Checker |
| State | Jira labels/comments; `docs/specs/`; `tasks/` |
| Automations / worktrees | Optional later; v1 = Cursor + `sdlc-loop` |

## Default autonomy: Supervised

1. **Start** — issue key + “run sdlc-loop”
2. **PLAN GATE** — approve plan/todo once
3. **ESCALATE** — failures / expensive judgment
4. **VERDICT** — ship / block / redirect / narrow → `sdlc:done`

## Escalate triggers

| Trigger | Example |
|---------|---------|
| Deterministic / rubric fail | Missing artifact after retry |
| Verify fail | Repo test/lint suite still red |
| Ask-first | New dependency, surprising schema, label taxonomy change |
| Checker Critical | Security / data loss |
| Product ambiguity | Scope not in ticket; conflicting AC |
| Connector down | Jira MCP unavailable |

On escalate: accumulate `sdlc:blocked` + evidence comment; wait for outer loop.

## Inner loop cycle

```
read Jira issue + labels
  → next phase skill from REGISTRY
  → deterministic → reasoning → rubric
  → pass: jira-phase-gate / fail: retry or ESCALATE
  → next phase (unless plan gate / escalate / verdict)
```

## Maker ≠ checker

Separate checker pass before **VERDICT**.

## Lights on vs out

| Lights out OK | Keep lights on |
|---------------|----------------|
| Green/red verify oracles | Spec/API contracts |
| Rubric checklists | Security-sensitive changes |
| Short mechanical retries | Final **VERDICT** / `sdlc:done` |

## Entry

Invoke **`sdlc-loop`** with an issue key.
