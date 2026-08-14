"""Tests for MiniGit stash (push / list / pop)."""

from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from frontend.operations import Operations


class TestStash:
    """Verify stash stack behavior against the BLRID-10 spec."""

    def setup_method(self) -> None:
        """Create a temporary repo with sample files."""
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# Test Project\n")
        subdir = os.path.join(self.tmpdir, "src")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "main.py"), "w") as f:
            f.write("print('hello')\n")
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        """Remove the temporary directory."""
        shutil.rmtree(self.tmpdir)

    def _init_ops(self) -> Operations:
        """Initialize a repo and return Operations."""
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")
        return ops

    def test_push_empty_staging_fails(self) -> None:
        """Push with nothing staged raises ValueError."""
        ops = self._init_ops()
        with pytest.raises(ValueError, match=r"(?i)staged"):
            ops.stash_push()

    def test_push_list_pop_happy_path(self) -> None:
        """Push clears staging; list shows entry; pop restores staging and WD."""
        ops = self._init_ops()
        readme = os.path.join(self.tmpdir, "README.md")
        with open(readme, "w") as f:
            f.write("# Stashed\n")
        ops.add("README.md")
        meta = ops.stash_push(message="save wip")
        assert meta["message"] == "save wip"
        assert ops.get_staged() == []
        with open(readme) as f:
            assert f.read() == "# Test Project\n"

        listed = ops.stash_list()
        assert len(listed) == 1
        assert listed[0]["index"] == 0
        assert listed[0]["message"] == "save wip"

        popped = ops.stash_pop()
        assert popped["message"] == "save wip"
        staged = ops.get_staged()
        assert len(staged) == 1
        assert staged[0]["path"] == "README.md"
        with open(readme) as f:
            assert f.read() == "# Stashed\n"
        assert ops.stash_list() == []

    def test_pop_empty_fails(self) -> None:
        """Pop on empty stack raises ValueError."""
        ops = self._init_ops()
        with pytest.raises(ValueError, match=r"(?i)stash"):
            ops.stash_pop()

    def test_pop_conflict_aborts_and_keeps_stash(self) -> None:
        """Conflict on pop aborts and leaves the stash entry."""
        ops = self._init_ops()
        readme = os.path.join(self.tmpdir, "README.md")
        with open(readme, "w") as f:
            f.write("# Stashed\n")
        ops.add("README.md")
        ops.stash_push(message="wip")

        with open(readme, "w") as f:
            f.write("# Divergent dirty\n")

        with pytest.raises(ValueError, match=r"(?i)conflict"):
            ops.stash_pop()

        assert len(ops.stash_list()) == 1
        assert ops.get_staged() == []
