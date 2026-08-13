# Rubric: implement

## Pass if

- [ ] `aiagent-ready` + `human-approved` present before coding
- [ ] Changes map to approved tasks
- [ ] Branch `aiagent/<ISSUE-KEY>` + GitHub PR opened/updated
- [ ] `aiagent-approved` set when PR ready for human
- [ ] `make check` green (or documented equivalent)
- [ ] Scope discipline (no drive-by refactors)

## Fail if

- Coding without gate labels
- Broken build between slices left unresolved
- Maker self-approved without checker path planned
- No PR for human review when code changed
