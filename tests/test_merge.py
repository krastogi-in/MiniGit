"""Tests for merge: FF, two-parent, conflicts, missing ref, already up to date."""

from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from frontend.merge import MergeConflictError
from frontend.operations import Operations


class TestMerge:
    """Verify Operations.merge against BLRID-2 acceptance criteria."""

    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "base.txt"), "w") as f:
            f.write("base\n")
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        shutil.rmtree(self.tmpdir)

    def _ops(self) -> Operations:
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="initial")
        return ops

    def _commit_file(self, ops: Operations, path: str, content: str, message: str) -> str:
        full = os.path.join(self.tmpdir, path)
        parent = os.path.dirname(full)
        if parent and parent != self.tmpdir:
            os.makedirs(parent, exist_ok=True)
        with open(full, "w") as f:
            f.write(content)
        ops.add(path)
        return ops.create_new_commit(message, author="Tester")

    def test_missing_source_ref_errors(self) -> None:
        ops = self._ops()
        with pytest.raises(ValueError, match="does not exist"):
            ops.merge("no-such-branch")

    def test_already_up_to_date(self) -> None:
        ops = self._ops()
        ops.create_branch("feature")
        ops.checkout_branch("main")
        tip_before = ops.db.get_ref("main")
        result = ops.merge("feature")
        assert result == tip_before
        assert ops.db.get_ref("main") == tip_before

    def test_fast_forward(self) -> None:
        ops = self._ops()
        ops.create_branch("feature")
        self._commit_file(ops, "feat.txt", "f\n", "on feature")
        feature_tip = ops.db.get_ref("feature")
        ops.checkout_branch("main")
        result = ops.merge("feature")
        assert result == feature_tip
        assert ops.db.get_ref("main") == feature_tip
        commit = ops.get_commit(result)
        assert commit is not None
        assert commit.get("second_parent_hash") in (None, "")

    def test_two_parent_merge_clean(self) -> None:
        ops = self._ops()

        ops.create_branch("feature")
        self._commit_file(ops, "feat.txt", "feature\n", "feature change")
        feature_tip = ops.db.get_ref("feature")

        ops.checkout_branch("main")
        self._commit_file(ops, "main.txt", "main\n", "main change")
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

    def test_conflict_aborts_without_updating_tip(self) -> None:
        ops = self._ops()
        ops.create_branch("feature")
        self._commit_file(ops, "base.txt", "feature-side\n", "feature edit")
        ops.checkout_branch("main")
        self._commit_file(ops, "base.txt", "main-side\n", "main edit")
        tip_before = ops.db.get_ref("main")

        with pytest.raises(MergeConflictError) as exc_info:
            ops.merge("feature")
        assert "base.txt" in exc_info.value.paths
        assert ops.db.get_ref("main") == tip_before

    def test_single_parent_commits_still_readable(self) -> None:
        ops = self._ops()
        h = ops.db.get_ref("main")
        assert h
        c = ops.get_commit(h)
        assert c is not None
        assert c["parent_hash"] is None
        assert c.get("second_parent_hash") in (None, "")
