---
name: diff-preview
description: >-
  Show proposed code changes as diffs file-by-file and wait for user approval
  before applying each change. Use when implementing features, making code
  changes, or when a maker agent needs to present changes for review before
  applying them.
---

# Diff Preview

Present every proposed file change as a unified diff and **wait for explicit
approval** before applying it. No silent multi-file edits.

## When to use

- During `incremental-implementation` (maker phase)
- Any time code files are being modified or created
- Before applying changes suggested during `code-review-and-quality` fixes

## Workflow (per file)

1. **Read** the current file in full
2. **Present** the change as a unified-diff preview (see format below)
3. **Ask:** `Apply this change to <file path>?`
4. **Wait** for approval — acceptable responses:
   `yes`, `ok`, `approve`, `apply`, `go ahead`, `lgtm`, `y`
5. **Apply** the change only after approval
6. **Lint** the changed file (`ReadLints`)
7. Move to the next file

## Diff format

Use unified-diff style with 3–5 lines of context:

```
File: <relative path>
---
- removed line
+ added line
  context line
```

For new files, show the full content under `+ (new file)`.

## Rules

- **Never batch-apply** changes across multiple files without per-file approval
- **Never skip** the diff presentation step
- If the user says **no / reject / change**, adjust the diff based on
  feedback and re-present — do not apply the rejected version
- **Batch override:** if the user says `"apply all remaining"`, you may still
  show each diff but skip the wait between files
- After all files are applied, present a **closing summary**: files changed,
  files added, total lines modified

## Deterministic

- [ ] Every modified/created file shown as diff before edit
- [ ] Approval received per file (or batch override active)
- [ ] Lint clean after each apply
- [ ] Closing summary presented

## What You Are NOT

- You are NOT a decision-maker — the human decides what gets applied
- You are NOT a shortcut — never skip preview even for "obvious" changes
