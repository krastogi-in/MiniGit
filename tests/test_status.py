"""Tests for MiniGit status (BLRID-11): current branch + staged files."""

from __future__ import annotations

import os
import shutil
import tempfile

from frontend.operations import Operations


class TestStatus:
    """Verify status API, HEAD persistence, and empty/staged reporting."""

    def setup_method(self) -> None:
        """Create a temporary repo directory with a sample file."""
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# Status Test\n")
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        """Clean up the temporary directory."""
        shutil.rmtree(self.tmpdir)

    def _init_ops(self) -> Operations:
        """Initialize a repo and return Operations."""
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")
        return ops

    def test_status_shows_main_after_init(self) -> None:
        """status reports main after init with nothing staged."""
        ops = self._init_ops()
        info = ops.status()
        assert info["branch"] == "main"
        assert info["staged"] == []

    def test_status_lists_staged_files(self) -> None:
        """status lists staged paths after add."""
        ops = self._init_ops()
        with open(os.path.join(self.tmpdir, "note.txt"), "w") as f:
            f.write("hello\n")
        blob_hash = ops.add("note.txt")
        info = ops.status()
        assert info["branch"] == "main"
        assert len(info["staged"]) == 1
        assert info["staged"][0]["path"] == "note.txt"
        assert info["staged"][0]["blob_hash"] == blob_hash

    def test_head_survives_new_operations_instance(self) -> None:
        """checkout updates HEAD so a new Operations sees the branch."""
        ops = self._init_ops()
        ops.create_branch("feature")
        # create_branch switches and should persist HEAD
        assert ops.branch == "feature"
        ops2 = Operations(self.tmpdir, self.db_path)
        assert ops2.branch == "feature"
        assert ops2.status()["branch"] == "feature"

    def test_checkout_persists_head(self) -> None:
        """Explicit checkout updates HEAD for subsequent Processes."""
        ops = self._init_ops()
        ops.create_branch("dev")
        ops.checkout_branch("main")
        ops.checkout_branch("dev")
        ops2 = Operations(self.tmpdir, self.db_path)
        assert ops2.status()["branch"] == "dev"

    def test_cli_status_empty_staged(self) -> None:
        """CLI status prints branch and nothing staged."""
        import io
        from argparse import Namespace
        from contextlib import redirect_stdout

        from cli import cmd_status, find_repo

        self._init_ops()
        cwd = os.getcwd()
        try:
            os.chdir(self.tmpdir)
            assert os.path.realpath(find_repo() or "") == os.path.realpath(
                self.tmpdir
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                cmd_status(Namespace(command="status"))
            out = buf.getvalue()
            assert "On branch main" in out
            assert "nothing staged" in out
        finally:
            os.chdir(cwd)

    def test_flask_status_route(self) -> None:
        """Flask /status page shows current branch."""
        import json

        from app import REGISTRY_FILE, REPOS_DIR, app

        self._init_ops()
        os.makedirs(REPOS_DIR, exist_ok=True)
        registry = {}
        if os.path.isfile(REGISTRY_FILE):
            with open(REGISTRY_FILE) as f:
                registry = json.load(f)
        name = "blrid11-status-test"
        registry[name] = self.tmpdir
        with open(REGISTRY_FILE, "w") as f:
            json.dump(registry, f)

        client = app.test_client()
        resp = client.get(f"/repo/{name}/status")
        assert resp.status_code == 200
        assert b"main" in resp.data
        assert b"nothing staged" in resp.data

        # cleanup registry entry
        registry.pop(name, None)
        with open(REGISTRY_FILE, "w") as f:
            json.dump(registry, f)

    def test_bad_repo_missing_minigit(self) -> None:
        """CLI find_repo returns None when .minigit is absent."""
        from cli import find_repo

        empty = tempfile.mkdtemp()
        try:
            assert find_repo(empty) is None
        finally:
            shutil.rmtree(empty)
