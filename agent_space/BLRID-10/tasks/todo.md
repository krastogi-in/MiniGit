# Todo: BLRID-10 Stash

- [ ] **T1** Schema + stash CRUD (`sqlite_client`)
  - Acceptance: table created on init; insert/list/delete-top; parameterized SQL; validated inputs
  - Verify: targeted unit tests or ops smoke; no f-string SQL
  - Files: `src/backend/sqlite_client.py`, `tests/…`
  - Size: M · **build** (reuse DB patterns)

- [ ] **T2** Operations: `stash_push`, `stash_list`, `stash_pop`
  - Acceptance: push clears staging; list newest-first; pop restores staging/WD or aborts on conflict leaving stash
  - Verify: manual tmp_path script or tests in T3
  - Files: `src/frontend/operations.py`
  - Size: L · **build** (reuse stage/blob/flatten)

- [ ] **T3** Tests
  - Acceptance: empty push, happy push/list/pop, empty pop, conflict abort
  - Verify: `pytest tests/ -k stash -v` then full suite
  - Files: `tests/test_stash.py` (or similar)
  - Size: M · **build**

- [ ] **T4** CLI
  - Acceptance: `python src/cli.py stash …` push/list/pop documented in help
  - Verify: CLI against tmp repo
  - Files: `src/cli.py`
  - Size: S · **build**

- [ ] **T5** Flask UI
  - Acceptance: stash / list / pop from working-dir (or staging) view with clear errors
  - Verify: route smoke or UI manual; no XSS of messages
  - Files: `src/app.py`, `src/templates/…`
  - Size: M · **build**

- [ ] **T6** README + verify gate
  - Acceptance: README shows stash commands; `make check` green
  - Verify: `make check`
  - Files: `README.md`
  - Size: S · **build**

**Checkpoint:** every 2–3 tasks; PR branch `aiagent/BLRID-10` at implement.
