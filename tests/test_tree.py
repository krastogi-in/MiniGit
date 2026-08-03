import os
import tempfile
import shutil

from components.tree import Tree
from components.blob import Blob


class TestTree:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "file1.txt"), "w") as f:
            f.write("hello")
        with open(os.path.join(self.tmpdir, "file2.txt"), "w") as f:
            f.write("world")

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_discovers_files(self):
        tree = Tree(self.tmpdir)
        assert "file1.txt" in tree.files
        assert "file2.txt" in tree.files

    def test_files_are_blobs(self):
        tree = Tree(self.tmpdir)
        assert isinstance(tree.files["file1.txt"], Blob)
        assert isinstance(tree.files["file2.txt"], Blob)

    def test_blob_content_matches(self):
        tree = Tree(self.tmpdir)
        assert tree.files["file1.txt"].get_data() == "hello"
        assert tree.files["file2.txt"].get_data() == "world"

    def test_hash_deterministic(self):
        t1 = Tree(self.tmpdir)
        t2 = Tree(self.tmpdir)
        assert t1.get_hash() == t2.get_hash()

    def test_hash_changes_with_content(self):
        t1 = Tree(self.tmpdir)
        old_hash = t1.get_hash()
        with open(os.path.join(self.tmpdir, "file1.txt"), "w") as f:
            f.write("changed!")
        t2 = Tree(self.tmpdir)
        assert t2.get_hash() != old_hash

    def test_subdirectory(self):
        subdir = os.path.join(self.tmpdir, "sub")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "nested.txt"), "w") as f:
            f.write("nested content")
        tree = Tree(self.tmpdir)
        assert "sub" in tree.files
        assert isinstance(tree.files["sub"], Tree)
        assert "nested.txt" in tree.files["sub"].files

    def test_equality(self):
        t1 = Tree(self.tmpdir)
        t2 = Tree(self.tmpdir)
        assert t1 == t2

    def test_adding_file_changes_hash(self):
        t1 = Tree(self.tmpdir)
        with open(os.path.join(self.tmpdir, "new.txt"), "w") as f:
            f.write("new file")
        t2 = Tree(self.tmpdir)
        assert t1 != t2
