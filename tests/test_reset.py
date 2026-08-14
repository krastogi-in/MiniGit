"""Tests for safe reset with loss preview (BLRID-29)."""

from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from frontend.operations import Operations


class TestSafeReset:
    """Verify soft/mixed/hard reset and dry-run preview."""

    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# v1\n")
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        shutil.rmtree(self.tmpdir)

    def _init(self) -> Operations:
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")
        return ops

    def _second_commit(self, ops: Operations, text: str = "# v2\n") -> str:
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write(text)
        ops.add("README.md")
        return ops.create_new_commit("Second commit", author="Tester")

    def test_dry_run_lists_commits_and_leaves_tip(self) -> None:
        ops = self._init()
        tip0 = ops.get_commit_history()[0]["hash"]
        tip1 = self._second_commit(ops)
        preview = ops.reset(tip0, mode="mixed", dry_run=True)
        assert tip1 in [c["hash"] for c in preview["commits_to_drop"]]
        assert ops.db.get_ref("main") == tip1

    def test_soft_keeps_staging(self) -> None:
        ops = self._init()
        tip0 = ops.get_commit_history()[0]["hash"]
        self._second_commit(ops)
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# staged\n")
        ops.add("README.md")
        assert ops.get_staged()
        ops.reset(tip0, mode="soft", confirm=True)
        assert ops.db.get_ref("main") == tip0
        assert ops.get_staged()

    def test_mixed_clears_staging(self) -> None:
        ops = self._init()
        tip0 = ops.get_commit_history()[0]["hash"]
        self._second_commit(ops)
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# staged\n")
        ops.add("README.md")
        ops.reset(tip0, mode="mixed", confirm=True)
        assert ops.db.get_ref("main") == tip0
        assert ops.get_staged() == []

    def test_hard_syncs_working_tree(self) -> None:
        ops = self._init()
        tip0 = ops.get_commit_history()[0]["hash"]
        self._second_commit(ops, "# v2\n")
        ops.reset(tip0, mode="hard", confirm=True)
        assert ops.db.get_ref("main") == tip0
        with open(os.path.join(self.tmpdir, "README.md")) as f:
            assert f.read() == "# v1\n"

    def test_hard_dirty_aborts_without_force(self) -> None:
        ops = self._init()
        tip0 = ops.get_commit_history()[0]["hash"]
        self._second_commit(ops, "# v2\n")
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# dirty\n")
        with pytest.raises(ValueError, match="uncommitted"):
            ops.reset(tip0, mode="hard", confirm=True, force=False)
        assert ops.db.get_ref("main") != tip0

    def test_invalid_hash_format(self) -> None:
        ops = self._init()
        tip = ops.db.get_ref("main")
        with pytest.raises(ValueError, match="Invalid commit hash"):
            ops.reset("not-a-hash", confirm=True)
        assert ops.db.get_ref("main") == tip

    def test_tip_equals_target_noop(self) -> None:
        ops = self._init()
        tip = ops.db.get_ref("main")
        assert tip is not None
        preview = ops.reset(tip, mode="mixed", confirm=True)
        assert preview["commits_to_drop"] == []
        assert ops.db.get_ref("main") == tip

    def test_hard_removes_empty_dirs(self) -> None:
        ops = self._init()
        tip0 = ops.get_commit_history()[0]["hash"]
        nested = os.path.join(self.tmpdir, "pkg", "mod.py")
        os.makedirs(os.path.dirname(nested))
        with open(nested, "w") as f:
            f.write("x = 1\n")
        ops.add("pkg/mod.py")
        ops.create_new_commit("add nested", author="Tester")
        ops.reset(tip0, mode="hard", confirm=True)
        assert not os.path.exists(nested)
        assert not os.path.isdir(os.path.join(self.tmpdir, "pkg"))

    def test_unknown_hash(self) -> None:
        ops = self._init()
        tip = ops.db.get_ref("main")
        bad = "a" * 64
        with pytest.raises(ValueError, match="not found"):
            ops.reset(bad, confirm=True)
        assert ops.db.get_ref("main") == tip

    def test_non_ancestor(self) -> None:
        ops = self._init()
        tip0 = ops.get_commit_history()[0]["hash"]
        ops.create_branch("other")
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# other\n")
        ops.add("README.md")
        other_tip = ops.create_new_commit("Other line", author="Tester")
        ops.checkout_branch("main")
        self._second_commit(ops, "# main2\n")
        with pytest.raises(ValueError, match="ancestor"):
            ops.reset(other_tip, confirm=True)
        assert ops.db.get_ref("main") != tip0

    def test_apply_requires_confirm(self) -> None:
        ops = self._init()
        tip0 = ops.get_commit_history()[0]["hash"]
        self._second_commit(ops)
        with pytest.raises(ValueError, match=r"--yes|confirm"):
            ops.reset(tip0, dry_run=False, confirm=False)
