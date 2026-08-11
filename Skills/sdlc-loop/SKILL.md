---
name: sdlc-loop
description: >-
  Orchestrates a feature-agnostic AI SDLC inner loop while keeping the human on
  the outer loop. Use when running the factory on any Jira ticket, for supervised
  autonomy, or to continue until escalate or verdict. Reads issue + sdlc:* labels
  as state; runs phase skills; maker then separate checker; pauses only on plan
  gate, failures, and final verdict.
---

# SDLC Loop Orchestrator

You are the **loop harness**, not the feature author. Keep the human on the **outer loop**; agents run the **inner loop**.  

Model: [skills.addy.ie/loops](https://skills.addy.ie/loops/).  
People guide: `docs/ai-sdlc/README.md`. Design: `docs/design/ai-sdlc-loop.md`.

## When to use

- User says: run SDLC loop, supervised build, factory mode, outer-loop mode
- Any Jira issue that should move through AI SDLC phases
- Continue after human unblocks an escalate

## Inputs

- **Jira issue key** (required) — e.g. `BLRID-123`
- Autonomy: default **supervised**; `interactive` only if user asks

Do **not** assume a specific feature. Read the issue (summary, description, AC, links). All scope comes from the ticket and phase artifacts.

## State (Jira = DB)

Read accumulated `sdlc:*` labels to find the next phase:

| Latest progress label | Next skill |
|-----------------------|------------|
| (none) | `idea-refine` |
| `sdlc:ideate` | `spec-driven-development` |
| `sdlc:spec` | `planning-and-task-breakdown` → then **PLAN GATE** |
| `sdlc:plan` | `incremental-implementation` (maker) |
| `sdlc:implement` | `test-driven-development` |
| `sdlc:test` | `code-review-and-quality` (**separate checker pass**) |
| `sdlc:review` | **VERDICT GATE** → on approve: `jira-phase-gate` + `sdlc:done` |
| `sdlc:done` | Stop; summarize evidence |
| `sdlc:blocked` | Do not advance; wait for outer-loop instructions |

## Inner loop (without asking each step)

For each phase until gate/escalate:

1. Load phase skill from `Skills/<name>/SKILL.md`
2. Ground work in **this issue** + repo conventions (`AGENTS.md` if changing MiniGit)
3. Deterministic checks → reasoning → rubric
4. On pass → `jira-phase-gate` (comment + accumulate label)
5. On fail → one mechanical retry if obvious; else **ESCALATE**

After plan approval, continue maker tasks without pausing between them (supervised).

## Outer-loop packets

### PLAN GATE

```markdown
## OUTER LOOP — PLAN GATE
Issue: <KEY>
Evidence: tasks/plan.md, tasks/todo.md (or issue-scoped paths)
Ask: Approve plan? (yes / change X / stop)
Until yes: do not start maker.
```

### ESCALATE

```markdown
## OUTER LOOP — ESCALATE
Issue: <KEY>
Phase: …
Trigger: <deterministic|verify|ask-first|checker-critical|connector|product>
Evidence: …
Tried: …
Ask: redirect / fix constraint / abort
Action: accumulate sdlc:blocked + comment
```

### VERDICT

```markdown
## OUTER LOOP — VERDICT
Issue: <KEY>
Evidence: diff summary, verify commands, review checklist
Ask: ship | block | redirect | narrow
On ship: jira-phase-gate → sdlc:done
```

## Maker ≠ checker

- Maker: `incremental-implementation` (+ TDD as needed)
- Checker: separate pass with **only** `code-review-and-quality`
- Never self-LGTM in the maker pass

## Autonomy rungs

| Rung | Behavior |
|------|----------|
| Supervised (default) | Plan gate + escalate + verdict |
| Interactive | Also pause after each phase |
| Unattended | Forbidden in v1 |

## Related

- `Skills/REGISTRY.md` · `Skills/jira-phase-gate/SKILL.md` · `evals/rubrics/loop.md`
