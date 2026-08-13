"""Tests for merge: FF, two-parent, conflicts, missing ref, already up to date."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from frontend.merge import MergeConflictError
from frontend.operations import Operations

if TYPE_CHECKING:
    from pathlib import Path


class TestMerge:
    """Verify Operations.merge against BLRID-3 acceptance criteria."""

    def _ops(self, tmp_path: Path) -> Operations:
        with open(tmp_path / "base.txt", "w") as f:
            f.write("base\n")
        db_path = str(tmp_path / ".minigit" / "minigit.db")
        ops = Operations(str(tmp_path), db_path)
        ops.init_repo(author="Tester", message="initial")
        return ops

    def _commit_file(
        self, ops: Operations, repo: Path, path: str, content: str, message: str
    ) -> str:
        full = repo / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        ops.add(path)
        return ops.create_new_commit(message, author="Tester")

    def test_missing_source_ref_errors(self, tmp_path: Path) -> None:
        ops = self._ops(tmp_path)
        with pytest.raises(ValueError, match="does not exist"):
            ops.merge("no-such-branch")

    def test_already_up_to_date(self, tmp_path: Path) -> None:
        ops = self._ops(tmp_path)
        ops.create_branch("feature")
        ops.checkout_branch("main")
        tip_before = ops.db.get_ref("main")
        result = ops.merge("feature")
        assert result == tip_before
        assert ops.db.get_ref("main") == tip_before

    def test_fast_forward(self, tmp_path: Path) -> None:
        ops = self._ops(tmp_path)
        ops.create_branch("feature")
        self._commit_file(ops, tmp_path, "feat.txt", "f\n", "on feature")
        feature_tip = ops.db.get_ref("feature")
        ops.checkout_branch("main")
        result = ops.merge("feature")
        assert result == feature_tip
        assert ops.db.get_ref("main") == feature_tip
        commit = ops.get_commit(result)
        assert commit is not None
        assert commit.get("second_parent_hash") in (None, "")

    def test_two_parent_merge_clean(self, tmp_path: Path) -> None:
        ops = self._ops(tmp_path)

        ops.create_branch("feature")
        self._commit_file(ops, tmp_path, "feat.txt", "feature\n", "feature change")
        feature_tip = ops.db.get_ref("feature")

        ops.checkout_branch("main")
        self._commit_file(ops, tmp_path, "main.txt", "main\n", "main change")
        main_tip = ops.db.get_ref("main")

        merge_hash = ops.merge("feature")
        assert merge_hash not in (main_tip, feature_tip)
        commit = ops.get_commit(merge_hash)
        assert commit is not None
        assert commit["parent_hash"] == main_tip
        assert commit["second_parent_hash"] == feature_tip
        files = ops._flatten_tree(commit["tree_hash"])
        assert "feat.txt" in files
        assert "main.txt" in files
        assert "base.txt" in files
        assert ops.db.get_ref("main") == merge_hash

    def test_conflict_aborts_without_updating_tip(self, tmp_path: Path) -> None:
        ops = self._ops(tmp_path)
        ops.create_branch("feature")
        self._commit_file(ops, tmp_path, "base.txt", "feature-side\n", "feature edit")
        ops.checkout_branch("main")
        self._commit_file(ops, tmp_path, "base.txt", "main-side\n", "main edit")
        tip_before = ops.db.get_ref("main")

        with pytest.raises(MergeConflictError) as exc_info:
            ops.merge("feature")
        assert "base.txt" in exc_info.value.paths
        assert ops.db.get_ref("main") == tip_before

    def test_single_parent_commits_still_readable(self, tmp_path: Path) -> None:
        ops = self._ops(tmp_path)
        h = ops.db.get_ref("main")
        assert h
        c = ops.get_commit(h)
        assert c is not None
        assert c["parent_hash"] is None
        assert c.get("second_parent_hash") in (None, "")
