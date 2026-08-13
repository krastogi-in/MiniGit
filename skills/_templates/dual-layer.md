# Dual-layer + loop contract

Copy into each phase `SKILL.md`. Orchestration: `sdlc-loop`. Design: `docs/design/ai-sdlc-loop.md`.

## Deterministic layer (fail closed)

- [ ] Required artifacts exist at expected paths
- [ ] Rubric file checked: `evals/rubrics/{{phase}}.md`
- [ ] MiniGit commands run when applicable (`make check`, etc.)
- [ ] Gate labels respected (`sdlc:agent-ready`, `sdlc:human-ready`, …) when the phase requires them
- [ ] Do not claim done if any checkbox fails

## Reasoning layer

- Apply phase-specific judgment only after deterministic gates pass
- Do not override a failed gate with “looks good”

## Intervention (outer loop — escalate, don’t chatter)

Do **not** pause for casual confirmation. Escalate or **HUMAN GATE** when:

- Deterministic/rubric fail after one retry
- Verify (`make check`) still red
- Ask-first boundary hit
- Checker Critical finding
- Product ambiguity / connector (Jira MCP) down
- Missing `sdlc:agent-ready` / `sdlc:human-ready` before maker
- Human set `sdlc:need-review-stage` (incorporate feedback)

Escalate packet format (**ESCALATE**): see `skills/sdlc-loop/SKILL.md`. Accumulate `sdlc:blocked` via `jira-phase-gate`.

**Human gates** and **verdict** are owned by `sdlc-loop`, not every phase skill.

## Jira fingerprint

After rubric pass, invoke `jira-phase-gate`:

1. Post evidence comment (`_templates/phase-comment.md`)
2. **Accumulate** label `{{LABEL}}` (keep prior `sdlc:*` and gate labels)
3. Apply status transitions when the loop contract requires (In Progress / Review)
4. At ready gate: post idea/spec/plan as a **comment** — never replace the original Description

## Feedback

On outer-loop rejection or `sdlc:need-review-stage`: agent removes stale `sdlc:human-ready` / `sdlc:agent-approved`, incorporates BLRID + PR comments (+ optional `evals/feedback/{{issue}}-{{phase}}.md`), then waits for re-approval and clears the feedback label.
