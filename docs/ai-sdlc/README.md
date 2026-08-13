# AI SDLC Factory (in MiniGit)

This repository contains **two layers**. Do not confuse them.

| Layer | What it is | Entry points |
|-------|------------|--------------|
| **AI SDLC factory** | Generic, ticket-driven skills + loop. Works for **any** feature described by a Jira issue. | `Skills/`, `docs/ai-sdlc/`, `evals/` |
| **MiniGit app** | Educational Git clone (Python/SQLite/Flask) used as the **sandbox** when a ticket asks for product changes. | `src/`, `tests/`, [`AGENTS.md`](../../AGENTS.md) |

Inspired by [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) and [loop engineering](https://skills.addy.ie/loops/).

## What this project is (for people)

You stay on the **outer loop**. Agents run the **inner loop**. Jira is the **state database**: `sdlc:*` labels (progress + gates), comments, and workflow status.

**Input:** a Jira issue key (and Atlassian MCP access).  
**Output:** specs/plans/code/tests as required by *that ticket*, PR on `aiagent/<KEY>`, plus label trail through to `sdlc:done` after your verdict.

The loop **resumes** from existing labels. It flags **duplicate tickets** and **already-covered** code early. Feature details belong in **that ticket’s** spec/plan — never hardcoded into the factory skills.

## How to run

Step-by-step runbook (Jira MCP → ticket → trigger → outer loop):

**→ [HOW-TO-EXECUTE.md](HOW-TO-EXECUTE.md)**

Short version:

1. Ensure Atlassian MCP can write BLRID (`~/.cursor/mcp.json`).
2. In Cursor, invoke skill **`sdlc-loop`** with the issue key.
3. After plan: look for `sdlc:agent-ready` + **In Progress**; add `sdlc:human-ready` (or comment `approved`).
4. Review the PR on `aiagent/<KEY>`; agent sets `sdlc:agent-approved`, then status **Review** after you accept.
5. Optional: add `sdlc:need-review-stage` for feedback incorporation.
6. Respond to **ESCALATE** / **VERDICT** as needed.

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
| Outer-loop packets + gate labels | Hardcoded perf numbers for one feature |
| Maker ≠ checker | “Teaching slice” as the only path |
| [`AGENTS.md`](../../AGENTS.md) for MiniGit code | Replacing ticket AC with baked-in backlog |

## Optional example

A sample feature narrative (not part of the loop): [`docs/examples/merge/`](../examples/merge/).

## Related docs

- Loop design: [`docs/design/ai-sdlc-loop.md`](../design/ai-sdlc-loop.md)
- Factory spec: [`specs/ai-sdlc-skills-registry.md`](specs/ai-sdlc-skills-registry.md)
- Idea one-pager: [`ideas/ai-sdlc-skills-registry.md`](ideas/ai-sdlc-skills-registry.md)
- Factory plan (historical): [`tasks/`](tasks/)
- Ticket run artifacts: [`agent_space/`](../../agent_space/README.md) (not under product `docs/`)
