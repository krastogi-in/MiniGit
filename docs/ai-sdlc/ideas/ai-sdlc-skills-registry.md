# AI SDLC Skills Registry

## Problem Statement
How might we run any Jira-backed feature through an AI SDLC with humans on the outer loop, agents inside, and durable progress in Jira — without hardcoding one demo feature into the factory?

## Recommended Direction
**Ticket-driven factory** hosted beside the MiniGit sandbox.

- Skills in `Skills/` (Cursor via `.cursor/skills/` symlinks)
- Orchestrator `sdlc-loop`; state = BLRID labels/comments
- Dual-layer + maker/checker + supervised autonomy ([loops](https://skills.addy.ie/loops/))
- MiniGit + `AGENTS.md` only when the **ticket** requires product code
- Optional samples under `docs/examples/` (e.g. Merge) — not in the loop
- Ticket run scratch under `agent_space/<KEY>/` — not product `docs/`

## Key Assumptions
- [ ] BLRID allows `sdlc:*` labels
- [x] Agent updates Jira via Atlassian MCP (when configured)
- [x] Factory is feature-agnostic
- [ ] First live issue key chosen

## MVP Scope
**In:** registry, sdlc-loop, phase skills, rubrics, evals, people README, outer-loop packets  
**Out:** unattended dark factory; hardcoded Merge implementation; full Jira hierarchy pack (follow-up)

## Not Doing
- Baking Merge/two-parent/perf into skills — belongs in ticket specs
- Replacing `AGENTS.md` — still required for MiniGit coding

## Open Questions
- MCP auth · first issue key · Epic/Story field taxonomy docs
