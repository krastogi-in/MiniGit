# Design Intent — MiniGit Object Model

## Overview

This document describes the design preconditions, invariants, and postconditions
that govern MiniGit's core object model.

## Preconditions

### Blob Creation
- Input `data` must be a valid UTF-8 string (binary files are excluded by extension)
- `data` length must not exceed 10,000,000 characters

### Tree Construction
- `path` must be a valid, existing filesystem directory
- Directories in `IGNORE_DIRS` are skipped (prevents infinite recursion on `.minigit`)
- Files with extensions in `IGNORE_EXTENSIONS` are skipped

### Commit Creation
- A valid tree must exist (constructed from the working directory)
- `author` must be a non-empty string (defaults to `$USER` env var)
- `message` must be a non-empty string (defaults to "No message")
- `parent_commit_pointer` is either `None` (root commit) or a valid commit hash

### Staging
- File must exist in the working directory for `add` action
- File must exist in the current commit tree for `delete` action
- At least one staged entry must exist before creating a commit

## Invariants

1. **Hash determinism**: Given identical content, the hash is always identical
2. **Immutability**: Once stored, blobs and trees are never modified
3. **Referential integrity**: Every commit's `tree_hash` exists in the trees table
4. **Single HEAD**: Exactly one HEAD ref exists, pointing to the current branch name
5. **Branch validity**: Every branch ref points to a valid commit hash
6. **Content-addressable dedup**: Two identical blobs share one database row

## Postconditions

### After `init_repo()`
- `.minigit/minigit.db` exists with all 5 tables created
- A "main" branch ref exists pointing to the initial commit
- HEAD ref points to "main"
- All files in the working directory are stored as blobs

### After `create_new_commit()`
- A new commit row exists with the correct parent hash
- The current branch ref is updated to the new commit hash
- The staging table is cleared
- All staged blobs exist in the blobs table

### After `create_branch()`
- A new ref exists with the branch name
- The new ref points to the same commit as the source branch

## Error Handling Strategy

All errors are raised as Python exceptions:
- `ValueError` — invalid input (bad hash format, duplicate branch name)
- `TypeError` — wrong argument type
- `FileNotFoundError` — file not found during staging

No silent failures. The CLI and web UI catch exceptions and display user-friendly messages.
