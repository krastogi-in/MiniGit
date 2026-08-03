import json
import os
import sys

from backend.sqlite_client import SQLiteClient
from components.blob import Blob
from components.tree import Tree
from components.commit import Commit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class Operations:
    def __init__(self, repo_path, db_path=None):
        self.repo_path = repo_path
        self.branch = "main"
        if db_path is None:
            db_path = os.path.join(repo_path, ".minigit", "minigit.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = SQLiteClient(db_path)

    def init_repo(self, author=None, message=None):
        if author is None:
            author = os.getenv("USER", "unknown")
        if message is None:
            message = "Initial commit"

        commit_obj = Commit(
            self.repo_path,
            parent_commit_pointer=None,
            author=author,
            message=message
        )
        tree_obj = commit_obj.Tree_pointer
        self._store_tree(tree_obj)
        self.db.store_commit(
            commit_obj.get_hash(),
            tree_obj.get_hash(),
            None,
            commit_obj.author,
            commit_obj.message,
            commit_obj.timestamp
        )
        self.db.set_ref("main", commit_obj.get_hash())
        self.db.set_ref("HEAD", "main")
        return commit_obj.get_hash()

    def _store_tree(self, tree_obj):
        """Recursively store a tree and all its subtrees/blobs."""
        entries = []
        for name in sorted(tree_obj.files.keys()):
            child = tree_obj.files[name]
            if isinstance(child, Blob):
                entries.append({
                    "name": name,
                    "type": "blob",
                    "hash": child.get_hash()
                })
                self.db.store_blob(child.get_hash(), child.get_data())
            elif isinstance(child, Tree):
                entries.append({
                    "name": name,
                    "type": "tree",
                    "hash": child.get_hash()
                })
                self._store_tree(child)
        self.db.store_tree(tree_obj.get_hash(), json.dumps(entries))

    def create_branch(self, branch_name):
        existing = self.db.get_ref(branch_name)
        if existing:
            raise ValueError(f"Branch '{branch_name}' already exists")
        commit_hash = self.db.get_ref(self.branch)
        if not commit_hash:
            raise ValueError(f"Current branch '{self.branch}' has no commits")
        self.db.set_ref(branch_name, commit_hash)
        self.branch = branch_name
        return branch_name

    def checkout_branch(self, branch_name):
        commit_hash = self.db.get_ref(branch_name)
        if not commit_hash:
            raise ValueError(f"Branch '{branch_name}' does not exist")
        self.branch = branch_name
        return branch_name

    def get_all_branches(self):
        refs = self.db.get_all_refs()
        return [r for r in refs if r["name"] != "HEAD"]

    def delete_branch(self, branch_name):
        if branch_name == "main":
            raise ValueError("Cannot delete 'main' branch")
        if branch_name == self.branch:
            raise ValueError("Cannot delete the current branch")
        existing = self.db.get_ref(branch_name)
        if not existing:
            raise ValueError(f"Branch '{branch_name}' does not exist")
        self.db.delete_ref(branch_name)

    def add(self, file_path):
        """Stage a file for the next commit."""
        full_path = os.path.join(self.repo_path, file_path)
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(full_path, 'r') as f:
            content = f.read()
        blob = Blob(content)
        self.db.store_blob(blob.get_hash(), blob.get_data())
        self.db.stage_file(file_path, "add", blob.get_hash())
        return blob.get_hash()

    def delete_file(self, file_path):
        """Stage a file for deletion in the next commit."""
        parent_hash = self.db.get_ref(self.branch)
        if not parent_hash:
            raise ValueError("No commits yet")
        parent = self.db.get_commit(parent_hash)
        flat = self._flatten_tree(parent["tree_hash"])
        if file_path not in flat:
            raise FileNotFoundError(
                f"File not tracked: {file_path}")
        self.db.stage_file(file_path, "delete")

    def create_new_commit(self, message, author=None):
        """Create a new commit on the current branch."""
        if author is None:
            author = os.getenv("USER", "unknown")

        parent_hash = self.db.get_ref(self.branch)
        staged = self.db.get_staged()
        if not staged:
            raise ValueError("Nothing staged to commit")

        current_files = {}
        if parent_hash:
            parent = self.db.get_commit(parent_hash)
            if parent:
                current_files = self._flatten_tree(parent["tree_hash"])

        for entry in staged:
            if entry["action"] == "add":
                current_files[entry["path"]] = entry["blob_hash"]
            elif entry["action"] == "delete":
                current_files.pop(entry["path"], None)

        root_tree_hash = self._build_tree_from_flat(current_files)

        commit_obj = Commit(
            self.repo_path,
            parent_commit_pointer=parent_hash,
            author=author,
            message=message
        )
        commit_hash = commit_obj.get_hash()

        self.db.store_commit(
            commit_hash,
            root_tree_hash,
            parent_hash,
            commit_obj.author,
            commit_obj.message,
            commit_obj.timestamp
        )
        self.db.set_ref(self.branch, commit_hash)
        self.db.clear_staging()
        return commit_hash

    def _build_tree_from_flat(self, flat_files):
        """Build nested tree objects from a flat {path: blob_hash} dict."""
        root = {}
        for path, blob_hash in flat_files.items():
            parts = path.split("/")
            node = root
            for part in parts[:-1]:
                if part not in node:
                    node[part] = {}
                node = node[part]
            node[parts[-1]] = blob_hash

        return self._store_tree_from_dict(root)

    def _store_tree_from_dict(self, tree_dict):
        """Recursively store tree objects from a nested dict. Returns hash."""
        from hashlib import sha256
        entries = []
        for name in sorted(tree_dict.keys()):
            value = tree_dict[name]
            if isinstance(value, dict):
                child_hash = self._store_tree_from_dict(value)
                entries.append({
                    "name": name,
                    "type": "tree",
                    "hash": child_hash
                })
            else:
                entries.append({
                    "name": name,
                    "type": "blob",
                    "hash": value
                })
        entries_json = json.dumps(entries)
        tree_content = "\n".join(
            f"{e['type']} {e['hash']} {e['name']}"
            for e in entries
        )
        tree_hash = sha256(tree_content.encode()).hexdigest()
        self.db.store_tree(tree_hash, entries_json)
        return tree_hash

    def get_commit_history(self, branch_name=None):
        """Walk parent pointers and return list of commits."""
        if branch_name is None:
            branch_name = self.branch
        commit_hash = self.db.get_ref(branch_name)
        history = []
        while commit_hash:
            commit_data = self.db.get_commit(commit_hash)
            if not commit_data:
                break
            history.append(commit_data)
            commit_hash = commit_data["parent_hash"]
        return history

    def get_staged(self):
        """Return list of staged files."""
        return self.db.get_staged()

    def get_working_dir_files(self, subdir=""):
        """List files/dirs in the working directory for the UI explorer."""
        base = os.path.join(self.repo_path, subdir) if subdir else self.repo_path
        if not os.path.isdir(base):
            return []
        ignore_dirs = Tree.IGNORE_DIRS
        ignore_ext = Tree.IGNORE_EXTENSIONS
        items = []
        for name in sorted(os.listdir(base)):
            if name in ignore_dirs:
                continue
            full_path = os.path.join(base, name)
            rel_path = os.path.join(subdir, name) if subdir else name
            if os.path.isdir(full_path):
                items.append({
                    "name": name,
                    "path": rel_path,
                    "type": "dir"
                })
            elif os.path.isfile(full_path):
                _, ext = os.path.splitext(name)
                if ext.lower() in ignore_ext:
                    continue
                items.append({
                    "name": name,
                    "path": rel_path,
                    "type": "file"
                })
        return items

    # --- BROWSE / DIFF (used by UI) ---

    def browse_tree(self, tree_hash):
        """Return list of entries at a tree hash."""
        entries_json = self.db.get_tree(tree_hash)
        if not entries_json:
            return []
        return json.loads(entries_json)

    def get_blob_content(self, blob_hash):
        """Return file content for a blob hash."""
        return self.db.get_blob(blob_hash)

    def get_commit(self, commit_hash):
        """Return commit data dict."""
        return self.db.get_commit(commit_hash)

    def get_diffs(self, hash1, hash2):
        """Compute diff between two commits by comparing their trees."""
        commit1 = self.db.get_commit(hash1)
        commit2 = self.db.get_commit(hash2)
        if not commit1 or not commit2:
            return []

        files1 = self._flatten_tree(commit1["tree_hash"])
        files2 = self._flatten_tree(commit2["tree_hash"])

        all_paths = set(files1.keys()) | set(files2.keys())
        diffs = []
        for path in sorted(all_paths):
            old_hash = files1.get(path)
            new_hash = files2.get(path)
            if old_hash == new_hash:
                continue
            old_content = self.db.get_blob(old_hash) if old_hash else ""
            new_content = self.db.get_blob(new_hash) if new_hash else ""
            diffs.append({
                "path": path,
                "old_content": old_content or "",
                "new_content": new_content or "",
                "status": ("added" if not old_hash
                           else "deleted" if not new_hash
                           else "modified")
            })
        return diffs

    def _flatten_tree(self, tree_hash, prefix=""):
        """Walk a tree recursively, return {path: blob_hash} dict."""
        entries_json = self.db.get_tree(tree_hash)
        if not entries_json:
            return {}
        entries = json.loads(entries_json)
        result = {}
        for entry in entries:
            full_path = (f"{prefix}/{entry['name']}"
                         if prefix else entry["name"])
            if entry["type"] == "blob":
                result[full_path] = entry["hash"]
            elif entry["type"] == "tree":
                result.update(self._flatten_tree(entry["hash"], full_path))
        return result
