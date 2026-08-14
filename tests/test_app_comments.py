"""Flask route tests for review comments."""

from __future__ import annotations

import json
import os
import shutil
import tempfile

from app import app
from frontend.operations import Operations


class TestAppComments:
    """Verify web UI routes for adding and addressing comments."""

    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.repos_dir = os.path.join(self.tmpdir, "repos")
        os.makedirs(self.repos_dir)
        self.repo_name = "testrepo"
        self.repo_path = os.path.join(self.repos_dir, self.repo_name)
        os.makedirs(self.repo_path)
        self.db_path = os.path.join(self.repo_path, ".minigit", "minigit.db")
        ops = Operations(self.repo_path, self.db_path)
        ops.init_repo(author="Tester", message="init")
        self.parent = ops.get_commit_history()[0]["hash"]
        with open(os.path.join(self.repo_path, "README.md"), "w") as f:
            f.write("# Updated\n")
        ops.add("README.md")
        self.head = ops.create_new_commit("second")
        registry = {self.repo_name: self.repo_path}
        with open(os.path.join(self.repos_dir, "repos.json"), "w") as f:
            json.dump(registry, f)
        app.config["TESTING"] = True
        self.client = app.test_client()
        self._orig_repos = app.REPOS_DIR if hasattr(app, "REPOS_DIR") else None
        import app as app_module
        app_module.REPOS_DIR = self.repos_dir
        app_module.REGISTRY_FILE = os.path.join(self.repos_dir, "repos.json")

    def teardown_method(self) -> None:
        shutil.rmtree(self.tmpdir)

    def test_add_and_address_comment_via_web(self) -> None:
        add_resp = self.client.post(
            f"/repo/{self.repo_name}/commit/{self.head}/comments",
            data={
                "base_hash": self.parent,
                "path": "README.md",
                "line": "1",
                "body": "Please clarify",
            },
            follow_redirects=False,
        )
        assert add_resp.status_code == 302
        ops = Operations(self.repo_path, self.db_path)
        comments = ops.list_review_comments(self.parent, self.head, "all")
        assert len(comments) == 1
        comment_id = comments[0]["id"]
        addr_resp = self.client.post(
            f"/repo/{self.repo_name}/comments/{comment_id}/address",
            data={"commit_hash": self.head},
            follow_redirects=False,
        )
        assert addr_resp.status_code == 302
        updated = ops.get_review_comment(comment_id) if hasattr(ops, "get_review_comment") else ops.db.get_review_comment(comment_id)
        assert updated["status"] == "addressed"

    def test_commit_detail_shows_comment_form(self) -> None:
        resp = self.client.get(f"/repo/{self.repo_name}/commit/{self.head}")
        assert resp.status_code == 200
        assert b"Add review comment" in resp.data

    def test_add_comment_missing_fields(self) -> None:
        resp = self.client.post(
            f"/repo/{self.repo_name}/commit/{self.head}/comments",
            data={"base_hash": self.parent, "path": "", "line": "", "body": ""},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"required" in resp.data.lower()
