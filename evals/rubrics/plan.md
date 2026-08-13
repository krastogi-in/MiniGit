# Rubric: plan

## Pass if

- [ ] `agent_space/<ISSUE-KEY>/tasks/plan.md` exists
- [ ] `agent_space/<ISSUE-KEY>/tasks/todo.md` exists with acceptance + verify per task
- [ ] Checkpoints defined
- [ ] Already-covered tasks marked reuse/verify vs build
- [ ] Notes PR branch `aiagent/<ISSUE-KEY>`
- [ ] After pass: harness sets `aiagent-ready` + In Progress; human approval via gate (not silent continue)

## Fail if

- Tasks lack acceptance criteria
- XL tasks not split
- Maker started without HUMAN GATE / `human-approved`
