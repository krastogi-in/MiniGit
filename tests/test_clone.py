"""Tests for MiniGit clone and clone-count (BLRID-22)."""

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile

import pytest

from backend.sqlite_client import SQLiteClient
from frontend.operations import Operations


class TestCloneCountMeta:
    """Backend meta APIs for clone_count."""

    def setup_method(self) -> None:
        """Create a temporary database file."""
        self.fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.db = SQLiteClient(self.db_path)

    def teardown_method(self) -> None:
        """Close and remove the temporary database."""
        self.db.close()
        os.close(self.fd)
        os.unlink(self.db_path)

    def test_clone_count_defaults_to_zero(self) -> None:
        """Fresh DB reports clone_count of 0."""
        assert self.db.get_clone_count() == 0

    def test_increment_clone_count(self) -> None:
        """increment_clone_count persists and returns new value."""
        assert self.db.increment_clone_count() == 1
        assert self.db.get_clone_count() == 1
        assert self.db.increment_clone_count() == 2


class TestCloneRepo:
    """Operations.clone_repo behavior."""

    def setup_method(self) -> None:
        """Create a temporary source repo with sample files."""
        self.tmpdir = tempfile.mkdtemp()
        self.source = os.path.join(self.tmpdir, "source")
        os.makedirs(self.source)
        with open(os.path.join(self.source, "README.md"), "w") as f:
            f.write("# Source\n")
        self.db_path = os.path.join(self.source, ".minigit", "minigit.db")
        self.ops = Operations(self.source, self.db_path)
        self.ops.init_repo(author="Tester", message="Initial commit")

    def teardown_method(self) -> None:
        """Clean up the temporary directory."""
        with contextlib.suppress(Exception):
            self.ops.db.close()
        shutil.rmtree(self.tmpdir)

    def test_clone_creates_working_copy(self) -> None:
        """Successful clone creates a usable MiniGit repo at dest."""
        dest = os.path.join(self.tmpdir, "dest")
        count = self.ops.clone_repo(dest)
        assert count == 1
        assert os.path.isdir(os.path.join(dest, ".minigit"))
        dest_ops = Operations(dest, os.path.join(dest, ".minigit", "minigit.db"))
        history = dest_ops.get_commit_history()
        assert len(history) == 1
        assert history[0]["message"] == "Initial commit"
        dest_ops.db.close()

    def test_clone_increments_counter(self) -> None:
        """Each successful clone increments the source counter."""
        dest1 = os.path.join(self.tmpdir, "dest1")
        dest2 = os.path.join(self.tmpdir, "dest2")
        assert self.ops.clone_repo(dest1) == 1
        assert self.ops.get_clone_count() == 1
        assert self.ops.clone_repo(dest2) == 2
        assert self.ops.get_clone_count() == 2

    def test_clone_missing_source_fails(self) -> None:
        """Cloning a path without .minigit raises ValueError."""
        bogus = os.path.join(self.tmpdir, "not-a-repo")
        os.makedirs(bogus)
        bad = Operations(bogus, os.path.join(bogus, ".minigit", "minigit.db"))
        # Operations creates .minigit dir in __init__ — remove to simulate missing
        shutil.rmtree(os.path.join(bogus, ".minigit"), ignore_errors=True)
        with pytest.raises(ValueError, match="Not a MiniGit repository"):
            bad.clone_repo(os.path.join(self.tmpdir, "out"))
        bad.db.close()

    def test_clone_existing_dest_repo_fails_without_increment(self) -> None:
        """Cloning into an existing MiniGit dest fails and does not bump count."""
        dest = os.path.join(self.tmpdir, "dest")
        self.ops.clone_repo(dest)
        assert self.ops.get_clone_count() == 1
        with pytest.raises(ValueError, match="already is a MiniGit"):
            self.ops.clone_repo(dest)
        assert self.ops.get_clone_count() == 1
