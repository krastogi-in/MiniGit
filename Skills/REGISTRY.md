# AI SDLC Skills Registry

Canonical skills live here. Cursor discovers them via symlinks in `.cursor/skills/`.

**People start here:** [docs/ai-sdlc/README.md](../docs/ai-sdlc/README.md)  
**Loop design:** [docs/design/ai-sdlc-loop.md](../docs/design/ai-sdlc-loop.md)  
**Orchestrator:** `sdlc-loop` — human outer loop; agents inner loop  
**Model:** [skills.addy.ie/loops](https://skills.addy.ie/loops/)  
**Templates:** [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)  
**State DB:** Jira (BLRID) — `sdlc:*` labels **accumulate**

Skills are **feature-agnostic**. Input = issue key; work is derived from the ticket (and artifacts the phases create).

## How to run

1. Atlassian MCP can write the target Jira project (e.g. BLRID).
2. Invoke **`sdlc-loop`** with an issue key.
3. Outer loop: answer **PLAN GATE**, **ESCALATE**, **VERDICT** only (supervised default).
4. Do not micro-prompt each phase unless autonomy=`interactive`.

## Loop roles

| Role | Skill / actor |
|------|----------------|
| Harness | `sdlc-loop` |
| Inner workers | phase skills below |
| State + fingerprint | `jira-phase-gate` |
| Maker | `incremental-implementation` (+ `test-driven-development`) |
| Checker | `code-review-and-quality` (separate pass) |
| Outer loop | Human |
| Product conventions (when coding MiniGit) | root `AGENTS.md` |

## Phase map

| Phase | Skill dir | Label | Outer-loop touch | Role | Rubric |
|-------|-----------|-------|------------------|------|--------|
| Requirements | `idea-refine` | `sdlc:ideate` | Escalate only | Inner | `evals/rubrics/ideate.md` |
| Design | `spec-driven-development` | `sdlc:spec` | Escalate only | Inner | `evals/rubrics/spec.md` |
| Plan | `planning-and-task-breakdown` | `sdlc:plan` | **PLAN GATE** | Inner → outer | `evals/rubrics/plan.md` |
| Build | `incremental-implementation` | `sdlc:implement` | Escalate on fail | **Maker** | `evals/rubrics/implement.md` |
| Test | `test-driven-development` | `sdlc:test` | Escalate on fail | Maker | `evals/rubrics/test.md` |
| Review | `code-review-and-quality` | `sdlc:review` | Then **VERDICT** | **Checker** | `evals/rubrics/review.md` |
| Done | — | `sdlc:done` | After ship verdict | Outer | — |
| Blocked | — | `sdlc:blocked` | **ESCALATE** | Outer | — |

## Dual-layer contract

1. **Deterministic** — artifacts, repo verify commands, rubric, label. Fail closed → escalate if unrecoverable.
2. **Reasoning** — LLM only after deterministic gates pass.
3. **Intervention** — escalate to outer loop (not every step). See `sdlc-loop`.
4. **Jira** — after rubric pass, `jira-phase-gate` accumulates `sdlc:*`.
5. **Feedback** — rejection → ticket comment + optional `evals/feedback/`; harness resumes.

## Autonomy (default supervised)

| Rung | Human when |
|------|------------|
| **Supervised (default)** | Start, plan gate, escalate, verdict |
| Interactive | Every phase (demos) |
| Unattended | Out of scope v1 |

## Examples (optional)

Sample feature narrative only: [docs/examples/merge/](../docs/examples/merge/). Not loaded into the loop.

## Commands

```bash
make eval-skills
make check          # when the ticket requires MiniGit product changes
```
