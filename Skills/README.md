# Skills (AI SDLC factory)

Canonical Cursor skills for a **ticket-driven** AI SDLC. Feature-agnostic.

- **What / why / how to run:** [docs/ai-sdlc/README.md](../docs/ai-sdlc/README.md)
- **Execute (Jira + trigger):** [docs/ai-sdlc/HOW-TO-EXECUTE.md](../docs/ai-sdlc/HOW-TO-EXECUTE.md)
- **Phase map + gate labels:** [REGISTRY.md](REGISTRY.md)
- **Loop design:** [docs/design/ai-sdlc-loop.md](../docs/design/ai-sdlc-loop.md)
- **Cursor discovery:** symlinked from `.cursor/skills/`

Gates: `aiagent-ready` → your `human-approved` → PR on `aiagent/<KEY>` → `aiagent-approved` → status **Review**. Feedback: `aiagent-need-review-stage` (agent clears stale approvals; you re-approve).

Ticket scratch lives in [`agent_space/`](../agent_space/README.md), not product `docs/`.

`AGENTS.md` at the repo root is for **MiniGit product** coding conventions, not a substitute for this factory README.
