# Todo: BLRID-22

- [ ] **T1** Backend clone_count  
  - **Acceptance:** `get_clone_count()` returns 0 by default; `increment_clone_count()` persists +1  
  - **Verify:** pytest targeting SQLiteClient meta APIs  
  - **Files:** `src/backend/sqlite_client.py`, tests  

- [ ] **T2** `clone_repo` operation  
  - **Acceptance:** Copies MiniGit repo to empty dest; increments source counter; errors on missing source / existing dest repo without mutating counter  
  - **Verify:** Operations tests with `tmp_path`  
  - **Files:** `src/frontend/operations.py` and/or `src/frontend/clone.py`  

- [ ] **T3** CLI  
  - **Acceptance:** `minigit clone` / `clone-stats` wired; prints count  
  - **Verify:** CLI smoke via pytest or subprocess in tests  
  - **Files:** `src/cli.py`  

- [ ] **T4** Test suite  
  - **Acceptance:** success, second clone count=2, missing source, bad dest  
  - **Verify:** `make test` / `make check`  
  - **Files:** `tests/test_clone.py`  

- [ ] **T5** (optional) Flask clone count display  
  - **Acceptance:** count visible on repo page OR skipped with note in PR  
  - **Verify:** manual / light test if implemented  
  - **Files:** `src/app.py`, templates  

## Checkpoint

After T1–T4 green: push `aiagent/BLRID-22`, open PR, set `sdlc:agent-approved` (post human-ready gate).
