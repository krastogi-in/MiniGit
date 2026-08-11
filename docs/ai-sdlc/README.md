# AI SDLC Factory (in MiniGit)

This repository contains **two layers**. Do not confuse them.

| Layer | What it is | Entry points |
|-------|------------|--------------|
| **AI SDLC factory** | Generic, ticket-driven skills + loop. Works for **any** feature described by a Jira issue. | `Skills/`, `docs/ai-sdlc/`, `evals/` |
| **MiniGit app** | Educational Git clone (Python/SQLite/Flask) used as the **sandbox** when a ticket asks for product changes. | `src/`, `tests/`, [`AGENTS.md`](../../AGENTS.md) |

Inspired by [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) and [loop engineering](https://skills.addy.ie/loops/).

## What this project is (for people)

You stay on the **outer loop**. Agents run the **inner loop**. Jira (BLRID) is the **state database**: accumulated `sdlc:*` labels fingerprint progress; comments store evidence.

**Input:** a Jira issue key (and Atlassian MCP access).  
**Output:** specs/plans/code/tests as required by *that ticket*, plus label trail through to `sdlc:done` after your verdict.

Feature details (e.g. “Merge needs two parents”) belong in **that ticket’s** spec/plan — never hardcoded into the factory skills.

## How to run

Step-by-step runbook (Jira MCP → ticket → trigger → outer loop):

**→ [HOW-TO-EXECUTE.md](HOW-TO-EXECUTE.md)**

Short version:

1. Ensure Atlassian MCP can write BLRID (`~/.cursor/mcp.json`).
2. In Cursor, invoke skill **`sdlc-loop`** with the issue key.
3. Respond only to **PLAN GATE**, **ESCALATE**, and **VERDICT** (supervised default).
4. Agents read the ticket, break work down, implement/test/review using phase skills, and update Jira after each rubric pass.

```bash
make eval-skills   # smoke-test that the registry is intact
make check         # MiniGit product quality (when coding the app)
```

## Skills map

See [`Skills/REGISTRY.md`](../../Skills/REGISTRY.md). Orchestrator: `sdlc-loop`. Phase workers are feature-agnostic.

## Keep / don’t keep

| Keep | Don’t put in factory skills |
|------|-----------------------------|
| Dual-layer (deterministic + LLM) | A specific feature’s design (Merge, etc.) |
| Outer-loop packets | Hardcoded perf numbers for one feature |
| Maker ≠ checker | “Teaching slice” as the only path |
| [`AGENTS.md`](../../AGENTS.md) for MiniGit code | Replacing ticket AC with baked-in backlog |

## Optional example

A sample feature narrative (not part of the loop): [`docs/examples/merge/`](../examples/merge/).

## Related docs

- Loop design: [`docs/design/ai-sdlc-loop.md`](../design/ai-sdlc-loop.md)
- Factory spec: [`docs/specs/ai-sdlc-skills-registry.md`](../specs/ai-sdlc-skills-registry.md)
- Idea one-pager: [`docs/ideas/ai-sdlc-skills-registry.md`](../ideas/ai-sdlc-skills-registry.md)
