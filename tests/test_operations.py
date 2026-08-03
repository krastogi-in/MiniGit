import os
import json
import tempfile
import shutil

from frontend.operations import Operations


class TestOperations:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# Test Project\n")
        subdir = os.path.join(self.tmpdir, "src")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "main.py"), "w") as f:
            f.write("print('hello')\n")
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self):
        shutil.rmtree(self.tmpdir)

    def _init_ops(self):
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")
        return ops

    def test_init_creates_db(self):
        self._init_ops()
        assert os.path.exists(self.db_path)

    def test_init_returns_hash(self):
        ops = Operations(self.tmpdir, self.db_path)
        h = ops.init_repo(author="Tester", message="init")
        assert isinstance(h, str)
        assert len(h) == 64

    def test_init_creates_main_branch(self):
        ops = self._init_ops()
        branches = ops.get_all_branches()
        names = [b["name"] for b in branches]
        assert "main" in names

    def test_commit_history(self):
        ops = self._init_ops()
        history = ops.get_commit_history()
        assert len(history) == 1
        assert history[0]["message"] == "Initial commit"
        assert history[0]["author"] == "Tester"

    def test_browse_root_tree(self):
        ops = self._init_ops()
        history = ops.get_commit_history()
        entries = ops.browse_tree(history[0]["tree_hash"])
        names = {e["name"] for e in entries}
        assert "README.md" in names
        assert "src" in names

    def test_browse_subtree(self):
        ops = self._init_ops()
        history = ops.get_commit_history()
        root_entries = ops.browse_tree(history[0]["tree_hash"])
        src_entry = next(e for e in root_entries if e["name"] == "src")
        src_entries = ops.browse_tree(src_entry["hash"])
        names = {e["name"] for e in src_entries}
        assert "main.py" in names

    def test_get_blob_content(self):
        ops = self._init_ops()
        history = ops.get_commit_history()
        root_entries = ops.browse_tree(history[0]["tree_hash"])
        readme = next(e for e in root_entries if e["name"] == "README.md")
        content = ops.get_blob_content(readme["hash"])
        assert content == "# Test Project\n"

    def test_create_branch(self):
        ops = self._init_ops()
        ops.create_branch("feature")
        branches = ops.get_all_branches()
        names = [b["name"] for b in branches]
        assert "feature" in names

    def test_create_duplicate_branch_fails(self):
        ops = self._init_ops()
        try:
            ops.create_branch("main")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_checkout_branch(self):
        ops = self._init_ops()
        ops.create_branch("dev")
        ops.checkout_branch("dev")
        assert ops.branch == "dev"

    def test_checkout_nonexistent_fails(self):
        ops = self._init_ops()
        try:
            ops.checkout_branch("nonexistent")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_delete_branch(self):
        ops = self._init_ops()
        ops.create_branch("temp")
        ops.checkout_branch("main")
        ops.delete_branch("temp")
        names = [b["name"] for b in ops.get_all_branches()]
        assert "temp" not in names

    def test_delete_main_fails(self):
        ops = self._init_ops()
        try:
            ops.delete_branch("main")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_flatten_tree(self):
        ops = self._init_ops()
        history = ops.get_commit_history()
        flat = ops._flatten_tree(history[0]["tree_hash"])
        assert "README.md" in flat
        assert "src/main.py" in flat

    def test_get_commit(self):
        ops = self._init_ops()
        history = ops.get_commit_history()
        commit = ops.get_commit(history[0]["hash"])
        assert commit["message"] == "Initial commit"

    def test_add_stages_file(self):
        ops = self._init_ops()
        blob_hash = ops.add("README.md")
        assert isinstance(blob_hash, str)
        assert len(blob_hash) == 64
        staged = ops.db.get_staged()
        assert len(staged) == 1
        assert staged[0]["path"] == "README.md"
        assert staged[0]["action"] == "add"

    def test_add_nonexistent_file_fails(self):
        ops = self._init_ops()
        try:
            ops.add("nonexistent.txt")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_delete_stages_removal(self):
        ops = self._init_ops()
        ops.delete_file("README.md")
        staged = ops.db.get_staged()
        assert len(staged) == 1
        assert staged[0]["action"] == "delete"

    def test_delete_untracked_file_fails(self):
        ops = self._init_ops()
        try:
            ops.delete_file("not_tracked.txt")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_create_new_commit(self):
        ops = self._init_ops()
        new_file = os.path.join(self.tmpdir, "new.txt")
        with open(new_file, "w") as f:
            f.write("new content")
        ops.add("new.txt")
        commit_hash = ops.create_new_commit("add new file", author="Tester")
        assert isinstance(commit_hash, str)
        assert len(commit_hash) == 64

    def test_new_commit_appears_in_history(self):
        ops = self._init_ops()
        new_file = os.path.join(self.tmpdir, "new.txt")
        with open(new_file, "w") as f:
            f.write("new content")
        ops.add("new.txt")
        ops.create_new_commit("second commit", author="Tester")
        history = ops.get_commit_history()
        assert len(history) == 2
        assert history[0]["message"] == "second commit"
        assert history[1]["message"] == "Initial commit"

    def test_new_commit_has_parent(self):
        ops = self._init_ops()
        new_file = os.path.join(self.tmpdir, "new.txt")
        with open(new_file, "w") as f:
            f.write("content")
        ops.add("new.txt")
        ops.create_new_commit("second", author="Tester")
        history = ops.get_commit_history()
        assert history[0]["parent_hash"] == history[1]["hash"]

    def test_commit_nothing_staged_fails(self):
        ops = self._init_ops()
        try:
            ops.create_new_commit("empty commit")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_delete_file_removes_from_tree(self):
        ops = self._init_ops()
        ops.delete_file("README.md")
        ops.create_new_commit("remove readme", author="Tester")
        history = ops.get_commit_history()
        flat = ops._flatten_tree(history[0]["tree_hash"])
        assert "README.md" not in flat
        assert "src/main.py" in flat

    def test_staging_cleared_after_commit(self):
        ops = self._init_ops()
        new_file = os.path.join(self.tmpdir, "new.txt")
        with open(new_file, "w") as f:
            f.write("content")
        ops.add("new.txt")
        ops.create_new_commit("commit", author="Tester")
        staged = ops.db.get_staged()
        assert len(staged) == 0
