# AI SDLC Skills Registry

Canonical skills live here. Cursor discovers them via symlinks in `.cursor/skills/`.

**People start here:** [docs/ai-sdlc/README.md](../docs/ai-sdlc/README.md)  
**Loop design:** [docs/design/ai-sdlc-loop.md](../docs/design/ai-sdlc-loop.md)  
**Orchestrator:** `sdlc-loop` — human outer loop; agents inner loop  
**Model:** [skills.addy.ie/loops](https://skills.addy.ie/loops/)  
**Templates:** [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)  
**State DB:** Jira — `sdlc:*` progress + `aiagent-*` / `human-approved` gates; status In Progress / Review  
**Run artifacts:** [`agent_space/<ISSUE-KEY>/`](../agent_space/README.md) (not product `docs/`)

Skills are **feature-agnostic**. Input = issue key; work is derived from the ticket (and artifacts the phases create). **Resume** from existing labels — do not restart finished phases.

## How to run

1. Atlassian MCP can write the target Jira project (e.g. BLRID).
2. Invoke **`sdlc-loop`** with an issue key.
3. Outer loop: **HUMAN GATE** (plan + PR), **ESCALATE**, **VERDICT**, and optional **`aiagent-need-review-stage`** feedback.
4. Do not micro-prompt each phase unless autonomy=`interactive`.

## Loop roles

| Role | Skill / actor |
|------|----------------|
| Harness | `sdlc-loop` |
| Inner workers | phase skills below |
| State + fingerprint + status | `jira-phase-gate` |
| Maker | `incremental-implementation` (+ `test-driven-development`) |
| Checker | `code-review-and-quality` (separate pass; inline comments) |
| Outer loop | Human |
| Product conventions (when coding MiniGit) | root `AGENTS.md` |

## Phase map

| Phase | Skill dir | Progress label | Gate / status | Outer-loop touch | Role | Rubric |
|-------|-----------|----------------|---------------|------------------|------|--------|
| Requirements | `idea-refine` | `sdlc:ideate` | dup + coverage notes | Escalate only | Inner | `evals/rubrics/ideate.md` |
| Design | `spec-driven-development` | `sdlc:spec` | coverage in boundaries | Escalate only | Inner | `evals/rubrics/spec.md` |
| Plan | `planning-and-task-breakdown` | `sdlc:plan` | then **`aiagent-ready`** + **In Progress** | **HUMAN GATE** | Inner → outer | `evals/rubrics/plan.md` |
| Build | `incremental-implementation` | `sdlc:implement` | needs `human-approved`; PR `aiagent/<KEY>`; **`aiagent-approved`** | Escalate on fail | **Maker** | `evals/rubrics/implement.md` |
| Test | `test-driven-development` | `sdlc:test` | same branch/PR | Escalate on fail | Maker | `evals/rubrics/test.md` |
| Review | `code-review-and-quality` | `sdlc:review` | after human PR OK → status **Review** | Then **VERDICT** | **Checker** | `evals/rubrics/review.md` |
| Done | — | `sdlc:done` | — | After ship verdict | Outer | — |
| Blocked | — | `sdlc:blocked` | — | **ESCALATE** | Outer | — |

### Gate labels (accumulate)

| Label | Meaning |
|-------|---------|
| `aiagent-ready` | Ideate + spec + plan complete; waiting on human |
| `human-approved` | Human accepted current gate (plan and/or via comment `approved`) |
| `aiagent-approved` | Maker finished slices + PR opened for human review |
| `aiagent-need-review-stage` | Human requested feedback incorporation at review; **agent strips** `human-approved` + `aiagent-approved` until re-approval |

Missing `aiagent-ready` or `human-approved` before maker → **stop** + summary comment.

## Dual-layer contract

1. **Deterministic** — artifacts, repo verify commands, rubric, labels, gates. Fail closed → escalate if unrecoverable.
2. **Reasoning** — LLM only after deterministic gates pass.
3. **Intervention** — escalate / human gate to outer loop (not every step). See `sdlc-loop`.
4. **Jira** — after rubric pass, `jira-phase-gate` accumulates labels and may transition status.
5. **Feedback** — `aiagent-need-review-stage` → agent revokes stale approvals, incorporates comments, waits for re-approval, then clears the feedback label. Optional `evals/feedback/`.

## Autonomy (default supervised)

| Rung | Human when |
|------|------------|
| **Supervised (default)** | Start, human gates, escalate, verdict, feedback label |
| Interactive | Every phase (demos) |
| Unattended | Out of scope v1 |

## Examples (optional)

Sample feature narrative only: [docs/examples/merge/](../docs/examples/merge/). Not loaded into the loop.

## Commands

```bash
make eval-skills
make check          # when the ticket requires MiniGit product changes
```
