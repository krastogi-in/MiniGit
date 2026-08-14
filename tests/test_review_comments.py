"""Tests for review comments (SQLite, operations, CLI)."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
from unittest.mock import patch

import pytest

from backend.sqlite_client import SQLiteClient
from frontend.operations import Operations


class TestReviewCommentsSQLite:
    """Verify review_comments table CRUD."""

    def setup_method(self) -> None:
        self.fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.db = SQLiteClient(self.db_path)

    def teardown_method(self) -> None:
        self.db.close()
        os.close(self.fd)
        os.unlink(self.db_path)

    def test_insert_and_get_comment(self) -> None:
        base = "a" * 64
        head = "b" * 64
        cid = self.db.insert_review_comment(
            base, head, "src/main.py", 10, "reviewer", "Please rename"
        )
        comment = self.db.get_review_comment(cid)
        assert comment is not None
        assert comment["status"] == "open"
        assert comment["file_path"] == "src/main.py"
        assert comment["line_number"] == 10

    def test_list_filters_status(self) -> None:
        base = "a" * 64
        head = "b" * 64
        cid = self.db.insert_review_comment(base, head, "f.txt", 1, "r", "one")
        self.db.address_review_comment(cid)
        self.db.insert_review_comment(base, head, "f.txt", 2, "r", "two")
        open_only = self.db.list_review_comments(base, head, "open")
        assert len(open_only) == 1
        assert open_only[0]["body"] == "two"
        all_comments = self.db.list_review_comments(base, head, "all")
        assert len(all_comments) == 2

    def test_address_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="not found"):
            self.db.address_review_comment(9999)

    def test_address_twice_raises(self) -> None:
        base = "a" * 64
        head = "b" * 64
        cid = self.db.insert_review_comment(base, head, "f.txt", 1, "r", "note")
        self.db.address_review_comment(cid)
        with pytest.raises(ValueError, match="already addressed"):
            self.db.address_review_comment(cid)

    def test_invalid_line_number(self) -> None:
        base = "a" * 64
        head = "b" * 64
        with pytest.raises(ValueError, match="line_number"):
            self.db.insert_review_comment(base, head, "f.txt", 0, "r", "bad")

    def test_empty_body_rejected(self) -> None:
        base = "a" * 64
        head = "b" * 64
        with pytest.raises(ValueError, match="empty"):
            self.db.insert_review_comment(base, head, "f.txt", 1, "r", "   ")


class TestReviewCommentsOperations:
    """Verify operations layer for review comments."""

    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")
        self.ops = Operations(self.tmpdir, self.db_path)
        self.ops.init_repo(author="Tester", message="init")

    def teardown_method(self) -> None:
        shutil.rmtree(self.tmpdir)

    def _second_commit(self) -> tuple[str, str]:
        parent = self.ops.get_commit_history()[0]["hash"]
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# Updated\n")
        self.ops.add("README.md")
        head = self.ops.create_new_commit("second")
        return parent, head

    def test_add_list_address_round_trip(self) -> None:
        parent, head = self._second_commit()
        comment = self.ops.add_review_comment(
            parent, head, "README.md", 1, "fix typo", author="alice"
        )
        assert comment["id"] >= 1
        listed = self.ops.list_review_comments(parent, head, "open")
        assert len(listed) == 1
        addressed = self.ops.address_review_comment(comment["id"])
        assert addressed["status"] == "addressed"
        assert self.ops.list_review_comments(parent, head, "open") == []

    def test_invalid_status_filter(self) -> None:
        parent, head = self._second_commit()
        with pytest.raises(ValueError, match="Invalid status"):
            self.ops.list_review_comments(parent, head, "bogus")


class TestReviewCommentsCLI:
    """CLI tests for comment subcommands."""

    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="init")
        parent = ops.get_commit_history()[0]["hash"]
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# Updated\n")
        ops.add("README.md")
        self.head = ops.create_new_commit("second")
        self.parent = parent

    def teardown_method(self) -> None:
        shutil.rmtree(self.tmpdir)

    def _args(self, command: str, **kwargs: object) -> argparse.Namespace:
        base = {"command": "comment", "comment_command": command}
        base.update(kwargs)
        return argparse.Namespace(**base)

    def test_comment_add_and_list_handlers(self, capsys: pytest.CaptureFixture[str]) -> None:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from cli import cmd_comment_add, cmd_comment_list

        with patch("cli.find_repo", return_value=self.tmpdir):
            cmd_comment_add(self._args(
                "add",
                base_hash=self.parent,
                head_hash=self.head,
                path="README.md",
                line=1,
                message="Looks good",
                author="alice",
            ))
            out = capsys.readouterr().out
            assert "Comment" in out
            cmd_comment_list(self._args(
                "list",
                base_hash=self.parent,
                head_hash=self.head,
                status="all",
            ))
            assert "Looks good" in capsys.readouterr().out

    def test_comment_address_handler(self, capsys: pytest.CaptureFixture[str]) -> None:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from cli import cmd_comment_add, cmd_comment_address, cmd_comment_list

        with patch("cli.find_repo", return_value=self.tmpdir):
            cmd_comment_add(self._args(
                "add",
                base_hash=self.parent,
                head_hash=self.head,
                path="README.md",
                line=1,
                message="fix",
                author=None,
            ))
            match = re.search(r"Comment (\d+)", capsys.readouterr().out)
            assert match is not None
            cmd_comment_address(self._args("address", comment_id=int(match.group(1))))
            assert "addressed" in capsys.readouterr().out
            cmd_comment_list(self._args(
                "list",
                base_hash=self.parent,
                head_hash=self.head,
                status="open",
            ))
            assert "No comments" in capsys.readouterr().out
