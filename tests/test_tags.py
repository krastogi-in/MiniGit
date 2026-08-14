"""Tests for tag support: Operations.create_tag/delete_tag/get_all_tags/resolve_ref."""

import os
import shutil
import tempfile

import pytest

from frontend.operations import Operations


class TestTags:
    """Verify tag creation, listing, deletion, and resolution."""

    def setup_method(self) -> None:
        """Create a temporary repo directory with an initial commit."""
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "README.md"), "w") as f:
            f.write("# Test Project\n")
        self.db_path = os.path.join(self.tmpdir, ".minigit", "minigit.db")

    def teardown_method(self) -> None:
        """Clean up the temporary directory."""
        shutil.rmtree(self.tmpdir)

    def _init_ops(self) -> Operations:
        """Helper to initialize a repo and return the Operations instance."""
        ops = Operations(self.tmpdir, self.db_path)
        ops.init_repo(author="Tester", message="Initial commit")
        return ops

    def test_create_tag_defaults_to_branch_tip(self) -> None:
        """Creating a tag with no explicit commit resolves to the current tip."""
        ops = self._init_ops()
        tip = ops.db.get_ref("main")
        ops.create_tag("v1.0", tagger="Tester", message="release")
        tag = ops.db.get_tag("v1.0")
        assert tag["commit_hash"] == tip

    def test_create_tag_against_explicit_commit(self) -> None:
        """Creating a tag against an explicit hash uses that hash, not the tip."""
        ops = self._init_ops()
        first_commit = ops.db.get_ref("main")
        ops.add("README.md")
        ops.create_new_commit("second commit", author="Tester")
        ops.create_tag("v0.1", commit_hash=first_commit, tagger="Tester", message="early point")
        tag = ops.db.get_tag("v0.1")
        assert tag["commit_hash"] == first_commit
        assert tag["commit_hash"] != ops.db.get_ref("main")

    def test_list_tags(self) -> None:
        """get_all_tags returns all created tags."""
        ops = self._init_ops()
        ops.create_tag("v1.0", tagger="Tester", message="first")
        ops.create_tag("v2.0", tagger="Tester", message="second")
        names = {t["name"] for t in ops.get_all_tags()}
        assert names == {"v1.0", "v2.0"}

    def test_delete_tag(self) -> None:
        """A deleted tag can be recreated with the same name."""
        ops = self._init_ops()
        ops.create_tag("temp", tagger="Tester", message="msg")
        ops.delete_tag("temp")
        assert ops.db.get_tag("temp") is None
        ops.create_tag("temp", tagger="Tester", message="recreated")
        assert ops.db.get_tag("temp") is not None

    def test_delete_missing_tag_raises(self) -> None:
        """Deleting a nonexistent tag raises ValueError."""
        ops = self._init_ops()
        with pytest.raises(ValueError):
            ops.delete_tag("nope")

    def test_duplicate_tag_name_rejected(self) -> None:
        """Creating a tag with an existing name raises ValueError."""
        ops = self._init_ops()
        ops.create_tag("v1.0", tagger="Tester", message="first")
        with pytest.raises(ValueError):
            ops.create_tag("v1.0", tagger="Tester", message="second")

    def test_invalid_tag_name_rejected(self) -> None:
        """Tag name with spaces raises ValueError before any DB write."""
        ops = self._init_ops()
        with pytest.raises(ValueError):
            ops.create_tag("bad name", tagger="Tester", message="msg")

    def test_tag_name_collides_with_branch_rejected(self) -> None:
        """Creating a tag with the same name as an existing branch raises ValueError."""
        ops = self._init_ops()
        ops.create_branch("release")
        ops.checkout_branch("main")
        with pytest.raises(ValueError):
            ops.create_tag("release", tagger="Tester", message="msg")

    def test_create_tag_unknown_commit_rejected(self) -> None:
        """Creating a tag against a commit hash that doesn't exist raises ValueError."""
        ops = self._init_ops()
        with pytest.raises(ValueError):
            ops.create_tag("v1.0", commit_hash="a" * 64, tagger="Tester", message="msg")

    def test_tag_immutable_across_new_commits(self) -> None:
        """A tag keeps pointing at its original commit after the branch advances."""
        ops = self._init_ops()
        tagged_commit = ops.db.get_ref("main")
        ops.create_tag("v1.0", tagger="Tester", message="snapshot")
        ops.add("README.md")
        ops.create_new_commit("advance branch", author="Tester")
        tag = ops.db.get_tag("v1.0")
        assert tag["commit_hash"] == tagged_commit
        assert tag["commit_hash"] != ops.db.get_ref("main")

    def test_resolve_ref_commit_hash(self) -> None:
        """resolve_ref returns a valid commit hash unchanged."""
        ops = self._init_ops()
        tip = ops.db.get_ref("main")
        assert ops.resolve_ref(tip) == tip

    def test_resolve_ref_branch_name(self) -> None:
        """resolve_ref resolves a branch name to its tip commit."""
        ops = self._init_ops()
        tip = ops.db.get_ref("main")
        assert ops.resolve_ref("main") == tip

    def test_resolve_ref_tag_name(self) -> None:
        """resolve_ref resolves a tag name to its pinned commit."""
        ops = self._init_ops()
        tip = ops.db.get_ref("main")
        ops.create_tag("v1.0", tagger="Tester", message="release")
        assert ops.resolve_ref("v1.0") == tip

    def test_resolve_ref_unknown_raises(self) -> None:
        """resolve_ref raises ValueError for a name that matches nothing."""
        ops = self._init_ops()
        with pytest.raises(ValueError):
            ops.resolve_ref("does-not-exist")
