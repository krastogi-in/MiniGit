"""Tests for the Operations frontend layer."""

import os
import shutil
import tempfile

from frontend.operations import Operations


class TestOperations:
    """Verify high-level git operations: init, branch, stage, commit, diff."""

    def setup_method(self) -> None:
        """Create a temporary repo directory with sample files."""
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# Test Project\n")
        subdir = os.path.join(self.tmpdir, "src")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "main.py"), "w") as f:
            f.write("print('hello')\n")
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        """Clean up the temporary directory."""
        shutil.rmtree(self.tmpdir)

    def _init_ops(self) -> Operations:
        """Helper to initialize a repo and return the Operations instance."""
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")
        return ops

    def test_init_creates_db(self) -> None:
        """init_repo creates the .minigit database file."""
        self._init_ops()
        assert os.path.exists(self.db_path)

    def test_init_returns_hash(self) -> None:
        """init_repo returns a valid 64-char hex commit hash."""
        ops = Operations(self.tmpdir, self.db_path)
        h = ops.init_repo(author="Tester", message="init")
        assert isinstance(h, str)
        assert len(h) == 64

    def test_init_creates_main_branch(self) -> None:
        """init_repo creates a 'main' branch."""
        ops = self._init_ops()
        branches = ops.get_all_branches()
        names = [b["name"] for b in branches]
        assert "main" in names

    def test_commit_history(self) -> None:
        """Initial commit appears in history with correct metadata."""
        ops = self._init_ops()
        history = ops.get_commit_history()
        assert len(history) == 1
        assert history[0]["message"] == "Initial commit"
        assert history[0]["author"] == "Tester"

    def test_browse_root_tree(self) -> None:
        """Root tree contains top-level files and directories."""
        ops = self._init_ops()
        history = ops.get_commit_history()
        entries = ops.browse_tree(history[0]["tree_hash"])
        names = {e["name"] for e in entries}
        assert "README.md" in names
        assert "src" in names

    def test_browse_subtree(self) -> None:
        """Subtree entries are accessible via their tree hash."""
        ops = self._init_ops()
        history = ops.get_commit_history()
        root_entries = ops.browse_tree(history[0]["tree_hash"])
        src_entry = next(e for e in root_entries if e["name"] == "src")
        src_entries = ops.browse_tree(src_entry["hash"])
        names = {e["name"] for e in src_entries}
        assert "main.py" in names

    def test_get_blob_content(self) -> None:
        """Blob content matches the original file."""
        ops = self._init_ops()
        history = ops.get_commit_history()
        root_entries = ops.browse_tree(history[0]["tree_hash"])
        readme = next(e for e in root_entries if e["name"] == "README.md")
        content = ops.get_blob_content(readme["hash"])
        assert content == "# Test Project\n"

    def test_create_branch(self) -> None:
        """create_branch adds a new branch ref."""
        ops = self._init_ops()
        ops.create_branch("feature")
        branches = ops.get_all_branches()
        names = [b["name"] for b in branches]
        assert "feature" in names

    def test_create_duplicate_branch_fails(self) -> None:
        """Creating a branch that already exists raises ValueError."""
        ops = self._init_ops()
        try:
            ops.create_branch("main")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_checkout_branch(self) -> None:
        """checkout_branch switches the active branch."""
        ops = self._init_ops()
        ops.create_branch("dev")
        ops.checkout_branch("dev")
        assert ops.branch == "dev"

    def test_checkout_nonexistent_fails(self) -> None:
        """Checking out a nonexistent branch raises ValueError."""
        ops = self._init_ops()
        try:
            ops.checkout_branch("nonexistent")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_delete_branch(self) -> None:
        """delete_branch removes the branch ref."""
        ops = self._init_ops()
        ops.create_branch("temp")
        ops.checkout_branch("main")
        ops.delete_branch("temp")
        names = [b["name"] for b in ops.get_all_branches()]
        assert "temp" not in names

    def test_delete_main_fails(self) -> None:
        """Deleting 'main' branch raises ValueError."""
        ops = self._init_ops()
        try:
            ops.delete_branch("main")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_flatten_tree(self) -> None:
        """_flatten_tree returns all file paths recursively."""
        ops = self._init_ops()
        history = ops.get_commit_history()
        flat = ops._flatten_tree(history[0]["tree_hash"])
        assert "README.md" in flat
        assert "src/main.py" in flat

    def test_get_commit(self) -> None:
        """get_commit returns the commit with correct message."""
        ops = self._init_ops()
        history = ops.get_commit_history()
        commit = ops.get_commit(history[0]["hash"])
        assert commit["message"] == "Initial commit"

    def test_add_stages_file(self) -> None:
        """add() stages a file and returns its blob hash."""
        ops = self._init_ops()
        blob_hash = ops.add("README.md")
        assert isinstance(blob_hash, str)
        assert len(blob_hash) == 64
        staged = ops.db.get_staged()
        assert len(staged) == 1
        assert staged[0]["path"] == "README.md"
        assert staged[0]["action"] == "add"

    def test_add_nonexistent_file_fails(self) -> None:
        """Adding a nonexistent file raises FileNotFoundError."""
        ops = self._init_ops()
        try:
            ops.add("nonexistent.txt")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_delete_stages_removal(self) -> None:
        """delete_file() stages a deletion entry."""
        ops = self._init_ops()
        ops.delete_file("README.md")
        staged = ops.db.get_staged()
        assert len(staged) == 1
        assert staged[0]["action"] == "delete"

    def test_delete_untracked_file_fails(self) -> None:
        """Deleting an untracked file raises FileNotFoundError."""
        ops = self._init_ops()
        try:
            ops.delete_file("not_tracked.txt")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_create_new_commit(self) -> None:
        """create_new_commit returns a valid commit hash."""
        ops = self._init_ops()
        new_file = os.path.join(self.tmpdir, "new.txt")
        with open(new_file, "w") as f:
            f.write("new content")
        ops.add("new.txt")
        commit_hash = ops.create_new_commit("add new file", author="Tester")
        assert isinstance(commit_hash, str)
        assert len(commit_hash) == 64

    def test_new_commit_appears_in_history(self) -> None:
        """New commit is the first entry in history."""
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

    def test_new_commit_has_parent(self) -> None:
        """New commit's parent_hash points to the previous commit."""
        ops = self._init_ops()
        new_file = os.path.join(self.tmpdir, "new.txt")
        with open(new_file, "w") as f:
            f.write("content")
        ops.add("new.txt")
        ops.create_new_commit("second", author="Tester")
        history = ops.get_commit_history()
        assert history[0]["parent_hash"] == history[1]["hash"]

    def test_commit_nothing_staged_fails(self) -> None:
        """Committing with nothing staged raises ValueError."""
        ops = self._init_ops()
        try:
            ops.create_new_commit("empty commit")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_delete_file_removes_from_tree(self) -> None:
        """Deleted file is absent from the new commit's tree."""
        ops = self._init_ops()
        ops.delete_file("README.md")
        ops.create_new_commit("remove readme", author="Tester")
        history = ops.get_commit_history()
        flat = ops._flatten_tree(history[0]["tree_hash"])
        assert "README.md" not in flat
        assert "src/main.py" in flat

    def test_staging_cleared_after_commit(self) -> None:
        """Staging area is empty after a successful commit."""
        ops = self._init_ops()
        new_file = os.path.join(self.tmpdir, "new.txt")
        with open(new_file, "w") as f:
            f.write("content")
        ops.add("new.txt")
        ops.create_new_commit("commit", author="Tester")
        staged = ops.db.get_staged()
        assert len(staged) == 0

    def test_get_commit_graph_data_single_commit(self) -> None:
        """Graph data includes the initial commit on lane 0."""
        ops = self._init_ops()
        graph = ops.get_commit_graph_data()
        assert len(graph["nodes"]) == 1
        assert graph["nodes"][0]["lane"] == 0
        assert graph["truncated"] is False
        assert "main" in graph["nodes"][0]["branch_names"]

    def test_get_commit_graph_data_branch_lanes(self) -> None:
        """Diverged branches assign separate lanes in graph data."""
        ops = self._init_ops()
        ops.create_branch("feature")
        ops.checkout_branch("feature")
        new_file = os.path.join(self.tmpdir, "feature.txt")
        with open(new_file, "w") as f:
            f.write("feature\n")
        ops.add("feature.txt")
        ops.create_new_commit("on feature", author="Tester")
        graph = ops.get_commit_graph_data()
        lanes = {n["hash"]: n["lane"] for n in graph["nodes"]}
        tips = {t["name"]: t["hash"] for t in graph["branch_tips"]}
        assert lanes[tips["feature"]] != lanes[tips["main"]]

    def test_get_commit_graph_data_truncation(self) -> None:
        """Graph truncates when more than max_commits exist."""
        ops = self._init_ops()
        for i in range(3):
            path = os.path.join(self.tmpdir, f"file{i}.txt")
            with open(path, "w") as f:
                f.write(f"content {i}\n")
            ops.add(f"file{i}.txt")
            ops.create_new_commit(f"commit {i}", author="Tester")
        graph = ops.get_commit_graph_data(max_commits=2)
        assert graph["truncated"] is True
        assert len(graph["nodes"]) == 2
        assert graph["total_commits"] == 4
