"""Tests for the AI-powered commit message assistant."""

import json
import os
import shutil
import tempfile

import pytest

from frontend.commit_assistant import CommitMessageGenerator, GenerationResult
from frontend.operations import Operations


class TestCommitMessageGenerator:
    """Verify heuristic commit message generation from staged diffs."""

    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        shutil.rmtree(self.tmpdir)

    def _init_ops(self) -> Operations:
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")
        return ops

    def _write_file(self, name: str, content: str) -> str:
        full = os.path.join(self.tmpdir, name)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)
        return full

    def test_single_file_added(self) -> None:
        """Adding one file produces 'feat: add <filename>'."""
        ops = self._init_ops()
        self._write_file("config.py", "DEBUG = True\n")
        ops.add("config.py")

        gen = CommitMessageGenerator(ops)
        result = gen.generate()

        assert result.commit_type == "feat"
        assert result.summary == "add config.py"
        assert result.message == "feat: add config.py"
        assert result.file_count == 1
        assert result.change_types == {"added": 1}

    def test_test_file_added(self) -> None:
        """Adding a test file produces 'test: add test_<name>'."""
        ops = self._init_ops()
        os.makedirs(os.path.join(self.tmpdir, "tests"), exist_ok=True)
        self._write_file("tests/test_foo.py", "def test_it(): pass\n")
        ops.add("tests/test_foo.py")

        gen = CommitMessageGenerator(ops)
        result = gen.generate()

        assert result.commit_type == "test"
        assert "test_foo.py" in result.summary

    def test_docs_file_modified(self) -> None:
        """Modifying a .md file produces 'docs: update <filename>'."""
        self._write_file("README.md", "# Original\n")
        ops = self._init_ops()
        self._write_file("README.md", "# Updated\n")
        ops.add("README.md")

        gen = CommitMessageGenerator(ops)
        result = gen.generate()

        assert result.commit_type == "docs"
        assert result.summary == "update README.md"
        assert result.change_types.get("modified") == 1

    def test_config_file_added(self) -> None:
        """Adding a config file produces 'chore: add <filename>'."""
        ops = self._init_ops()
        self._write_file("pyproject.toml", "[tool.ruff]\n")
        ops.add("pyproject.toml")

        gen = CommitMessageGenerator(ops)
        result = gen.generate()

        assert result.commit_type == "chore"
        assert "pyproject.toml" in result.summary

    def test_multiple_files_same_dir(self) -> None:
        """Multiple files in the same directory produces count summary."""
        ops = self._init_ops()
        os.makedirs(os.path.join(self.tmpdir, "lib"), exist_ok=True)
        self._write_file("lib/a.py", "a = 1\n")
        self._write_file("lib/b.py", "b = 2\n")
        ops.add("lib/a.py")
        ops.add("lib/b.py")

        gen = CommitMessageGenerator(ops)
        result = gen.generate()

        assert result.file_count == 2
        assert "2 files" in result.summary
        assert "lib" in result.summary

    def test_multiple_files_different_dirs(self) -> None:
        """Multiple files across directories uses 'and N other(s)' form."""
        ops = self._init_ops()
        self._write_file("app.py", "from flask import Flask\n")
        os.makedirs(os.path.join(self.tmpdir, "utils"), exist_ok=True)
        self._write_file("utils/helper.py", "def h(): pass\n")
        ops.add("app.py")
        ops.add("utils/helper.py")

        gen = CommitMessageGenerator(ops)
        result = gen.generate()

        assert result.file_count == 2
        assert "and 1 other" in result.summary

    def test_no_staged_changes_raises(self) -> None:
        """No staged changes raises ValueError."""
        ops = self._init_ops()
        gen = CommitMessageGenerator(ops)

        with pytest.raises(ValueError, match="Nothing staged"):
            gen.generate()

    def test_message_length_limit(self) -> None:
        """Generated messages are at most 72 characters."""
        ops = self._init_ops()
        for i in range(20):
            self._write_file(f"dir_{i}/very_long_filename_{i}.py", f"x = {i}\n")
            ops.add(f"dir_{i}/very_long_filename_{i}.py")

        gen = CommitMessageGenerator(ops)
        result = gen.generate()

        assert len(result.message) <= 72

    def test_file_deletion(self) -> None:
        """Deleting a tracked file shows 'remove' action."""
        ops = self._init_ops()
        self._write_file("temp.py", "tmp = 1\n")
        ops.add("temp.py")
        ops.create_new_commit("add temp", author="Tester")

        ops.delete_file("temp.py")
        gen = CommitMessageGenerator(ops)
        result = gen.generate()

        assert result.change_types.get("deleted") == 1
        assert "remove" in result.summary

    def test_generation_result_dataclass(self) -> None:
        """GenerationResult has expected fields."""
        r = GenerationResult(
            message="feat: add foo",
            commit_type="feat",
            summary="add foo",
            file_count=1,
            change_types={"added": 1},
        )
        assert r.message == "feat: add foo"
        assert r.commit_type == "feat"
        assert r.file_count == 1

    def test_mixed_add_modify_delete(self) -> None:
        """Mixed operations classify by majority."""
        ops = self._init_ops()
        self._write_file("new_feature.py", "def feat(): pass\n")
        ops.add("new_feature.py")
        ops.create_new_commit("setup", author="Tester")

        readme = os.path.join(self.tmpdir, "README.md")
        with open(readme, "w") as f:
            f.write("# Changed\n")
        ops.add("README.md")

        self._write_file("another.py", "y = 2\n")
        ops.add("another.py")

        gen = CommitMessageGenerator(ops)
        result = gen.generate()

        assert result.file_count == 2
        assert result.message.startswith(("feat:", "docs:"))


