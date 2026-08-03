import re
import sqlite3


_HEX_HASH = re.compile(r'^[0-9a-f]{64}$')
_REF_NAME = re.compile(r'^[A-Za-z0-9_.\-/]+$')


def _validate_hash(value, label="hash"):
    if not isinstance(value, str) or not _HEX_HASH.match(value):
        raise ValueError(
            f"Invalid {label}: expected 64-char hex string, got {value!r}")


def _validate_ref_name(name):
    if not isinstance(name, str) or not _REF_NAME.match(name):
        raise ValueError(
            f"Invalid ref name: must be alphanumeric/dash/underscore/dot, "
            f"got {name!r}")


def _validate_str(value, label, max_len=10000):
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string, got {type(value).__name__}")
    if len(value) > max_len:
        raise ValueError(f"{label} exceeds max length of {max_len}")


class SQLiteClient:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS blobs (
                hash TEXT PRIMARY KEY,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS trees (
                hash TEXT PRIMARY KEY,
                entries TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS commits (
                hash TEXT PRIMARY KEY,
                tree_hash TEXT NOT NULL,
                parent_hash TEXT,
                author TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS refs (
                name TEXT PRIMARY KEY,
                commit_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS staging (
                path TEXT PRIMARY KEY,
                action TEXT NOT NULL,
                blob_hash TEXT
            );
        """)
        self.conn.commit()

    def store_blob(self, hash, data):
        _validate_hash(hash, "blob hash")
        _validate_str(data, "blob data", max_len=10_000_000)
        self.cursor.execute(
            "INSERT OR IGNORE INTO blobs (hash, data) VALUES (?, ?)",
            (hash, data)
        )
        self.conn.commit()

    def get_blob(self, hash):
        _validate_hash(hash, "blob hash")
        self.cursor.execute(
            "SELECT data FROM blobs WHERE hash = ?", (hash,)
        )
        row = self.cursor.fetchone()
        return row["data"] if row else None

    def store_tree(self, hash, entries_json):
        _validate_hash(hash, "tree hash")
        _validate_str(entries_json, "tree entries")
        self.cursor.execute(
            "INSERT OR IGNORE INTO trees (hash, entries) VALUES (?, ?)",
            (hash, entries_json)
        )
        self.conn.commit()

    def get_tree(self, hash):
        _validate_hash(hash, "tree hash")
        self.cursor.execute(
            "SELECT entries FROM trees WHERE hash = ?", (hash,)
        )
        row = self.cursor.fetchone()
        return row["entries"] if row else None

    def store_commit(self, hash, tree_hash, parent_hash,
                     author, message, timestamp):
        _validate_hash(hash, "commit hash")
        _validate_hash(tree_hash, "tree hash")
        if parent_hash is not None:
            _validate_hash(parent_hash, "parent hash")
        _validate_str(author, "author", max_len=200)
        _validate_str(message, "commit message", max_len=5000)
        _validate_str(timestamp, "timestamp", max_len=50)
        self.cursor.execute(
            "INSERT OR IGNORE INTO commits "
            "(hash, tree_hash, parent_hash, author, message, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (hash, tree_hash, parent_hash, author, message, timestamp)
        )
        self.conn.commit()

    def get_commit(self, hash):
        _validate_hash(hash, "commit hash")
        self.cursor.execute(
            "SELECT * FROM commits WHERE hash = ?", (hash,)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_commits(self):
        self.cursor.execute("SELECT * FROM commits ORDER BY timestamp DESC")
        return [dict(row) for row in self.cursor.fetchall()]

    def set_ref(self, name, commit_hash):
        _validate_ref_name(name)
        if name == "HEAD":
            _validate_ref_name(commit_hash)
        else:
            _validate_hash(commit_hash, "commit hash")
        self.cursor.execute(
            "INSERT OR REPLACE INTO refs (name, commit_hash) VALUES (?, ?)",
            (name, commit_hash)
        )
        self.conn.commit()

    def get_ref(self, name):
        _validate_ref_name(name)
        self.cursor.execute(
            "SELECT commit_hash FROM refs WHERE name = ?", (name,)
        )
        row = self.cursor.fetchone()
        return row["commit_hash"] if row else None

    def get_all_refs(self):
        self.cursor.execute("SELECT name, commit_hash FROM refs")
        return [dict(row) for row in self.cursor.fetchall()]

    def delete_ref(self, name):
        _validate_ref_name(name)
        self.cursor.execute("DELETE FROM refs WHERE name = ?", (name,))
        self.conn.commit()

    def stage_file(self, path, action, blob_hash=None):
        """Stage a file. action is 'add' or 'delete'."""
        _validate_str(path, "file path", max_len=1000)
        if action not in ("add", "delete"):
            raise ValueError(f"Invalid action: {action!r}")
        if action == "add" and blob_hash:
            _validate_hash(blob_hash, "blob hash")
        self.cursor.execute(
            "INSERT OR REPLACE INTO staging (path, action, blob_hash) "
            "VALUES (?, ?, ?)",
            (path, action, blob_hash)
        )
        self.conn.commit()

    def get_staged(self):
        self.cursor.execute("SELECT path, action, blob_hash FROM staging")
        return [dict(row) for row in self.cursor.fetchall()]

    def clear_staging(self):
        self.cursor.execute("DELETE FROM staging")
        self.conn.commit()

    def close(self):
        self.conn.close()
