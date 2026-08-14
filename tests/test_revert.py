"""Tests for revert_commit — undo a historical commit on the current branch."""

import os
import shutil
import tempfile

import pytest

from frontend.operations import Operations


class TestRevertCommit:
    """Verify revert creates an inverse commit and handles error cases."""

    def setup_method(self) -> None:
        """Create a temporary repo with an initial commit."""
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# Test Project\n")
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")
        self.ops = Operations(self.tmpdir, self.db_path)
        self.ops.init_repo(author="Tester", message="Initial commit")

    def teardown_method(self) -> None:
        """Remove the temporary directory."""
        shutil.rmtree(self.tmpdir)

    def _commit_file(self, name: str, content: str, message: str) -> str:
        """Stage a new file and commit it. Returns the new commit hash."""
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        self.ops.add(name)
        return self.ops.create_new_commit(message, author="Tester")

    def test_revert_restores_tree_before_change(self) -> None:
        """Reverting a file-add commit removes the added file from HEAD."""
        add_hash = self._commit_file("extra.txt", "extra\n", "add extra file")
        revert_hash = self.ops.revert_commit(add_hash)

        history = self.ops.get_commit_history()
        assert history[0]["hash"] == revert_hash
        assert history[0]["message"] == 'Revert "add extra file"'
        flat = self.ops._flatten_tree(history[0]["tree_hash"])
        assert "extra.txt" not in flat
        assert "README.md" in flat

    def test_revert_appears_in_log(self) -> None:
        """After revert, history has three commits with revert on top."""
        add_hash = self._commit_file("note.txt", "note\n", "second commit")
        self.ops.revert_commit(add_hash)
        history = self.ops.get_commit_history()
        assert len(history) == 3
        assert history[0]["message"].startswith('Revert "second commit"')
        assert history[1]["hash"] == add_hash
        assert history[2]["message"] == "Initial commit"

    def test_revert_root_commit_fails(self) -> None:
        """Cannot revert the initial (root) commit."""
        history = self.ops.get_commit_history()
        root_hash = history[0]["hash"]
        with pytest.raises(ValueError, match="Cannot revert root commit"):
            self.ops.revert_commit(root_hash)

    def test_revert_unknown_hash_fails(self) -> None:
        """Unknown commit hash raises ValueError."""
        fake_hash = "a" * 64
        with pytest.raises(ValueError, match="Commit not found"):
            self.ops.revert_commit(fake_hash)

    def test_revert_invalid_hash_format_fails(self) -> None:
        """Invalid hash format raises ValueError from validation."""
        with pytest.raises(ValueError, match="Invalid commit hash"):
            self.ops.revert_commit("not-a-hash")

    def test_revert_modified_file_restores_parent_content(self) -> None:
        """Reverting a modify commit restores the file to its parent content."""
        readme_path = os.path.join(self.tmpdir, "README.md")
        with open(readme_path, "w") as f:
            f.write("# Updated\n")
        self.ops.add("README.md")
        modify_hash = self.ops.create_new_commit("update readme", author="Tester")

        self.ops.revert_commit(modify_hash)
        history = self.ops.get_commit_history()
        flat = self.ops._flatten_tree(history[0]["tree_hash"])
        content = self.ops.get_blob_content(flat["README.md"])
        assert content == "# Test Project\n"
