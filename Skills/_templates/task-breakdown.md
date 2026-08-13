# Task Breakdown: {Feature Name}

**Issue:** {ISSUE-KEY}  
**Design doc:** `agent_space/{ISSUE-KEY}/specs/{slug}.md`  
**Date:** {YYYY-MM-DD}

---

## Phase 1: {Phase Name}

**Effort:** S/M/L  
**Dependencies:** none | Phase N

| Task | Description | Files | Complexity | Status |
|------|-------------|-------|------------|--------|
| T1.1 | ... | `src/...` | S | pending |
| T1.2 | ... | `src/...`, `tests/...` | M | pending |

**Checkpoint:** {what to verify after this phase}

## Phase 2: {Phase Name}

**Effort:** S/M/L  
**Dependencies:** Phase 1

| Task | Description | Files | Complexity | Status |
|------|-------------|-------|------------|--------|
| T2.1 | ... | ... | S | pending |

**Checkpoint:** {what to verify}

---

## Summary

| Phase | Tasks | Files | Effort |
|-------|-------|-------|--------|
| 1 | N | N | S/M/L |
| 2 | N | N | S/M/L |
| **Total** | **N** | **N** | **M** |

## Parallelism

Which phases or tasks can run concurrently:
- Phase 1 tasks are sequential (T1.1 before T1.2)
- Phase 2 can start after Phase 1 checkpoint passes
