"""Tests for the Tree component."""

import os
import shutil
import tempfile

from components.blob import Blob
from components.tree import Tree


class TestTree:
    """Verify Tree directory traversal, hashing, and equality."""

    def setup_method(self) -> None:
        """Create a temporary directory with test files."""
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "file1.txt"), "w") as f:
            f.write("hello")
        with open(os.path.join(self.tmpdir, "file2.txt"), "w") as f:
            f.write("world")

    def teardown_method(self) -> None:
        """Clean up the temporary directory."""
        shutil.rmtree(self.tmpdir)

    def test_discovers_files(self) -> None:
        """Tree discovers files in the directory."""
        tree = Tree(self.tmpdir)
        assert "file1.txt" in tree.files
        assert "file2.txt" in tree.files

    def test_files_are_blobs(self) -> None:
        """Discovered files are stored as Blob instances."""
        tree = Tree(self.tmpdir)
        assert isinstance(tree.files["file1.txt"], Blob)
        assert isinstance(tree.files["file2.txt"], Blob)

    def test_blob_content_matches(self) -> None:
        """Blob content matches the file content on disk."""
        tree = Tree(self.tmpdir)
        assert tree.files["file1.txt"].get_data() == "hello"
        assert tree.files["file2.txt"].get_data() == "world"

    def test_hash_deterministic(self) -> None:
        """Same directory produces the same tree hash."""
        t1 = Tree(self.tmpdir)
        t2 = Tree(self.tmpdir)
        assert t1.get_hash() == t2.get_hash()

    def test_hash_changes_with_content(self) -> None:
        """Modifying a file changes the tree hash."""
        t1 = Tree(self.tmpdir)
        old_hash = t1.get_hash()
        with open(os.path.join(self.tmpdir, "file1.txt"), "w") as f:
            f.write("changed!")
        t2 = Tree(self.tmpdir)
        assert t2.get_hash() != old_hash

    def test_subdirectory(self) -> None:
        """Subdirectories are stored as nested Tree instances."""
        subdir = os.path.join(self.tmpdir, "sub")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "nested.txt"), "w") as f:
            f.write("nested content")
        tree = Tree(self.tmpdir)
        assert "sub" in tree.files
        assert isinstance(tree.files["sub"], Tree)
        assert "nested.txt" in tree.files["sub"].files

    def test_equality(self) -> None:
        """Trees with same content are equal."""
        t1 = Tree(self.tmpdir)
        t2 = Tree(self.tmpdir)
        assert t1 == t2

    def test_adding_file_changes_hash(self) -> None:
        """Adding a new file to the directory changes the tree hash."""
        t1 = Tree(self.tmpdir)
        with open(os.path.join(self.tmpdir, "new.txt"), "w") as f:
            f.write("new file")
        t2 = Tree(self.tmpdir)
        assert t1 != t2
