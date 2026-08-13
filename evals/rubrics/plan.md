# Rubric: plan

## Pass if

- [ ] `agent_space/<ISSUE-KEY>/tasks/plan.md` exists
- [ ] `agent_space/<ISSUE-KEY>/tasks/todo.md` exists with acceptance + verify per task
- [ ] Checkpoints defined
- [ ] Already-covered tasks marked reuse/verify vs build
- [ ] Notes PR branch `aiagent/<ISSUE-KEY>`
- [ ] After pass: harness sets `sdlc:agent-ready` + In Progress; posts idea/spec/plan as a **Jira comment** (does not overwrite Description); human approval via gate

## Fail if

- Tasks lack acceptance criteria
- XL tasks not split
- Maker started without HUMAN GATE / `sdlc:human-ready`
- Idea/spec/plan only in repo with no Jira review-package comment before HUMAN GATE
- Original ticket Description overwritten for SDLC artifacts
