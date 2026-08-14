"""Tests for git status: staged, unstaged, untracked (BLRID-18)."""

from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from frontend.operations import Operations


class TestStatus:
    """Verify Operations.get_status against BLRID-18 acceptance criteria."""

    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# Test\n")
        subdir = os.path.join(self.tmpdir, "src")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "main.py"), "w") as f:
            f.write("print('hello')\n")
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        shutil.rmtree(self.tmpdir)

    def _ops(self) -> Operations:
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="initial")
        return ops

    def test_clean_working_tree(self) -> None:
        ops = self._ops()
        status = ops.get_status()
        assert status.branch == "main"
        assert status.head_commit is not None
        assert status.clean is True
        assert status.staged == []
        assert status.unstaged == []
        assert status.untracked == []

    def test_branch_from_head_ref(self) -> None:
        ops = self._ops()
        ops.create_branch("feature")
        ops.db.set_ref("HEAD", "feature")
        ops2 = Operations(self.tmpdir, self.db_path)
        status = ops2.get_status()
        assert status.branch == "feature"

    def test_staged_new_file(self) -> None:
        ops = self._ops()
        new_path = os.path.join(self.tmpdir, "new.txt")
        with open(new_path, "w") as f:
            f.write("new\n")
        ops.add("new.txt")
        status = ops.get_status()
        assert len(status.staged) == 1
        assert status.staged[0].path == "new.txt"
        assert status.staged[0].status == "new"

    def test_staged_modified_file(self) -> None:
        ops = self._ops()
        readme = os.path.join(self.tmpdir, "README.md")
        with open(readme, "w") as f:
            f.write("changed\n")
        ops.add("README.md")
        status = ops.get_status()
        assert any(
            c.path == "README.md" and c.status == "modified" for c in status.staged
        )

    def test_staged_deleted_file(self) -> None:
        ops = self._ops()
        ops.delete_file("README.md")
        status = ops.get_status()
        assert len(status.staged) == 1
        assert status.staged[0].path == "README.md"
        assert status.staged[0].status == "deleted"

    def test_unstaged_modified_file(self) -> None:
        ops = self._ops()
        readme = os.path.join(self.tmpdir, "README.md")
        with open(readme, "w") as f:
            f.write("dirty\n")
        status = ops.get_status()
        assert len(status.unstaged) == 1
        assert status.unstaged[0].path == "README.md"
        assert status.unstaged[0].status == "modified"

    def test_unstaged_deleted_file(self) -> None:
        ops = self._ops()
        os.remove(os.path.join(self.tmpdir, "README.md"))
        status = ops.get_status()
        assert any(
            c.path == "README.md" and c.status == "deleted" for c in status.unstaged
        )

    def test_untracked_file(self) -> None:
        ops = self._ops()
        with open(os.path.join(self.tmpdir, "scratch.txt"), "w") as f:
            f.write("scratch\n")
        status = ops.get_status()
        assert "scratch.txt" in status.untracked

    def test_staged_then_edited_again(self) -> None:
        ops = self._ops()
        readme = os.path.join(self.tmpdir, "README.md")
        with open(readme, "w") as f:
            f.write("staged version\n")
        ops.add("README.md")
        with open(readme, "w") as f:
            f.write("edited again\n")
        status = ops.get_status()
        staged_paths = {c.path for c in status.staged}
        unstaged_paths = {c.path for c in status.unstaged}
        assert "README.md" in staged_paths
        assert "README.md" in unstaged_paths

    def test_nested_working_tree_walk(self) -> None:
        ops = self._ops()
        with open(os.path.join(self.tmpdir, "src", "nested.py"), "w") as f:
            f.write("x\n")
        status = ops.get_status()
        assert "src/nested.py" in status.untracked

    def test_ignores_minigit_directory(self) -> None:
        ops = self._ops()
        with open(os.path.join(self.tmpdir, ".minigit", "secret.txt"), "w") as f:
            f.write("no\n")
        status = ops.get_status()
        assert not any(".minigit" in p for p in status.untracked)

    def test_no_commits_branch_raises(self) -> None:
        empty = tempfile.mkdtemp()
        try:
            db = os.path.join(empty, ".minigit", "minigit.db")
            os.makedirs(os.path.dirname(db))
            ops = Operations(empty, db)
            with pytest.raises(ValueError, match="has no commits"):
                ops.get_status()
        finally:
            shutil.rmtree(empty)
