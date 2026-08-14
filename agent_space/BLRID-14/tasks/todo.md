# Todo: Tag Support for MiniGit

**Issue:** [BLRID-14](https://redhat.atlassian.net/browse/BLRID-14) · **Plan:** [plan.md](plan.md)

- [ ] Task 1: `tags` table + SQLiteClient CRUD
  - Acceptance: table created via `_init_tables`; `store_tag`/`get_tag`/`get_all_tags`/`delete_tag`
    implemented with validation (`_validate_ref_name`, `_validate_hash`, `_validate_str`);
    duplicate name on `store_tag` raises (no silent overwrite)
  - Verify: `pytest tests/test_sqlite_client.py -k tag`
  - Files: `src/backend/sqlite_client.py`, `tests/test_sqlite_client.py`
  - Size: M

- [ ] Task 2: `Operations.create_tag` / `delete_tag` / `get_all_tags`
  - Acceptance: defaults to branch tip when no hash given; rejects branch-name collision,
    duplicate tag name, unknown commit hash; `delete_tag` raises on missing tag
  - Verify: `pytest tests/test_tags.py -k "create or delete or list"`
  - Files: `src/frontend/operations.py`, `tests/test_tags.py`
  - Size: M

- [ ] Task 3: `resolve_ref()` helper (tag resolution in `show`/`diff` paths)
  - Acceptance: resolves commit hash, branch name, or tag name to a commit hash; wired
    into existing read paths that accept "a hash or branch name"
  - Verify: `pytest tests/test_tags.py -k resolve`
  - Files: `src/frontend/operations.py`, `tests/test_tags.py`
  - Size: S

## Checkpoint 1 (after Task 2/3)

- [ ] `pytest tests/test_sqlite_client.py tests/test_tags.py` green
- [ ] Core tag semantics (create/list/delete/resolve/collision) proven before touching surfaces

- [ ] Task 4: CLI `tag` subcommand
  - Acceptance: `minigit tag <name> [<commit_hash>]` create; `minigit tag` list;
    `minigit tag -d <name>` delete; error style matches `cmd_branch`/`cmd_checkout`
  - Verify: manual smoke (no existing CLI test harness)
  - Files: `src/cli.py`
  - Size: S

- [ ] Task 5: Flask routes + template
  - Acceptance: list/create/delete tag routes; flash messages match stage/unstage pattern
  - Verify: manual smoke (no existing Flask test harness)
  - Files: `src/app.py`, `src/templates/`
  - Size: M

## Checkpoint 2 (after Task 5)

- [ ] Both surfaces (CLI + web) wired and manually smoke-tested
- [ ] Ready for final AC verification pass

- [ ] Task 6: AC close-out
  - Acceptance: every Jira acceptance criterion checked off; `make check` green
  - Verify: `make check`
  - Files: — (verification only)
  - Size: S

## PR

Branch: `aiagent/BLRID-14` — opens after Task 6, for human PR-gate review.
