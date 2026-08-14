# Todo: BLRID-11 status

## 1. HEAD persistence (build)
- **Acceptance:** New `Operations(repo)` loads branch from HEAD; `checkout_branch` updates HEAD ref; init still sets HEAD=main.
- **Verify:** unit/integration tests create repo, checkout other branch, new Operations sees that branch.
- **Files:** `src/frontend/operations.py`, possibly tests
- **Size:** M

## 2. Operations.status() (build / reuse staged)
- **Acceptance:** Returns dict with `branch` and `staged` (list of path/action/hash); empty staged OK.
- **Verify:** call after init / after stage
- **Files:** `src/frontend/operations.py`
- **Size:** S

## 3. Tests (build)
- **Acceptance:** tests for branch display, empty staged, staged with files, bad/missing repo
- **Verify:** `pytest tests/test_status.py -q`
- **Files:** `tests/test_status.py`
- **Size:** M

## 4. CLI (build)
- **Acceptance:** `minigit status` prints branch + staged or “nothing staged”; bad repo non-zero exit
- **Verify:** CLI tests or invoking via pytest helpers
- **Files:** `src/cli.py`
- **Size:** S

## 5. Flask UI (build)
- **Acceptance:** Status info visible for a repo (section or page) using Operations.status()
- **Verify:** route smoke / template render test if present pattern exists
- **Files:** `src/app.py`, `src/templates/*`
- **Size:** S

## 6. Close-out (verify)
- **Acceptance:** Ticket AC met; `make check`; PR `aiagent/BLRID-11`
- **Verify:** `make check`; `gh pr create` (or push + PR)
- **Files:** n/a
- **Size:** S
