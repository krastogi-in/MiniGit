# Rubric: loop (sdlc-loop)

## Pass if

- [ ] Default autonomy is supervised (human gates + escalate + verdict)
- [ ] Resume-from-labels documented (do not restart finished phases)
- [ ] Gate labels defined: `aiagent-ready`, `human-approved`, `aiagent-approved`, `aiagent-need-review-stage`
- [ ] Status map: In Progress after ready gate; Review after human PR approval
- [ ] Missing `aiagent-ready` / `human-approved` → stop + summary (no maker)
- [ ] PR branch convention `aiagent/<ISSUE-KEY>`
- [ ] Duplicate + already-covered boot checks
- [ ] Escalate triggers listed (deterministic, verify, ask-first, critical, connector, missing-gate)
- [ ] Maker ≠ checker enforced
- [ ] On `aiagent-need-review-stage`: agent removes stale `human-approved` / `aiagent-approved`; after re-approval, agent removes the feedback label
- [ ] Outer-loop packet formats defined (HUMAN GATE / ESCALATE / VERDICT / FEEDBACK)

## Fail if

- Human prompted every phase by default
- Self-review allowed in maker pass
- Maker runs without gate labels
- Jira updated without rubric/gate/escalate/verdict authority
- Loop always restarts from ideate when labels already exist
