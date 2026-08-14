# Agent run artifacts

Per-ticket scratch for the AI SDLC inner loop. **Not product docs** — do not put factory run output under `docs/` or repo-root `tasks/`.

## Layout

Each Jira issue gets a directory named by its key:

```
agent_space/<ISSUE-KEY>/
  ideas/      # idea-refine output
  specs/      # spec-driven-development output
  tasks/      # plan.md, todo.md
  reviews/    # checker notes (optional)
```

Product code and tests stay in `src/` and `tests/`. People guides stay in `docs/ai-sdlc/`.

## Git

Keep this README tracked. Optionally ignore local ticket runs by uncommenting `agent_space/*/` in `.gitignore`.
