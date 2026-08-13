# Spec: AI SDLC Skills Registry (ticket-driven factory)

## Objective

Provide a **feature-agnostic** AI SDLC skills registry and loop harness so a human stays on the outer loop while agents process **any** Jira ticket through ideate → spec → plan → implement → test → review, using Jira labels/comments as state.

**Sandbox app:** MiniGit (when the ticket requires product changes).  
**People guide:** [docs/ai-sdlc/README.md](../ai-sdlc/README.md)

**Success looks like:**
1. Skills are Cursor-discoverable and do not hardcode a specific feature.
2. Input = issue key; phases derive scope from the ticket.
3. Outer loop: plan gate, escalate, verdict only (supervised default).
4. Maker ≠ checker; Jira `sdlc:*` labels accumulate.
5. `make eval-skills` validates registry integrity.
6. Optional examples live under `docs/examples/` only.

## Decisions (locked)

1. **Factory ≠ feature** — no Merge/two-parent/perf numbers in skills; those belong in ticket-produced specs.
2. **Jira** = state DB via Atlassian MCP; labels accumulate (`sdlc:ideate` … `sdlc:done`, plus `sdlc:blocked`).
3. **Skills** in `skills/`; `.cursor/skills/` symlinks.
4. **Autonomy** = supervised by default ([loop engineering](https://skills.addy.ie/loops/)); orchestrator `sdlc-loop`.
5. **Keep `AGENTS.md`** for MiniGit product conventions; factory explained in `docs/ai-sdlc/README.md`.
6. **Eval v1** = deterministic structure checks, not LLM-as-judge.
7. **Deploy phase** = out of scope v1 (document as N/A for this sandbox).

## Tech Stack

| Layer | Choice |
|-------|--------|
| Skills | Cursor `SKILL.md` |
| Templates | Adapted from [agent-skills](https://github.com/addyosmani/agent-skills) |
| State | Jira + markdown artifacts |
| Sandbox | MiniGit + `AGENTS.md` |
| Verify | `make eval-skills`; `make check` when coding MiniGit |

## Commands

```bash
make eval-skills
make setup | make lint | make typecheck | make test | make check | make fmt
```

## Project Structure

```
docs/ai-sdlc/README.md          # What this project is
docs/design/ai-sdlc-loop.md
docs/examples/                  # Optional samples only
skills/                         # Factory skills (generic)
.cursor/skills/                 # Symlinks
evals/                          # Rubrics + eval runner
AGENTS.md                       # MiniGit product agents guide
src/ tests/                     # MiniGit app
```

## Code Style

Skills: Cursor conventions; under 500 lines; progressive disclosure.  
MiniGit: `AGENTS.md`.

## Testing Strategy

| Concern | Approach |
|---------|----------|
| Registry integrity | `make eval-skills` |
| Product changes | Ticket-defined tests via TDD skill + `make check` |

## Dual-layer / phase map

See `skills/REGISTRY.md`.

## Boundaries

**Always:** derive scope from the issue; fail closed on deterministic gates; update Jira only after rubric/escalate/verdict authority; maker ≠ checker.

**Ask first:** label taxonomy changes; new dependencies; enabling unattended loops.

**Never:** hardcode a demo feature into skills; commit secrets; fake Jira updates; claim done without evidence.

## Success Criteria

- [ ] `docs/ai-sdlc/README.md` explains factory vs MiniGit
- [ ] skills/REGISTRY feature-agnostic; Merge only under `docs/examples/`
- [ ] `sdlc-loop` takes issue key as input
- [ ] `make eval-skills` green
- [ ] `AGENTS.md` retained for MiniGit

## Open Questions

1. Atlassian MCP authenticated?
2. Which BLRID issue for the first live run?
3. Jira hierarchy pack (Epic/Story/fields) — next doc slice?

## Related

- Example narrative: [docs/examples/merge/](../../examples/merge/)
- Idea: [ideas/ai-sdlc-skills-registry.md](../ideas/ai-sdlc-skills-registry.md)
- Ticket runs: [agent_space/](../../../agent_space/README.md)
