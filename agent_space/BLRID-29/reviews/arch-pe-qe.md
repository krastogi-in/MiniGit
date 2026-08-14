# Review: BLRID-29 safe reset — Architecture / PE / QE

**PR:** https://github.com/krastogi-in/MiniGit/pull/21  
**Diff:** `aiagent/BLRID-29` vs `main`  
**Checker role:** advisory revive (implementation gate not yet moved to Review status)

## Verdict (overall)

**Conditional approve** — core design matches the ticket and is a solid teaching feature. Fix or track the Medium items before treating as ship-ready; none are Critical ship-blockers for an Innovation Day MVP if accepted as known limits.

---

## 1) Architecture review

### What works

- **Layering honored:** algorithm lives in `frontend/operations.py`; CLI is thin; no `components`↔`backend` violations (`lint-imports` KEPT).
- **No schema migration:** tip move is a ref update — fits MiniGit’s SQLite model.
- **Preview/apply split:** `preview_reset` + `reset(..., dry_run|confirm)` is a clean API for CLI/web reuse.
- **Safety invariant:** ancestor-only targets avoid arbitrary history jumps (stricter than “any commit,” better for learners).

### Findings

| Sev | Finding | Remedy |
|-----|---------|--------|
| Medium | `operations.py` now **well over** AGENTS.md ~300-line file budget after +150 LOC | Extract `reset.py` helpers (preview/sync/dirty) under `frontend/` or `frontend/reset_ops.py` |
| Medium | Hash regex duplicated (`_HEX_HASH` here vs `backend.sqlite_client._validate_hash`) | Call shared validate (export a public helper) or reuse DB get + format error |
| Low | `_sync_working_tree` is a **partial checkout** capability buried inside reset | When real checkout lands, share one sync primitive to avoid two disk writers |
| Low | Soft mode keeps MiniGit **staging rows** as-is (Git soft keeps index); semantics differ slightly from Git | Document in CLI help / README snippet as MiniGit-soft |
| Info | Does not update `HEAD` symbolic ref | Consistent with current broken-ish checkout; tip update on branch ref is enough for this ticket |

### Architecture score: **B+**

---

## 2) PE (product engineering) review

### AC vs delivery

| AC | Status |
|----|--------|
| `--dry-run` preview of commits leaving tip | Met |
| soft / mixed / hard; default mixed | Met |
| Unknown hash → error; tip unchanged | Met |
| hard + dirty without `--force` aborts | Met |
| Tests for main paths | Met (ops); CLI smoke only dry-run |
| CLI required; web optional | Met (web deferred — called out) |
| `make check` | **Partial** — feature tests green; repo-wide coverage gate already failing on `main` (~44%) |

### Findings

| Sev | Finding | Remedy |
|-----|---------|--------|
| Medium | CLI with **both** `--dry-run` and `--yes` silently prefers dry-run | Mutually exclusive group or error if both set |
| Medium | Preview prints **counts** for dirty/hard impact, not path names (hard to act on) | Print top N paths (e.g. 10) in `_print_reset_preview` |
| Low | No user-facing note that target must be an **ancestor** until error | Add to `--help` / dry-run footer |
| Low | Web confirm UI deferred | OK for MVP; file follow-up or checkbox in ticket |
| Info | Value prop (safe undo without silent data loss) is clear and demoable | Keep `--dry-run` in README quick start when merging |

### PE score: **B+**

---

## 3) QE (quality engineering) review

### Covered well

- Dry-run leaves tip unchanged  
- Soft retains staging; mixed clears staging  
- Hard restores file content; dirty abort without force  
- Unknown hash; non-ancestor; missing confirm  

### Gaps / risks

