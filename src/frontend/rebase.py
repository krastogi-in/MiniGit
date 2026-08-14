"""Helpers for replaying one MiniGit branch onto another."""

from __future__ import annotations

from hashlib import sha256
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from frontend.operations import Operations


class RebaseConflictError(ValueError):
    """Raised when a commit cannot be replayed safely onto a new base."""


class RebaseEngine:
    """Replay the current branch's unique commits onto a target branch."""

    def __init__(self, operations: Operations) -> None:
        self.operations = operations

    def rebase_onto(self, target_branch: str) -> dict[str, Any]:
        """Rebase the current branch onto *target_branch*."""
        current_branch = self.operations.branch
        if current_branch == target_branch:
            raise ValueError("Cannot rebase a branch onto itself")

        current_head = self._get_branch_head(current_branch)
        target_head = self._get_branch_head(target_branch)
        split_point = self._find_split_point(current_head, target_head)
        if split_point is None:
            raise ValueError("Cannot rebase branches with unrelated history")
        if split_point == target_head:
            return self._result("up_to_date", current_branch, target_branch, current_head)
        if split_point == current_head:
            self.operations.db.set_ref(current_branch, target_head)
            return self._result("fast_forward", current_branch, target_branch, target_head)

        replay_commits = self._collect_replay_commits(current_head, split_point)
        new_head = target_head
        replayed = 0
        skipped = 0
        for commit in replay_commits:
            rebased_hash = self._replay_commit(commit, new_head)
            if rebased_hash is None:
                skipped += 1
                continue
            replayed += 1
            new_head = rebased_hash

        self.operations.db.set_ref(current_branch, new_head)
        return self._result(
            "rebased",
            current_branch,
            target_branch,
            new_head,
            replayed=replayed,
            skipped=skipped,
        )

    def _result(
        self,
        status: str,
        branch: str,
        target_branch: str,
        head: str,
        replayed: int = 0,
        skipped: int = 0,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "branch": branch,
            "target_branch": target_branch,
            "head": head,
            "replayed": replayed,
            "skipped": skipped,
        }

    def _get_branch_head(self, branch_name: str) -> str:
        commit_hash = self.operations.db.get_ref(branch_name)
        if not commit_hash:
            raise ValueError(f"Branch '{branch_name}' does not exist")
        return cast("str", commit_hash)

    def _find_split_point(self, current_head: str, target_head: str) -> str | None:
        target_ancestors: set[str] = set()
        commit_hash: str | None = target_head
        while commit_hash:
            target_ancestors.add(commit_hash)
            commit_hash = self._get_parent_hash(commit_hash)

        commit_hash = current_head
        while commit_hash:
            if commit_hash in target_ancestors:
                return commit_hash
            commit_hash = self._get_parent_hash(commit_hash)
        return None

    def _collect_replay_commits(self, current_head: str, split_point: str) -> list[dict[str, Any]]:
        replay_commits: list[dict[str, Any]] = []
        commit_hash = current_head
        while commit_hash != split_point:
            commit = self._get_commit(commit_hash)
            replay_commits.append(commit)
            parent_hash = commit["parent_hash"]
            if not parent_hash:
                raise ValueError("Could not find the split point while preparing replay")
            commit_hash = parent_hash
        replay_commits.reverse()
        return replay_commits

    def _get_parent_hash(self, commit_hash: str) -> str | None:
        return cast("str | None", self._get_commit(commit_hash)["parent_hash"])

    def _get_commit(self, commit_hash: str) -> dict[str, Any]:
        commit = self.operations.db.get_commit(commit_hash)
        if not commit:
            raise ValueError(f"Commit '{commit_hash}' could not be loaded")
        return cast("dict[str, Any]", commit)

    def _replay_commit(self, commit: dict[str, Any], new_parent_hash: str) -> str | None:
        parent_flat = self._flatten_commit(commit["parent_hash"])
        commit_flat = self._flatten_commit(commit["hash"])
        rebased_parent_flat = self._flatten_commit(new_parent_hash)
        rebased_flat = self._apply_delta(rebased_parent_flat, parent_flat, commit_flat)
        if rebased_flat == rebased_parent_flat:
            return None

        tree_hash = self.operations._build_tree_from_flat(rebased_flat)
        return self._store_replayed_commit(commit, tree_hash, new_parent_hash)

    def _flatten_commit(self, commit_hash: str | None) -> dict[str, str]:
        if commit_hash is None:
            return {}
        commit = self._get_commit(commit_hash)
        return cast("dict[str, str]", self.operations._flatten_tree(commit["tree_hash"]))

    def _apply_delta(
        self,
        base_flat: dict[str, str],
        parent_flat: dict[str, str],
        commit_flat: dict[str, str],
    ) -> dict[str, str]:
        rebased = dict(base_flat)
        changed_paths = sorted(set(parent_flat) | set(commit_flat))
        for path in changed_paths:
            parent_hash = parent_flat.get(path)
            commit_hash = commit_flat.get(path)
            if parent_hash == commit_hash:
                continue
            base_hash = rebased.get(path)
            if self._has_conflict(base_hash, parent_hash, commit_hash):
                raise RebaseConflictError(f"Cannot safely replay changes for '{path}'")
            if commit_hash is None:
                rebased.pop(path, None)
            else:
                rebased[path] = commit_hash
        return rebased

    def _has_conflict(
        self,
        base_hash: str | None,
        parent_hash: str | None,
        commit_hash: str | None,
    ) -> bool:
        if parent_hash is None:
            return base_hash not in (None, commit_hash)
        if commit_hash is None:
            return base_hash not in (None, parent_hash)
        return base_hash not in (parent_hash, commit_hash)

    def _store_replayed_commit(
        self,
        commit: dict[str, Any],
        tree_hash: str,
        parent_hash: str,
    ) -> str:
        content = (
            f"{tree_hash}{parent_hash}{commit['author']}{commit['message']}{commit['timestamp']}"
        )
        commit_hash = sha256(content.encode()).hexdigest()
        self.operations.db.store_commit(
            commit_hash,
            tree_hash,
            parent_hash,
            commit["author"],
            commit["message"],
            commit["timestamp"],
        )
        return commit_hash
