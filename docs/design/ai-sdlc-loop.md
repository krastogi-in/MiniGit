# AI SDLC Loop Design

Based on [Loop engineering](https://skills.addy.ie/loops/): **skills run inside the loop; you stay on the outer loop.**

People-facing overview: [docs/ai-sdlc/README.md](../ai-sdlc/README.md).

## Mental model

| Loop | Who | Job |
|------|-----|-----|
| **Inner** | Agents | Read ticket → act (skill) → check (rubric / verify) → advance Jira state |
| **Outer** | You | Constraints, human gates, sample evidence, verdict, feedback label |

**Input:** any Jira issue. **State:** accumulated `sdlc:*` labels (progress + gates) + comments + status.  
**Resume:** start at the next unfinished phase from labels — never restart from ideate if progress already exists.  
Feature design is **not** hardcoded in skills; it emerges from the ticket via idea/spec/plan.

## Five primitives (mapped)

| Primitive ([Addy](https://skills.addy.ie/loops/)) | This factory |
|--------------------------------------------------|--------------|
| Skills | `skills/*` |
| Connectors | Atlassian MCP → Jira; GitHub CLI → PR `aiagent/<KEY>` |
| Subagents | Maker ≠ Checker |
| State | Jira labels/comments/status; `agent_space/<KEY>/` run artifacts |
| Automations / worktrees | Optional later; v1 = Cursor + `sdlc-loop` |

## Default autonomy: Supervised

1. **Start / resume** — issue key + “run sdlc-loop” (from existing labels)
2. **Boot checks** — duplicate tickets; already-covered code
3. **HUMAN GATE (plan)** — after `sdlc:agent-ready` + In Progress; unblock with `sdlc:human-ready` or comment `approved`
4. **Maker + PR** — branch `aiagent/<KEY>`; label `sdlc:agent-approved`
5. **HUMAN GATE (PR)** — then status **Review**
6. **Checker** — inline comments; honor `sdlc:need-review-stage` (agent strips stale `sdlc:human-ready` / `sdlc:agent-approved`, then waits for re-approval)
7. **ESCALATE** — failures / expensive judgment
8. **VERDICT** — ship / block / redirect / narrow → `sdlc:done`

## Escalate triggers

| Trigger | Example |
|---------|---------|
| Deterministic / rubric fail | Missing artifact after retry |
| Verify fail | Repo test/lint suite still red |
| Ask-first | New dependency, surprising schema, label taxonomy change |
| Checker Critical | Security / data loss |
| Product ambiguity | Scope not in ticket; conflicting AC |
| Connector down | Jira MCP unavailable |
| Missing gate | Maker attempted without `sdlc:agent-ready` / `sdlc:human-ready` |

On escalate: accumulate `sdlc:blocked` + evidence comment; wait for outer loop.

## Inner loop cycle

```
read Jira issue + labels (+ resume offset)
  → duplicate / coverage boot notes
  → next phase skill from REGISTRY
  → deterministic → reasoning → rubric
  → pass: jira-phase-gate (labels + status) / fail: retry or ESCALATE
  → human gate when contract requires
  → next phase
```

## Maker ≠ checker

Separate checker pass before **VERDICT**. Checker leaves inline findings for unvalidated logic, missing coverage, and edge cases vs AC.

## Lights on vs out

| Lights out OK | Keep lights on |
|---------------|----------------|
| Green/red verify oracles | Spec/API contracts |
| Rubric checklists | Security-sensitive changes |
| Short mechanical retries | Human gates / **VERDICT** / `sdlc:done` |

## Entry

Invoke **`sdlc-loop`** with an issue key.
