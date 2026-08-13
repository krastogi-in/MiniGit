# Implementation Plan: AI SDLC Skills Registry (generic factory)

## Overview

Ship and maintain a **ticket-driven** AI SDLC factory: Cursor skills + `sdlc-loop` + Jira state + rubrics/evals. Scope for any feature comes from the Jira issue, not from a baked-in backlog. MiniGit remains the sandbox app (`AGENTS.md`).

Spec: [specs/ai-sdlc-skills-registry.md](../specs/ai-sdlc-skills-registry.md)  
People guide: [README.md](../README.md)

## Architecture Decisions

- Factory skills are **feature-agnostic**
- Example narratives only under `docs/examples/`
- Supervised outer loop: plan gate, escalate, verdict
- Labels accumulate; maker ≠ checker
- Keep `AGENTS.md` for product code

## Dependency Graph

```
docs/ai-sdlc/README.md
        │
skills/REGISTRY + sdlc-loop + phase skills + jira-phase-gate
        │
.cursor/skills symlinks + evals
        │
        ▼
Live run: any BLRID issue → sdlc-loop → artifacts + labels
```

## Task List

### Phase 1: Factory foundation — DONE

- [x] Registry, templates, phase skills, jira-phase-gate, sdlc-loop
- [x] Symlinks, rubrics, `make eval-skills`
- [x] Cleanup: strip feature hardcoding; add people README + examples/

### Checkpoint: Factory

- [x] `make eval-skills` green
- [ ] Human OK to run live ticket

### Phase 2: Live ticket run (generic)

- [ ] Task A: Confirm Atlassian MCP; pick BLRID issue
- [ ] Task B: Run `sdlc-loop` on that issue through PLAN GATE
- [ ] Task C: After plan approval, supervised maker→test→checker→VERDICT

### Phase 3: Follow-ups (optional)

- [ ] Task D: Jira hierarchy/fields doc (Outcome/Epic/Story/Component/versions)
- [ ] Task E: Richer evals / feedback samples
- [ ] Task F: Deploy skill or explicit N/A in registry

## Risks

| Risk | Mitigation |
|------|------------|
| MCP missing | Fail closed in jira-phase-gate |
| Feature creep into skills | Review REGISTRY for ticket-only language |
| Confusion factory vs MiniGit | `docs/ai-sdlc/README.md` |

## Open Questions

- MCP auth · first issue key
