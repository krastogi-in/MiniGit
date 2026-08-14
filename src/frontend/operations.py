"""High-level Git operations orchestrating components and backend."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from hashlib import sha256
from typing import Any

import structlog

from backend.sqlite_client import SQLiteClient
from components.blob import Blob
from components.commit import Commit
from components.tree import Tree

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logger = structlog.get_logger(__name__)


class Operations:
    """Orchestrates MiniGit operations: init, branch, stage, commit, diff.

    Acts as the primary interface between the CLI/web UI and the
    underlying storage + object model layers.
    """

    def __init__(self, repo_path: str, db_path: str | None = None) -> None:
        self.repo_path: str = repo_path
        self.branch: str = "main"
        if db_path is None:
            db_path = os.path.join(repo_path, ".minigit", "minigit.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db: SQLiteClient = SQLiteClient(db_path)

    def init_repo(self, author: str | None = None, message: str | None = None) -> str:
        """Initialize a new repository with an initial commit.

        Returns the hash of the initial commit.
        """
        if author is None:
            author = os.getenv("USER", "unknown")
        if message is None:
            message = "Initial commit"

        commit_obj = Commit(
            self.repo_path,
            parent_commit_pointer=None,
            author=author,
            message=message,
        )
        tree_obj = commit_obj.Tree_pointer
        self._store_tree(tree_obj)
        self.db.store_commit(
            commit_obj.get_hash(),
            tree_obj.get_hash(),
            None,
            None,
            commit_obj.author,
            commit_obj.message,
            commit_obj.timestamp,
        )
        self.db.set_ref("main", commit_obj.get_hash())
        self.db.set_ref("HEAD", "main")
        logger.info("repo_initialized", path=self.repo_path)
        return commit_obj.get_hash()

    def _store_tree(self, tree_obj: Tree) -> None:
        """Recursively persist a tree and all its child blobs/subtrees."""
        entries: list[dict[str, str]] = []
        for name in sorted(tree_obj.files.keys()):
            child = tree_obj.files[name]
            if isinstance(child, Blob):
                entries.append({"name": name, "type": "blob", "hash": child.get_hash()})
                self.db.store_blob(child.get_hash(), child.get_data())
            elif isinstance(child, Tree):
                entries.append({"name": name, "type": "tree", "hash": child.get_hash()})
                self._store_tree(child)
        self.db.store_tree(tree_obj.get_hash(), json.dumps(entries))

    def create_branch(self, branch_name: str) -> str:
        """Create a new branch pointing to the current branch's HEAD commit.

        Returns the branch name. Raises ValueError if branch already exists.
        """
        existing = self.db.get_ref(branch_name)
        if existing:
            raise ValueError(f"Branch '{branch_name}' already exists")
        commit_hash = self.db.get_ref(self.branch)
        if not commit_hash:
            raise ValueError(f"Current branch '{self.branch}' has no commits")
        self.db.set_ref(branch_name, commit_hash)
        self.branch = branch_name
        return branch_name

    def checkout_branch(self, branch_name: str) -> str:
        """Switch the active branch. Raises ValueError if branch doesn't exist."""
        commit_hash = self.db.get_ref(branch_name)
        if not commit_hash:
            raise ValueError(f"Branch '{branch_name}' does not exist")
        self.branch = branch_name
        return branch_name

    def get_all_branches(self) -> list[dict[str, str]]:
        """Return all branch refs (excludes HEAD)."""
        refs = self.db.get_all_refs()
        return [r for r in refs if r["name"] != "HEAD"]

    def delete_branch(self, branch_name: str) -> None:
        """Delete a branch ref. Cannot delete 'main' or the current branch."""
        if branch_name == "main":
            raise ValueError("Cannot delete 'main' branch")
        if branch_name == self.branch:
            raise ValueError("Cannot delete the current branch")
        existing = self.db.get_ref(branch_name)
        if not existing:
            raise ValueError(f"Branch '{branch_name}' does not exist")
        self.db.delete_ref(branch_name)

    def add(self, file_path: str) -> str:
        """Stage a file for the next commit. Returns the blob hash."""
        full_path = os.path.join(self.repo_path, file_path)
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(full_path, "r") as f:
            content = f.read()
        blob = Blob(content)
        self.db.store_blob(blob.get_hash(), blob.get_data())
        self.db.stage_file(file_path, "add", blob.get_hash())
        return blob.get_hash()

    def delete_file(self, file_path: str) -> None:
        """Stage a file for deletion in the next commit."""
        parent_hash = self.db.get_ref(self.branch)
        if not parent_hash:
            raise ValueError("No commits yet")
        parent = self.db.get_commit(parent_hash)
        if not parent:
            raise ValueError("Parent commit not found")
        flat = self._flatten_tree(parent["tree_hash"])
        if file_path not in flat:
            raise FileNotFoundError(f"File not tracked: {file_path}")
        self.db.stage_file(file_path, "delete")

    def create_new_commit(self, message: str, author: str | None = None) -> str:
        """Create a new commit on the current branch from staged changes.

        Returns the new commit hash. Raises ValueError if nothing is staged.
        """
        if author is None:
            author = os.getenv("USER", "unknown")

        parent_hash = self.db.get_ref(self.branch)
        staged = self.db.get_staged()
        if not staged:
            raise ValueError("Nothing staged to commit")

        current_files: dict[str, str] = {}
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
            message=message,
        )
        commit_hash = self._compute_commit_hash(
            root_tree_hash,
            parent_hash,
            None,
            commit_obj.author,
            commit_obj.message,
            commit_obj.timestamp,
        )

        self.db.store_commit(
            commit_hash,
            root_tree_hash,
            parent_hash,
            None,
            commit_obj.author,
            commit_obj.message,
            commit_obj.timestamp,
        )
        self.db.set_ref(self.branch, commit_hash)
        self.db.clear_staging()
        logger.info("commit_created", hash=commit_hash[:8], message=message)
        return commit_hash

    def merge(
        self,
        source_ref: str,
        author: str | None = None,
        message: str | None = None,
    ) -> dict[str, str]:
        """Merge source branch/ref into the current branch."""
        if author is None:
            author = os.getenv("USER", "unknown")
        target_tip = self.db.get_ref(self.branch)
        if not target_tip:
            raise ValueError(f"Current branch '{self.branch}' has no commits")

        source_tip = self._resolve_commit_ref(source_ref)
        if not source_tip:
            raise ValueError(f"Source ref '{source_ref}' does not exist")

        if target_tip == source_tip:
            return {"status": "already-up-to-date", "commit_hash": target_tip}

        target_ancestors = self._collect_ancestors(target_tip)
        source_ancestors = self._collect_ancestors(source_tip)

        if source_tip in target_ancestors:
            return {"status": "already-up-to-date", "commit_hash": target_tip}

        if target_tip in source_ancestors:
            self.db.set_ref(self.branch, source_tip)
            return {"status": "fast-forward", "commit_hash": source_tip}

        base_hash = self._find_merge_base(target_tip, source_tip)
        if not base_hash:
            raise ValueError("Unable to determine merge base")

        merge_result = self._merge_trees(base_hash, target_tip, source_tip)
        if merge_result["conflicts"]:
            conflicts = ", ".join(merge_result["conflicts"])
            raise ValueError(f"Merge conflict detected in: {conflicts}")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        merge_message = message or f"Merge branch '{source_ref}' into '{self.branch}'"
        merge_commit_hash = self._compute_commit_hash(
            merge_result["tree_hash"],
            target_tip,
            source_tip,
            author,
            merge_message,
            timestamp,
        )
        self.db.store_commit(
            merge_commit_hash,
            merge_result["tree_hash"],
            target_tip,
            source_tip,
            author,
            merge_message,
            timestamp,
        )
        self.db.set_ref(self.branch, merge_commit_hash)
        return {"status": "merged", "commit_hash": merge_commit_hash}

    def _resolve_commit_ref(self, ref: str) -> str | None:
        """Resolve branch name or commit hash to a commit hash."""
        ref_commit = self.db.get_ref(ref)
        if ref_commit:
            return ref_commit
        if len(ref) == 64 and all(c in "0123456789abcdef" for c in ref):
            return ref if self.db.get_commit(ref) else None
        return None

    def _collect_ancestors(self, commit_hash: str) -> dict[str, int]:
        """Return ancestor distance map for a commit."""
        distances: dict[str, int] = {}
        queue: list[tuple[str, int]] = [(commit_hash, 0)]
        while queue:
            current, depth = queue.pop(0)
            if current in distances and distances[current] <= depth:
                continue
            commit = self.db.get_commit(current)
            if not commit:
                continue
            distances[current] = depth
            for parent_key in ("parent_hash", "parent_hash2"):
                parent_hash = commit.get(parent_key)
                if parent_hash:
                    queue.append((parent_hash, depth + 1))
        return distances

    def _find_merge_base(self, target_tip: str, source_tip: str) -> str | None:
        """Find the nearest common ancestor commit hash."""
        target_ancestors = self._collect_ancestors(target_tip)
        source_ancestors = self._collect_ancestors(source_tip)
        common = set(target_ancestors.keys()) & set(source_ancestors.keys())
        if not common:
            return None
        return min(common, key=lambda h: target_ancestors[h] + source_ancestors[h])

    def _merge_trees(
        self,
        base_hash: str,
        target_tip: str,
        source_tip: str,
    ) -> dict[str, Any]:
        """Perform simplified file-level three-way merge by blob hashes."""
        base_commit = self.db.get_commit(base_hash)
        target_commit = self.db.get_commit(target_tip)
        source_commit = self.db.get_commit(source_tip)
        if not base_commit or not target_commit or not source_commit:
            raise ValueError("Missing commits required for merge")

        base_files = self._flatten_tree(base_commit["tree_hash"])
        target_files = self._flatten_tree(target_commit["tree_hash"])
        source_files = self._flatten_tree(source_commit["tree_hash"])

        merged_files: dict[str, str] = {}
        conflicts: list[str] = []
        all_paths = set(base_files.keys()) | set(target_files.keys()) | set(source_files.keys())
        for path in sorted(all_paths):
            base_blob = base_files.get(path)
            target_blob = target_files.get(path)
            source_blob = source_files.get(path)

            if target_blob == source_blob:
                resolved = target_blob
            elif target_blob == base_blob:
                resolved = source_blob
            elif source_blob == base_blob:
                resolved = target_blob
            else:
                conflicts.append(path)
                continue

            if resolved is not None:
                merged_files[path] = resolved

        if conflicts:
            return {"conflicts": conflicts, "tree_hash": ""}
        return {"conflicts": [], "tree_hash": self._build_tree_from_flat(merged_files)}

    def _compute_commit_hash(
        self,
        tree_hash: str,
        parent_hash: str | None,
        parent_hash2: str | None,
        author: str,
        message: str,
        timestamp: str,
    ) -> str:
        """Compute commit hash from commit payload fields."""
        parent1 = parent_hash or ""
        parent2 = parent_hash2 or ""
        content = f"{tree_hash}{parent1}{parent2}{author}{message}{timestamp}"
        return sha256(content.encode()).hexdigest()

    def _build_tree_from_flat(self, flat_files: dict[str, str]) -> str:
        """Build nested tree objects from a flat {path: blob_hash} dict. Returns root hash."""
        root: dict[str, Any] = {}
        for path, blob_hash in flat_files.items():
            parts = path.split("/")
            node = root
            for part in parts[:-1]:
                if part not in node:
                    node[part] = {}
                node = node[part]
            node[parts[-1]] = blob_hash

        return self._store_tree_from_dict(root)

    def _store_tree_from_dict(self, tree_dict: dict[str, Any]) -> str:
        """Recursively store tree objects from a nested dict. Returns the tree hash."""
        entries: list[dict[str, str]] = []
        for name in sorted(tree_dict.keys()):
            value = tree_dict[name]
            if isinstance(value, dict):
                child_hash = self._store_tree_from_dict(value)
                entries.append({"name": name, "type": "tree", "hash": child_hash})
            else:
                entries.append({"name": name, "type": "blob", "hash": value})
        entries_json = json.dumps(entries)
        tree_content = "\n".join(f"{e['type']} {e['hash']} {e['name']}" for e in entries)
        tree_hash = sha256(tree_content.encode()).hexdigest()
        self.db.store_tree(tree_hash, entries_json)
        return tree_hash

    def get_commit_history(self, branch_name: str | None = None) -> list[dict[str, Any]]:
        """Walk parent pointers from branch HEAD. Returns list of commit dicts."""
        if branch_name is None:
            branch_name = self.branch
        commit_hash = self.db.get_ref(branch_name)
        history: list[dict[str, Any]] = []
        while commit_hash:
            commit_data = self.db.get_commit(commit_hash)
            if not commit_data:
                break
            history.append(commit_data)
            commit_hash = commit_data["parent_hash"]
        return history

    def get_staged(self) -> list[dict[str, Any]]:
        """Return the list of currently staged file entries."""
        return self.db.get_staged()

    def get_working_dir_files(self, subdir: str = "") -> list[dict[str, str]]:
        """List files and directories in the working directory for the UI explorer."""
        base = os.path.join(self.repo_path, subdir) if subdir else self.repo_path
        if not os.path.isdir(base):
            return []
        ignore_dirs = Tree.IGNORE_DIRS
        ignore_ext = Tree.IGNORE_EXTENSIONS
        items: list[dict[str, str]] = []
        for name in sorted(os.listdir(base)):
            if name in ignore_dirs:
                continue
            full_path = os.path.join(base, name)
            rel_path = os.path.join(subdir, name) if subdir else name
            if os.path.isdir(full_path):
                items.append({"name": name, "path": rel_path, "type": "dir"})
            elif os.path.isfile(full_path):
                _, ext = os.path.splitext(name)
                if ext.lower() in ignore_ext:
                    continue
                items.append({"name": name, "path": rel_path, "type": "file"})
        return items

    def browse_tree(self, tree_hash: str) -> list[dict[str, str]]:
        """Return the list of entries at a given tree hash."""
        entries_json = self.db.get_tree(tree_hash)
        if not entries_json:
            return []
        return json.loads(entries_json)

    def get_blob_content(self, blob_hash: str) -> str | None:
        """Return file content for a blob hash, or None if not found."""
        return self.db.get_blob(blob_hash)

    def get_commit(self, commit_hash: str) -> dict[str, Any] | None:
        """Return commit data dict by hash, or None if not found."""
        return self.db.get_commit(commit_hash)

    def get_diffs(self, hash1: str, hash2: str) -> list[dict[str, str]]:
        """Compute diff between two commits by comparing their flattened trees."""
        commit1 = self.db.get_commit(hash1)
        commit2 = self.db.get_commit(hash2)
        if not commit1 or not commit2:
            return []

        files1 = self._flatten_tree(commit1["tree_hash"])
        files2 = self._flatten_tree(commit2["tree_hash"])

        all_paths = set(files1.keys()) | set(files2.keys())
        diffs: list[dict[str, str]] = []
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
                "status": (
                    "added" if not old_hash else "deleted" if not new_hash else "modified"
                ),
            })
        return diffs

    def _flatten_tree(self, tree_hash: str, prefix: str = "") -> dict[str, str]:
        """Walk a tree recursively, returning a flat {path: blob_hash} mapping."""
        entries_json = self.db.get_tree(tree_hash)
        if not entries_json:
            return {}
        entries = json.loads(entries_json)
        result: dict[str, str] = {}
        for entry in entries:
            full_path = f"{prefix}/{entry['name']}" if prefix else entry["name"]
            if entry["type"] == "blob":
                result[full_path] = entry["hash"]
            elif entry["type"] == "tree":
                result.update(self._flatten_tree(entry["hash"], full_path))
        return result
