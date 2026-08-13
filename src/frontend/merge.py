"""Merge helpers for MiniGit — FF, two-parent merge, conflict abort."""

from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING, Any

from components.commit import Commit

if TYPE_CHECKING:
    from frontend.operations import Operations


class MergeConflictError(ValueError):
    """Raised when merge aborts due to conflicting path changes."""

    def __init__(self, paths: list[str]) -> None:
        self.paths: list[str] = sorted(paths)
        joined = ", ".join(self.paths)
        super().__init__(f"Merge conflict in: {joined}")


def merge_branch(
    ops: Operations,
    source_ref: str,
    author: str | None = None,
    message: str | None = None,
) -> str:
    """Merge *source_ref* into the current branch tip.

    Returns the resulting tip commit hash (unchanged tip, FF tip, or new merge).
    """
    source_tip = ops.db.get_ref(source_ref)
    if not source_tip:
        raise ValueError(f"Branch '{source_ref}' does not exist")

    head_tip = ops.db.get_ref(ops.branch)
    if not head_tip:
        raise ValueError(f"Current branch '{ops.branch}' has no commits")

    if source_tip == head_tip:
        return str(source_tip)

    ancestor = _find_common_ancestor(ops, head_tip, source_tip)
    if ancestor is None:
        raise ValueError("Unrelated histories: no common ancestor")

    if ancestor == head_tip:
        ops.db.set_ref(ops.branch, source_tip)
        return str(source_tip)

    if ancestor == source_tip:
        return str(head_tip)

    head_commit = ops.db.get_commit(head_tip)
    source_commit = ops.db.get_commit(source_tip)
    base_commit = ops.db.get_commit(ancestor)
    if not head_commit or not source_commit or not base_commit:
        raise ValueError("Required commit does not exist")

    base_files = ops._flatten_tree(base_commit["tree_hash"])
    ours = ops._flatten_tree(head_commit["tree_hash"])
    theirs = ops._flatten_tree(source_commit["tree_hash"])
    merged, conflicts = _three_way_merge(base_files, ours, theirs)
    if conflicts:
        raise MergeConflictError(conflicts)

    if author is None:
        author = os.getenv("USER", "unknown")
    if message is None:
        message = f"Merge branch '{source_ref}'"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tree_hash = ops._build_tree_from_flat(merged)
    commit_hash = Commit.hash_from_fields(
        tree_hash,
        head_tip,
        author,
        message,
        timestamp,
        second_parent_hash=source_tip,
    )
    ops.db.store_commit(
        commit_hash,
        tree_hash,
        head_tip,
        author,
        message,
        timestamp,
        second_parent_hash=source_tip,
    )
    ops.db.set_ref(ops.branch, commit_hash)
    return str(commit_hash)


def _parent_hashes(commit: dict[str, Any]) -> list[str]:
    parents: list[str] = []
    p1 = commit.get("parent_hash")
    if p1:
        parents.append(p1)
    p2 = commit.get("second_parent_hash")
    if p2:
        parents.append(p2)
    return parents


def _find_common_ancestor(ops: Operations, a: str, b: str) -> str | None:
    """Return a common ancestor hash, preferring the newest shared commit."""
    ancestors_a = _ancestor_set(ops, a)
    queue = [b]
    seen: set[str] = set()
    while queue:
        current = queue.pop(0)
        if current in seen:
            continue
        seen.add(current)
        if current in ancestors_a:
            return current
        commit = ops.db.get_commit(current)
        if not commit:
            continue
        queue.extend(_parent_hashes(commit))
    return None


def _ancestor_set(ops: Operations, tip: str) -> set[str]:
    result: set[str] = set()
    queue = [tip]
    while queue:
        current = queue.pop(0)
        if current in result:
            continue
        result.add(current)
        commit = ops.db.get_commit(current)
        if not commit:
            continue
        queue.extend(_parent_hashes(commit))
    return result


def _three_way_merge(
    base: dict[str, str],
    ours: dict[str, str],
    theirs: dict[str, str],
) -> tuple[dict[str, str], list[str]]:
    """Merge flat path→blob maps. Returns (merged, conflict_paths)."""
    all_paths = set(base) | set(ours) | set(theirs)
    merged: dict[str, str] = {}
    conflicts: list[str] = []
    for path in all_paths:
        b = base.get(path)
        o = ours.get(path)
        t = theirs.get(path)
        if o == t:
            if o is not None:
                merged[path] = o
            continue
        if o == b:
            if t is not None:
                merged[path] = t
            continue
        if t == b:
            if o is not None:
                merged[path] = o
            continue
        conflicts.append(path)
    return merged, conflicts