class TestGetStagedDiffs:
    """Verify Operations.get_staged_diffs() returns correct structure."""

    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        shutil.rmtree(self.tmpdir)

    def _init_ops(self) -> Operations:
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")
        return ops

    def _write_file(self, name: str, content: str) -> None:
        full = os.path.join(self.tmpdir, name)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)

    def test_staged_add_returns_diff(self) -> None:
        ops = self._init_ops()
        self._write_file("hello.py", "print('hi')\n")
        ops.add("hello.py")

        diffs = ops.get_staged_diffs()

        assert len(diffs) == 1
        assert diffs[0]["path"] == "hello.py"
        assert diffs[0]["action"] == "added"
        assert diffs[0]["new_content"] == "print('hi')\n"
        assert diffs[0]["old_content"] == ""

    def test_staged_modify_returns_both_contents(self) -> None:
        self._write_file("README.md", "# Original\n")
        ops = self._init_ops()
        self._write_file("README.md", "# Updated README\n")
        ops.add("README.md")

        diffs = ops.get_staged_diffs()

        assert len(diffs) == 1
        assert diffs[0]["action"] == "modified"
        assert diffs[0]["old_content"] == "# Original\n"
        assert diffs[0]["new_content"] == "# Updated README\n"

    def test_staged_delete_returns_old_content(self) -> None:
        ops = self._init_ops()
        self._write_file("temp.txt", "data\n")
        ops.add("temp.txt")
        ops.create_new_commit("add temp", author="Tester")

        ops.delete_file("temp.txt")
        diffs = ops.get_staged_diffs()

        assert len(diffs) == 1
        assert diffs[0]["action"] == "deleted"
        assert diffs[0]["old_content"] == "data\n"
        assert diffs[0]["new_content"] == ""

    def test_nothing_staged_raises(self) -> None:
        ops = self._init_ops()

        with pytest.raises(ValueError, match="Nothing staged"):
            ops.get_staged_diffs()


class TestWebEndpoint:
    """Verify the Flask suggest-message endpoint."""

    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        shutil.rmtree(self.tmpdir)

    def test_suggest_message_returns_json(self) -> None:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from app import app

        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")

        self._write_file("newfile.py", "x = 1\n")
        ops.add("newfile.py")

        from unittest.mock import patch
        with patch("app.get_ops", return_value=ops):
            with app.test_client() as client:
                resp = client.get("/repo/test-repo/suggest-message")
                assert resp.status_code == 200
                data = json.loads(resp.data)
                assert "message" in data
                assert "commit_type" in data
                assert "file_count" in data

    def test_suggest_message_no_staged(self) -> None:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from app import app

        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")

        from unittest.mock import patch
        with patch("app.get_ops", return_value=ops):
            with app.test_client() as client:
                resp = client.get("/repo/test-repo/suggest-message")
                assert resp.status_code == 400
                data = json.loads(resp.data)
                assert "error" in data

    def _write_file(self, name: str, content: str) -> None:
        full = os.path.join(self.tmpdir, name)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)
