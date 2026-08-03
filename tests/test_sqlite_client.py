import os
import tempfile

from backend.sqlite_client import SQLiteClient


class TestSQLiteClient:
    def setup_method(self):
        self.fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.db = SQLiteClient(self.db_path)

    def teardown_method(self):
        self.db.close()
        os.close(self.fd)
        os.unlink(self.db_path)

    def test_store_and_get_blob(self):
        h = "a" * 64
        self.db.store_blob(h, "hello world")
        assert self.db.get_blob(h) == "hello world"

    def test_get_missing_blob(self):
        h = "b" * 64
        assert self.db.get_blob(h) is None

    def test_duplicate_blob_ignored(self):
        h = "c" * 64
        self.db.store_blob(h, "first")
        self.db.store_blob(h, "second")
        assert self.db.get_blob(h) == "first"

    def test_store_and_get_tree(self):
        h = "d" * 64
        entries = '[{"name":"f.txt","type":"blob","hash":"x"}]'
        self.db.store_tree(h, entries)
        assert self.db.get_tree(h) == entries

    def test_store_and_get_commit(self):
        ch = "e" * 64
        th = "f" * 64
        self.db.store_commit(ch, th, None, "Alice", "init", "2026-01-01")
        c = self.db.get_commit(ch)
        assert c["hash"] == ch
        assert c["tree_hash"] == th
        assert c["parent_hash"] is None
        assert c["author"] == "Alice"
        assert c["message"] == "init"

    def test_get_missing_commit(self):
        h = "0" * 64
        assert self.db.get_commit(h) is None

    def test_set_and_get_ref(self):
        h = "1" * 64
        self.db.set_ref("main", h)
        assert self.db.get_ref("main") == h

    def test_update_ref(self):
        old = "2" * 64
        new = "3" * 64
        self.db.set_ref("main", old)
        self.db.set_ref("main", new)
        assert self.db.get_ref("main") == new

    def test_get_missing_ref(self):
        assert self.db.get_ref("nope") is None

    def test_get_all_refs(self):
        h1 = "4" * 64
        h2 = "5" * 64
        self.db.set_ref("main", h1)
        self.db.set_ref("dev", h2)
        refs = self.db.get_all_refs()
        names = {r["name"] for r in refs}
        assert names == {"main", "dev"}

    def test_delete_ref(self):
        h = "6" * 64
        self.db.set_ref("feature", h)
        self.db.delete_ref("feature")
        assert self.db.get_ref("feature") is None

    def test_get_all_commits(self):
        h1 = "a" * 64
        h2 = "b" * 64
        t1 = "c" * 64
        t2 = "d" * 64
        self.db.store_commit(h1, t1, None, "A", "first", "2026-01-01")
        self.db.store_commit(h2, t2, h1, "A", "second", "2026-01-02")
        commits = self.db.get_all_commits()
        assert len(commits) == 2


class TestValidation:
    def setup_method(self):
        self.fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.db = SQLiteClient(self.db_path)

    def teardown_method(self):
        self.db.close()
        os.close(self.fd)
        os.unlink(self.db_path)

    def test_invalid_blob_hash_rejected(self):
        try:
            self.db.store_blob("not-a-hash", "data")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_sql_injection_in_hash_rejected(self):
        try:
            self.db.get_blob("'; DROP TABLE blobs; --")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_invalid_ref_name_rejected(self):
        try:
            self.db.set_ref("'; DROP TABLE refs;--", "a" * 64)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_ref_name_with_spaces_rejected(self):
        try:
            self.db.set_ref("my branch", "a" * 64)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_non_string_author_rejected(self):
        try:
            self.db.store_commit(
                "a" * 64, "b" * 64, None, 12345, "msg", "ts")
            assert False, "Should have raised TypeError"
        except TypeError:
            pass

    def test_oversized_message_rejected(self):
        try:
            self.db.store_commit(
                "a" * 64, "b" * 64, None, "A", "x" * 5001, "ts")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_valid_hash_accepted(self):
        valid = "a" * 64
        self.db.store_blob(valid, "content")
        assert self.db.get_blob(valid) == "content"

    def test_valid_ref_accepted(self):
        self.db.set_ref("feature/my-branch", "a" * 64)
        assert self.db.get_ref("feature/my-branch") == "a" * 64
