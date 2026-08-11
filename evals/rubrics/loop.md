# Rubric: loop (sdlc-loop)

## Pass if

- [ ] Default autonomy is supervised (plan gate + escalate + verdict)
- [ ] Escalate triggers listed (deterministic, verify, ask-first, critical, connector)
- [ ] Maker ≠ checker enforced
- [ ] Jira labels treated as state; `sdlc:blocked` on escalate
- [ ] Outer-loop packet formats defined (PLAN / ESCALATE / VERDICT)

## Fail if

- Human prompted every phase by default
- Self-review allowed in maker pass
- Jira updated without rubric/escalate/verdict authority
