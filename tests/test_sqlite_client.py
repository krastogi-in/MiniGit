"""Tests for the SQLiteClient backend."""

import os
import tempfile

from backend.sqlite_client import SQLiteClient


class TestSQLiteClient:
    """Verify CRUD operations on the SQLite storage layer."""

    def setup_method(self) -> None:
        """Create a temporary database file."""
        self.fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.db = SQLiteClient(self.db_path)

    def teardown_method(self) -> None:
        """Close and remove the temporary database."""
        self.db.close()
        os.close(self.fd)
        os.unlink(self.db_path)

    def test_store_and_get_blob(self) -> None:
        """Stored blob is retrievable by hash."""
        h = "a" * 64
        self.db.store_blob(h, "hello world")
        assert self.db.get_blob(h) == "hello world"

    def test_get_missing_blob(self) -> None:
        """Missing blob returns None."""
        h = "b" * 64
        assert self.db.get_blob(h) is None

    def test_duplicate_blob_ignored(self) -> None:
        """Duplicate blob insert is silently ignored (first write wins)."""
        h = "c" * 64
        self.db.store_blob(h, "first")
        self.db.store_blob(h, "second")
        assert self.db.get_blob(h) == "first"

    def test_store_and_get_tree(self) -> None:
        """Stored tree entries are retrievable by hash."""
        h = "d" * 64
        entries = '[{"name":"f.txt","type":"blob","hash":"x"}]'
        self.db.store_tree(h, entries)
        assert self.db.get_tree(h) == entries

    def test_store_and_get_commit(self) -> None:
        """Stored commit is retrievable with all fields intact."""
        ch = "e" * 64
        th = "f" * 64
        self.db.store_commit(ch, th, None, None, "Alice", "init", "2026-01-01")
        c = self.db.get_commit(ch)
        assert c["hash"] == ch
        assert c["tree_hash"] == th
        assert c["parent_hash"] is None
        assert c["author"] == "Alice"
        assert c["message"] == "init"

    def test_get_missing_commit(self) -> None:
        """Missing commit returns None."""
        h = "0" * 64
        assert self.db.get_commit(h) is None

    def test_set_and_get_ref(self) -> None:
        """Ref can be set and retrieved."""
        h = "1" * 64
        self.db.set_ref("main", h)
        assert self.db.get_ref("main") == h

    def test_update_ref(self) -> None:
        """Ref can be updated to a new value."""
        old = "2" * 64
        new = "3" * 64
        self.db.set_ref("main", old)
        self.db.set_ref("main", new)
        assert self.db.get_ref("main") == new

    def test_get_missing_ref(self) -> None:
        """Missing ref returns None."""
        assert self.db.get_ref("nope") is None

    def test_get_all_refs(self) -> None:
        """get_all_refs returns all stored refs."""
        h1 = "4" * 64
        h2 = "5" * 64
        self.db.set_ref("main", h1)
        self.db.set_ref("dev", h2)
        refs = self.db.get_all_refs()
        names = {r["name"] for r in refs}
        assert names == {"main", "dev"}

    def test_delete_ref(self) -> None:
        """Deleted ref is no longer retrievable."""
        h = "6" * 64
        self.db.set_ref("feature", h)
        self.db.delete_ref("feature")
        assert self.db.get_ref("feature") is None

    def test_get_all_commits(self) -> None:
        """get_all_commits returns all stored commits."""
        h1 = "a" * 64
        h2 = "b" * 64
        t1 = "c" * 64
        t2 = "d" * 64
        self.db.store_commit(h1, t1, None, None, "A", "first", "2026-01-01")
        self.db.store_commit(h2, t2, h1, None, "A", "second", "2026-01-02")
        commits = self.db.get_all_commits()
        assert len(commits) == 2

    def test_store_commit_with_second_parent(self) -> None:
        """Merge commits persist both parent hashes."""
        commit_hash = "e" * 64
        tree_hash = "f" * 64
        parent1 = "1" * 64
        parent2 = "2" * 64
        self.db.store_commit(
            commit_hash,
            tree_hash,
            parent1,
            parent2,
            "Merge Bot",
            "merge commit",
            "2026-01-03",
        )
        commit = self.db.get_commit(commit_hash)
        assert commit["parent_hash"] == parent1
        assert commit["parent_hash2"] == parent2


class TestValidation:
    """Verify input validation rejects malformed data."""

    def setup_method(self) -> None:
        """Create a temporary database file."""
        self.fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.db = SQLiteClient(self.db_path)

    def teardown_method(self) -> None:
        """Close and remove the temporary database."""
        self.db.close()
        os.close(self.fd)
        os.unlink(self.db_path)

    def test_invalid_blob_hash_rejected(self) -> None:
        """Non-hex hash raises ValueError."""
        try:
            self.db.store_blob("not-a-hash", "data")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_sql_injection_in_hash_rejected(self) -> None:
        """SQL injection attempt in hash is rejected."""
        try:
            self.db.get_blob("'; DROP TABLE blobs; --")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_invalid_ref_name_rejected(self) -> None:
        """SQL injection in ref name is rejected."""
        try:
            self.db.set_ref("'; DROP TABLE refs;--", "a" * 64)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_ref_name_with_spaces_rejected(self) -> None:
        """Ref name with spaces is rejected."""
        try:
            self.db.set_ref("my branch", "a" * 64)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_non_string_author_rejected(self) -> None:
        """Non-string author raises TypeError."""
        try:
            self.db.store_commit(
                "a" * 64, "b" * 64, None, None, 12345, "msg", "ts")
            assert False, "Should have raised TypeError"
        except TypeError:
            pass

    def test_oversized_message_rejected(self) -> None:
        """Message exceeding max length raises ValueError."""
        try:
            self.db.store_commit(
                "a" * 64, "b" * 64, None, None, "A", "x" * 5001, "ts")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_valid_hash_accepted(self) -> None:
        """Valid 64-char hex hash is accepted."""
        valid = "a" * 64
        self.db.store_blob(valid, "content")
        assert self.db.get_blob(valid) == "content"

    def test_valid_ref_accepted(self) -> None:
        """Valid ref name with slashes and dashes is accepted."""
        self.db.set_ref("feature/my-branch", "a" * 64)
        assert self.db.get_ref("feature/my-branch") == "a" * 64
