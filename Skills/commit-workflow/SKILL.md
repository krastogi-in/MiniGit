---
name: commit-workflow
description: >-
  Stage, commit, and push code changes with explicit human approval gates.
  Enforces keyword authorization, explicit-path staging, proper commit message
  formatting, and ops follow-up conventions. Use when committing code, preparing
  a commit, writing commit messages, or pushing to remote.
---

# Commit Workflow

Git operations are **irreversible once pushed**. This skill enforces explicit
human authorization at every step.

## Keyword gates

| Action | User must say | Never do without |
|--------|---------------|------------------|
| Commit | `"commit"` | Explicit keyword |
| Push | `"push"` | Separate explicit keyword |
| Force push | `"force push"` | Almost never — warn first |
| Amend | `"amend"` | Only if HEAD is unpushed and user asks |

**Never** commit on implication. **Never** push on implication. These are
separate authorizations.

## Staging protocol

1. Run `git status -sb` + `git diff --stat` to show what changed
2. Stage **explicit file paths** — never `git add .` or `git add -A`
3. Exclude from staging:
   - `.env`, credentials, secrets
   - `.cursor/` drift, IDE config
   - Scratch files, `agent_space/` artifacts (unless the phase requires it)
   - `__pycache__/`, `.pyc`, build artifacts
4. Present the staged file list to the user

## Commit message format

```
<area>: <imperative summary> (<=72 chars)

- What changed and why (3–6 bullets)
- What is deferred to later phases

Jira: <ISSUE-KEY> (if applicable)
```

Use a HEREDOC to pass the message:

```bash
git commit -m "$(cat <<'EOF'
area: summary here

- bullet one
- bullet two

Jira: ISSUE-KEY
EOF
)"
```

## Workflow

1. **Show** `git status` + `git diff --stat`
2. **Stage** explicit paths — present the list
3. **Draft** commit message — show to user
4. **Wait** for the user to say `"commit"`
5. **Execute** the commit
6. **Verify** with `git log -1 --oneline` and `git status`
7. If push is needed: **ask separately**, wait for `"push"`

## Hook failures

If a pre-commit hook fails:
- **Fix** the issue (lint error, test failure, etc.)
- Create a **new commit** — never `--no-verify`, never amend a failed commit

## Protected branches

**Never** push directly to `main`, `dev`, or release branches without explicit
user instruction. Prefer feature branches and PRs.

## Deterministic

- [ ] `git status` shown before staging
- [ ] Explicit file paths staged (no wildcards)
- [ ] Commit message shown and approved
- [ ] User said `"commit"` before `git commit`
- [ ] User said `"push"` before `git push` (if applicable)
- [ ] No `--no-verify` or `--force` without explicit ask
- [ ] Post-commit verification shown

## What You Are NOT

- You are NOT authorized to push without permission
- You are NOT allowed to bypass hooks
- You are NOT allowed to work on protected branches without explicit instruction
