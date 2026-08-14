# Spec: Tag Support for MiniGit

**Issue:** [BLRID-14](https://redhat.atlassian.net/browse/BLRID-14) · **Idea:** [tag-support.md](../ideas/tag-support.md)

## Assumptions

- Annotated tags only (tagger + message + timestamp) — no separate lightweight-tag code path
- Tags stored in a new `tags` table, independent of `refs` (which stays branches/HEAD-only)
- Tag names reuse the existing ref-name pattern (`^[A-Za-z0-9_.\-/]+$`) and must not equal
  an existing branch name
- No new content-addressable object type; a tag is a named pointer + metadata row, not a
  hashed object referenced by other objects
- BLRID-15 (exact duplicate, untouched) will be closed by the human once this ships —
  not touched by this spec

## Objective

Let a MiniGit user create an immutable, named pointer to a specific commit (a tag),
list existing tags, delete a tag, and reference a tag anywhere a commit hash or branch
name is currently accepted for read operations (`show`, `diff`).

## Commands

```bash
# CLI
python src/cli.py tag <name> [<commit_hash>]   # create; defaults to current branch tip
python src/cli.py tag                          # list all tags
python src/cli.py tag -d <name>                # delete

# Verify
make check      # lint + typecheck + test
make test       # pytest only, faster loop
```

## Project structure (touched files)

```
src/backend/sqlite_client.py   # new `tags` table + store_tag/get_tag/get_all_tags/delete_tag
src/frontend/operations.py     # new Operations.create_tag / delete_tag / get_all_tags /
                                #   _resolve_ref (extend existing hash/branch resolution to tags)
src/cli.py                     # new `tag` subcommand (create / list / delete)
src/app.py                     # new routes: list tags, create tag (POST), delete tag (POST)
src/templates/                 # tag list partial/section (repo overview or dedicated page)
tests/test_sqlite_client.py    # tags table CRUD + validation
tests/test_operations.py       # create/list/delete tag; collision + duplicate rejection;
                                #   resolving a tag name in show/diff-equivalent paths
tests/test_tags.py             # new file — full tag behavior surface (see Testing Strategy)
```

## Code style

Follow [AGENTS.md](../../../AGENTS.md):
- `components/` must not import `backend/` or `frontend/`; `backend/` must not import
  `frontend/` or `components/`; this feature only touches `backend/` and `frontend/`
  (tags do not need a new `components/` object — no new hash-derived class required)
- Type annotations on all public functions
- Parameterized SQL only (no f-strings in queries) — mirror existing `_validate_hash`,
  `_validate_ref_name`, `_validate_str` patterns already in `sqlite_client.py`
- Functions under 50 lines; files under 300 lines (watch `sqlite_client.py` and
  `operations.py` growth — extract a helper module if either approaches the limit)

## Testing strategy

New `tests/test_tags.py` (pytest, `tmp_path` fixture per [AGENTS.md](../../../AGENTS.md)):

| Case | Assert |
|------|--------|
| Create tag against current branch tip (no explicit hash) | Tag resolves to branch tip commit |
| Create tag against explicit commit hash | Tag resolves to that commit, independent of branch tip |
| List tags | Returns all created tags with name + commit hash + tagger/message/timestamp |
| Delete tag | Tag no longer resolves; re-creating same name succeeds |
| Duplicate tag name | Raises `ValueError`, no overwrite |
| Invalid tag name (bad pattern) | Raises `ValueError` before any DB write |
| Tag name collides with existing branch name | Raises `ValueError` |
| Tag is immutable across new commits | After a new commit on the tagged branch, tag still points to original commit |
| Resolve tag name in `show`/diff-equivalent operation | Same result as passing the commit hash directly |
| Delete nonexistent tag | Raises `ValueError` |

Extend `tests/test_sqlite_client.py` for `tags` table CRUD + validation (mirrors existing
`refs`/`commits` test patterns already in that file).

Extend `tests/test_operations.py` only if `Operations` gains shared resolution helpers
that existing tests should cover (e.g. a generalized "resolve ref-or-hash" helper if it's
reused beyond tags).

## Boundaries

**Always:**
- Validate tag names with the existing `_REF_NAME` pattern before any DB write
- Reject tag names colliding with existing branch names
- Run `make check` before considering any task done

**Ask first:**
- Any new third-party dependency
- Any change to the existing `refs` or `commits` table schema (this feature is additive-only)

**Never:**
- Allow a tag to be silently overwritten by re-creating with the same name (must error)
- Introduce lightweight (non-annotated) tags as a second code path in v1
- Overwrite the original Jira Description with SDLC artifacts (comments only)

## Success criteria

- [ ] `tags` table exists with tagger/message/timestamp metadata
- [ ] CLI `tag` subcommand: create, list, delete
- [ ] Flask routes: list, create (POST), delete (POST)
- [ ] Tag resolvable in `show` and `diff` (or their web-UI equivalents) alongside commit
      hash / branch name
- [ ] All acceptance criteria in the Jira ticket satisfied
- [ ] `tests/test_tags.py` covers the full table in Testing Strategy above
- [ ] `make check` passes

## Open questions

- Should tag creation be exposed on the repo overview page, or does it warrant a
  dedicated `/repo/<name>/tags` page? (Left to planning phase — either satisfies the AC;
  a dedicated page scales better if tag count grows.)
- None of the above block starting the plan phase; they are UI-layout details, not
  scope/AC questions.
