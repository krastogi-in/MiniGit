# Dual-layer + loop contract

Copy into each phase `SKILL.md`. Orchestration: `sdlc-loop`. Design: `docs/design/ai-sdlc-loop.md`.

## Deterministic layer (fail closed)

- [ ] Required artifacts exist at expected paths
- [ ] Rubric file checked: `evals/rubrics/{{phase}}.md`
- [ ] MiniGit commands run when applicable (`make check`, etc.)
- [ ] Do not claim done if any checkbox fails

## Reasoning layer

- Apply phase-specific judgment only after deterministic gates pass
- Do not override a failed gate with “looks good”

## Intervention (outer loop — escalate, don’t chatter)

Do **not** pause for casual confirmation. Escalate only when:

- Deterministic/rubric fail after one retry
- Verify (`make check`) still red
- Ask-first boundary hit
- Checker Critical finding
- Product ambiguity / connector (Jira MCP) down

Escalate packet format (**ESCALATE**): see `Skills/sdlc-loop/SKILL.md`. Accumulate `sdlc:blocked` via `jira-phase-gate`.

**Plan gate** and **verdict** are owned by `sdlc-loop`, not every phase skill.

## Jira fingerprint

After rubric pass, invoke `jira-phase-gate`:

1. Post evidence comment (`_templates/phase-comment.md`)
2. **Accumulate** label `{{LABEL}}` (keep prior `sdlc:*`)

## Feedback

On outer-loop rejection: BLRID comment + optionally `evals/feedback/{{issue}}-{{phase}}.md`, then resume under `sdlc-loop`.
