"""Status helpers — compare HEAD, index (staging), and working tree."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from components.blob import Blob
from components.tree import Tree

if TYPE_CHECKING:
    from frontend.operations import Operations


@dataclass
class FileChange:
    """A path changed relative to HEAD or the index."""

    path: str
    status: str  # new | modified | deleted


@dataclass
class RepoStatus:
    """Three-tree status snapshot for the current branch."""

    branch: str
    head_commit: str | None
    staged: list[FileChange] = field(default_factory=list)
    unstaged: list[FileChange] = field(default_factory=list)
    untracked: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        """True when there are no pending changes."""
        return not self.staged and not self.unstaged and not self.untracked


def sync_branch_from_head(ops: Operations) -> None:
    """Set ops.branch from the HEAD ref when the repo is initialized."""
    head_ref = ops.db.get_ref("HEAD")
    if head_ref:
        ops.branch = head_ref


def walk_working_tree(repo_path: str) -> dict[str, str]:
    """Return {relative_path: blob_hash} for all non-ignored files under repo root."""
    result: dict[str, str] = {}
    _walk_dir(repo_path, repo_path, result)
    return result


def _walk_dir(repo_path: str, current: str, result: dict[str, str]) -> None:
    ignore_dirs = Tree.IGNORE_DIRS
    ignore_ext = Tree.IGNORE_EXTENSIONS
    for name in sorted(os.listdir(current)):
        if name in ignore_dirs:
            continue
        full = os.path.join(current, name)
        rel = os.path.relpath(full, repo_path)
        if os.path.isdir(full):
            _walk_dir(repo_path, full, result)
        elif os.path.isfile(full):
            _, ext = os.path.splitext(name)
            if ext.lower() in ignore_ext:
                continue
            with open(full) as f:
                result[rel] = Blob(f.read()).get_hash()


def _build_index(head: dict[str, str], staged: list[dict[str, str]]) -> dict[str, str]:
    """Apply staging entries onto HEAD to produce the effective index."""
    index = dict(head)
    for entry in staged:
        if entry["action"] == "add":
            index[entry["path"]] = entry["blob_hash"]
        elif entry["action"] == "delete":
            index.pop(entry["path"], None)
    return index


def _staged_changes(head: dict[str, str], index: dict[str, str]) -> list[FileChange]:
    changes: list[FileChange] = []
    all_paths = set(head) | set(index)
    for path in sorted(all_paths):
        head_hash = head.get(path)
        index_hash = index.get(path)
        if head_hash == index_hash:
            continue
        if head_hash is None:
            changes.append(FileChange(path, "new"))
        elif index_hash is None:
            changes.append(FileChange(path, "deleted"))
        else:
            changes.append(FileChange(path, "modified"))
    return changes


def _unstaged_changes(
    index: dict[str, str], working: dict[str, str]
) -> list[FileChange]:
    changes: list[FileChange] = []
    all_paths = set(index) | set(working)
    for path in sorted(all_paths):
        index_hash = index.get(path)
        work_hash = working.get(path)
        if index_hash == work_hash:
            continue
        if work_hash is None:
            changes.append(FileChange(path, "deleted"))
        else:
            changes.append(FileChange(path, "modified"))
    return changes


def _untracked_paths(
    head: dict[str, str],
    working: dict[str, str],
    staged_add_paths: set[str],
) -> list[str]:
    untracked: list[str] = []
    for path in sorted(working):
        if path in head or path in staged_add_paths:
            continue
        untracked.append(path)
    return untracked


def compute_repo_status(ops: Operations) -> RepoStatus:
    """Compare HEAD, staging index, and working tree for the current branch."""
    sync_branch_from_head(ops)
    branch = ops.branch
    head_commit = ops.db.get_ref(branch)
    head_files: dict[str, str] = {}
    if head_commit:
        commit = ops.db.get_commit(head_commit)
        if commit:
            head_files = ops._flatten_tree(commit["tree_hash"])

    staged_entries = ops.db.get_staged()
    index_files = _build_index(head_files, staged_entries)
    working_files = walk_working_tree(ops.repo_path)
    staged_add_paths = {
        e["path"] for e in staged_entries if e["action"] == "add"
    }

    return RepoStatus(
        branch=branch,
        head_commit=head_commit,
        staged=_staged_changes(head_files, index_files),
        unstaged=_unstaged_changes(index_files, working_files),
        untracked=_untracked_paths(head_files, working_files, staged_add_paths),
    )
