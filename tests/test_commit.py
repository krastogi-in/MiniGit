import os
import tempfile
import shutil

from components.commit import Commit


class TestCommit:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "file.txt"), "w") as f:
            f.write("content")

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_tree(self):
        c = Commit(self.tmpdir, message="test")
        assert c.Tree_pointer is not None
        assert "file.txt" in c.Tree_pointer.files

    def test_hash_is_string(self):
        c = Commit(self.tmpdir, message="test", timestamp="fixed")
        h = c.get_hash()
        assert isinstance(h, str)
        assert len(h) == 64

    def test_defaults(self):
        c = Commit(self.tmpdir)
        assert c.message == "No message"
        assert c.author is not None
        assert c.timestamp is not None

    def test_no_parent(self):
        c = Commit(self.tmpdir, message="initial")
        assert c.parent_commit_pointer is None

    def test_with_parent(self):
        c1 = Commit(self.tmpdir, message="first", timestamp="t1")
        c2 = Commit(self.tmpdir, parent_commit_pointer=c1,
                     message="second", timestamp="t2")
        assert c2.parent_commit_pointer is c1

    def test_different_messages_different_hashes(self):
        c1 = Commit(self.tmpdir, message="msg1", timestamp="t")
        c2 = Commit(self.tmpdir, message="msg2", timestamp="t")
        assert c1.get_hash() != c2.get_hash()

    def test_parent_affects_hash(self):
        c1 = Commit(self.tmpdir, message="m", timestamp="t")
        c_no_parent = Commit(self.tmpdir, message="m2", timestamp="t2")
        c_with_parent = Commit(self.tmpdir, parent_commit_pointer=c1,
                               message="m2", timestamp="t2")
        assert c_no_parent.get_hash() != c_with_parent.get_hash()
