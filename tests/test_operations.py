"""Tests for the Operations frontend layer."""

import os
import shutil
import tempfile

import pytest

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

    def _write_file(self, relative_path: str, content: str) -> None:
        """Write *content* into a repo-relative file."""
        full_path = os.path.join(self.tmpdir, relative_path)
        parent = os.path.dirname(full_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    def _commit_file(self, ops: Operations, relative_path: str, content: str, message: str) -> str:
        """Update a file and commit it on the current branch."""
        self._write_file(relative_path, content)
        ops.add(relative_path)
        return ops.create_new_commit(message, author="Tester")

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
        with pytest.raises(ValueError):
            ops.create_branch("main")

    def test_checkout_branch(self) -> None:
        """checkout_branch switches the active branch."""
        ops = self._init_ops()
        ops.create_branch("dev")
        ops.checkout_branch("dev")
        assert ops.branch == "dev"
        reopened = Operations(self.tmpdir, self.db_path)
        assert reopened.branch == "dev"

    def test_checkout_nonexistent_fails(self) -> None:
        """Checking out a nonexistent branch raises ValueError."""
        ops = self._init_ops()
        with pytest.raises(ValueError):
            ops.checkout_branch("nonexistent")

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
        with pytest.raises(ValueError):
            ops.delete_branch("main")

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
        with pytest.raises(FileNotFoundError):
            ops.add("nonexistent.txt")

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
        with pytest.raises(FileNotFoundError):
            ops.delete_file("not_tracked.txt")

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
        with pytest.raises(ValueError):
            ops.create_new_commit("empty commit")

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

    def test_rebase_replays_feature_commits_onto_target_branch(self) -> None:
        """rebase_branch replays unique commits onto the target branch tip."""
        ops = self._init_ops()
        ops.create_branch("feature")
        self._commit_file(ops, "README.md", "# Main branch\n", "main change")
        main_head = ops.get_commit_history()[0]["hash"]

        ops.checkout_branch("feature")
        feature_ops = Operations(self.tmpdir, self.db_path)
        feature_head_before = feature_ops.get_commit_history()[0]["hash"]
        self._commit_file(
            feature_ops,
            "src/main.py",
            "print('feature branch')\n",
            "feature change",
        )

        result = feature_ops.rebase_branch("main")

        assert result["status"] == "rebased"
        assert result["replayed"] == 1
        assert result["skipped"] == 0
        history = feature_ops.get_commit_history()
        assert history[0]["message"] == "feature change"
        assert history[0]["parent_hash"] == main_head
        assert history[1]["message"] == "main change"
        assert history[0]["hash"] != feature_head_before

        flat = feature_ops._flatten_tree(history[0]["tree_hash"])
        readme_hash = flat["README.md"]
        main_hash = flat["src/main.py"]
        assert feature_ops.get_blob_content(readme_hash) == "# Main branch\n"
        assert feature_ops.get_blob_content(main_hash) == "print('feature branch')\n"

    def test_rebase_fast_forwards_branch_without_unique_commits(self) -> None:
        """rebase_branch fast-forwards when the current branch has no unique commits."""
        ops = self._init_ops()
        ops.create_branch("feature")
        self._commit_file(ops, "README.md", "# Main branch\n", "main change")
        main_head = ops.get_commit_history()[0]["hash"]

        ops.checkout_branch("feature")
        feature_ops = Operations(self.tmpdir, self.db_path)
        result = feature_ops.rebase_branch("main")

        assert result["status"] == "fast_forward"
        assert result["head"] == main_head
        assert feature_ops.get_commit_history()[0]["hash"] == main_head

    def test_rebase_aborts_on_conflicting_changes(self) -> None:
        """rebase_branch refuses to replay a commit that conflicts with the target."""
        ops = self._init_ops()
        ops.create_branch("feature")
        self._commit_file(ops, "README.md", "# Main branch\n", "main change")

        ops.checkout_branch("feature")
        feature_ops = Operations(self.tmpdir, self.db_path)
        feature_head_before = feature_ops.get_commit_history()[0]["hash"]
        self._commit_file(feature_ops, "README.md", "# Feature branch\n", "feature change")
        feature_head = feature_ops.get_commit_history()[0]["hash"]

        with pytest.raises(ValueError, match="Cannot safely replay changes"):
            feature_ops.rebase_branch("main")

        assert feature_ops.get_commit_history()[0]["hash"] == feature_head
        assert feature_head != feature_head_before
