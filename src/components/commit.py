"""Commit object — snapshot pointing to a tree, parent, author, and message."""

from __future__ import annotations

import os
from datetime import datetime
from hashlib import sha256

from components.tree import Tree


class Commit:
    """A commit represents a point-in-time snapshot of the repository.

    Each commit points to a root Tree, an optional parent commit (and optional
    second parent for merges), and carries metadata (author, message, timestamp).
    """

    def __init__(
        self,
        path: str,
        parent_commit_pointer: str | Commit | None = None,
        author: str | None = None,
        message: str | None = None,
        timestamp: str | None = None,
        second_parent_commit_pointer: str | Commit | None = None,
    ) -> None:
        self.Tree_pointer: Tree = Tree(path)
        self.parent_commit_pointer: str | Commit | None = parent_commit_pointer
        self.second_parent_commit_pointer: str | Commit | None = (
            second_parent_commit_pointer
        )
        self.author: str = author if author is not None else os.getenv("USER", "unknown")
        self.message: str = message if message is not None else "No message"
        self.timestamp: str = (
            timestamp
            if timestamp is not None
            else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    @staticmethod
    def hash_from_fields(
        tree_hash: str,
        parent_hash: str | None,
        author: str,
        message: str,
        timestamp: str,
        second_parent_hash: str | None = None,
    ) -> str:
        """Compute commit hash from explicit fields (used for merge commits)."""
        parent = parent_hash or ""
        if second_parent_hash:
            content = f"{tree_hash}{parent}{second_parent_hash}{author}{message}{timestamp}"
        else:
            content = f"{tree_hash}{parent}{author}{message}{timestamp}"
        return sha256(content.encode()).hexdigest()

    def get_hash(self) -> str:
        """Compute SHA-256 hash from tree hash + parent(s) + author + message + timestamp."""
        return self.hash_from_fields(
            self.Tree_pointer.get_hash(),
            self.get_parent_hash(),
            self.author,
            self.message,
            self.timestamp,
            self.get_second_parent_hash(),
        )

    def get_parent_hash(self) -> str | None:
        """Return the parent commit hash, or None for root commits."""
        if self.parent_commit_pointer is None:
            return None
        if isinstance(self.parent_commit_pointer, str):
            return self.parent_commit_pointer
        return self.parent_commit_pointer.get_hash()

    def get_second_parent_hash(self) -> str | None:
        """Return the second parent hash for merge commits, or None."""
        if self.second_parent_commit_pointer is None:
            return None
        if isinstance(self.second_parent_commit_pointer, str):
            return self.second_parent_commit_pointer
        return self.second_parent_commit_pointer.get_hash()
