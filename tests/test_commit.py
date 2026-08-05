"""Tests for the Commit component."""

import os
import shutil
import tempfile

from components.commit import Commit


class TestCommit:
    """Verify Commit creation, hashing, and parent linkage."""

    def setup_method(self) -> None:
        """Create a temporary directory with a test file."""
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "file.txt"), "w") as f:
            f.write("content")

    def teardown_method(self) -> None:
        """Clean up the temporary directory."""
        shutil.rmtree(self.tmpdir)

    def test_creates_tree(self) -> None:
        """Commit constructs a Tree from the given path."""
        c = Commit(self.tmpdir, message="test")
        assert c.Tree_pointer is not None
        assert "file.txt" in c.Tree_pointer.files

    def test_hash_is_string(self) -> None:
        """Commit hash is a 64-character hex string."""
        c = Commit(self.tmpdir, message="test", timestamp="fixed")
        h = c.get_hash()
        assert isinstance(h, str)
        assert len(h) == 64

    def test_defaults(self) -> None:
        """Commit has sensible defaults for message, author, timestamp."""
        c = Commit(self.tmpdir)
        assert c.message == "No message"
        assert c.author is not None
        assert c.timestamp is not None

    def test_no_parent(self) -> None:
        """Root commit has no parent."""
        c = Commit(self.tmpdir, message="initial")
        assert c.parent_commit_pointer is None

    def test_with_parent(self) -> None:
        """Commit can reference a parent commit object."""
        c1 = Commit(self.tmpdir, message="first", timestamp="t1")
        c2 = Commit(self.tmpdir, parent_commit_pointer=c1,
                     message="second", timestamp="t2")
        assert c2.parent_commit_pointer is c1

    def test_different_messages_different_hashes(self) -> None:
        """Different messages produce different commit hashes."""
        c1 = Commit(self.tmpdir, message="msg1", timestamp="t")
        c2 = Commit(self.tmpdir, message="msg2", timestamp="t")
        assert c1.get_hash() != c2.get_hash()

    def test_parent_affects_hash(self) -> None:
        """Having a parent changes the commit hash."""
        c1 = Commit(self.tmpdir, message="m", timestamp="t")
        c_no_parent = Commit(self.tmpdir, message="m2", timestamp="t2")
        c_with_parent = Commit(self.tmpdir, parent_commit_pointer=c1,
                               message="m2", timestamp="t2")
        assert c_no_parent.get_hash() != c_with_parent.get_hash()