| Sev | Finding | Test / fix |
|-----|---------|------------|
| Medium | No test for **invalid hash format** (not 64 hex) vs unknown-but-valid hex | `pytest.raises(..., match="Invalid commit hash")` with `"abc"` |
| Medium | No CLI test for **`--yes` apply** or error exits (`sys.exit(1)`) | Extend `test_cli_reset.py` |
| Medium | Hard sync: `os.makedirs(... or ".")` can target **cwd** if dirname empty | Guard: only makedirs when `dirname` non-empty |
| Low | Nested delete leaves **empty directories** on disk | Optional rmdir cleanup; or document |
| Low | Dirty check assumes UTF-8 text files (matches Blob model) | OK; note if binary support arrives |
| Low | No test tip == target (no-op preview / apply) | Add explicit no-op case |
| Low | `test_hard_syncs_working_tree` always passes `force=True` even when clean | Assert clean path works **without** force |
| Info | Repo `cov-fail-under=60` fails with `app.py`/`cli.py` at 0% even on `main` | Separate chore ticket; not introduced solely by reset |

### QE score: **B**

---

## Five-axis checker summary (sdlc rubric style)

| Axis | Sev | Note |
|------|-----|------|
| Correctness | Medium | Core paths correct; dual-flag CLI + makedirs edge |
| Tests | Medium | Strong ops suite; thin CLI / format / no-op gaps |
| Security | Low | Hash validated; paths from stored trees (no user path injection on sync) |
| Maintainability | Medium | File size / duplicated hash validation |
| Requirements | Low | Ticket MVP met; web optional deferred honestly |

**Critical:** none  

---

## Recommended follow-ups (priority)

1. Print path lists in preview (PE)  
2. Reject `--dry-run` + `--yes` together (PE/QE)  
3. Fix `_sync_working_tree` dirname guard (QE)  
4. Add invalid-hash + CLI `--yes` + hard-without-force-when-clean tests (QE)  
5. Split reset helpers out of `operations.py` (Architecture)

---

## Ship recommendation

**OK to merge for Innovation Day MVP** after human PR review, with follow-ups tracked — **or** land a small fixup commit for items 1–3 first if you want a tighter bar.

---

## False-positive audit (re-checked against code)

| Original finding | Verdict | Why |
|------------------|---------|-----|
| `makedirs(... or ".")` can write via cwd | **False positive (overstated)** | For any real tree path, `os.path.join(repo_path, path)` has dirname ≥ `repo_path` (e.g. `README.md` → `/tmp/repo`). `or "."` is unreachable with MiniGit tree paths. Keep only as Low defensive nit if desired. |
| Coverage / `make check` broken **because of this PR** | **False positive (cause)** | `main` already ~44% with `app.py`/`cli.py` at 0%. Reset did not introduce the gate failure (it only adds more uncovered CLI lines). |
| “Does not update HEAD” as a reset defect | **False positive (as bug)** | `HEAD` stores the branch *name*; reset correctly updates the branch tip via `set_ref(self.branch, …)`. No HEAD rewrite needed. |
| Soft ≠ Git soft | **Not FP, but not a defect** | Intentional MiniGit staging-table model; document only. |
| Hard test always uses `force=True` | **Not a product bug** | Clean hard works without force in code; this is a **test-gap** only. |
| `--dry-run` + `--yes` prefers dry-run | **True** | Flags not mutually exclusive; silent preference is real UX ambiguity. |
| Preview counts not paths (dirty/hard) | **True** | Commits *are* listed; dirty/hard path names are not. |
| File >300 lines / duplicated hash regex | **True** | Style/maintainability, not runtime bugs. |
| Missing invalid-hash / CLI `--yes` tests | **True** | Coverage gaps, not proven production failures. |
| Empty dirs left after hard delete | **True (Low)** | Real leftover dirs possible. |
| Ancestor only in help | **True (Low)** | Docs gap. |

### Revised top actions (after FP filter)

1. Still worth: preview path names; reject or clarify `--dry-run`+`--yes`.
2. Optional: extra tests (invalid hash, CLI apply, hard without force when clean).
3. Drop as blockers: cwd/`makedirs` scare, “HEAD not updated”, “PR broke coverage.”
