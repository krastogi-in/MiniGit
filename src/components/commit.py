"""Commit object — snapshot pointing to a tree, parent, author, and message."""

from __future__ import annotations

import os
from datetime import datetime
from hashlib import sha256

from components.tree import Tree


class Commit:
    """A commit represents a point-in-time snapshot of the repository.

    Each commit points to a root Tree, an optional parent commit, and
    carries metadata (author, message, timestamp). The commit hash is
    derived from all these fields combined.
    """

    def __init__(
        self,
        path: str,
        parent_commit_pointer: str | Commit | None = None,
        author: str | None = None,
        message: str | None = None,
        timestamp: str | None = None,
    ) -> None:
        self.Tree_pointer: Tree = Tree(path)
        self.parent_commit_pointer: str | Commit | None = parent_commit_pointer
        self.author: str = author if author is not None else os.getenv("USER", "unknown")
        self.message: str = message if message is not None else "No message"
        self.timestamp: str = (
            timestamp
            if timestamp is not None
            else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def get_hash(self) -> str:
        """Compute SHA-256 hash from tree hash + parent + author + message + timestamp."""
        if self.parent_commit_pointer is None:
            parent_hash = ""
        elif isinstance(self.parent_commit_pointer, str):
            parent_hash = self.parent_commit_pointer
        else:
            parent_hash = self.parent_commit_pointer.get_hash()
        content = (
            f"{self.Tree_pointer.get_hash()}"
            f"{parent_hash}"
            f"{self.author}"
            f"{self.message}"
            f"{self.timestamp}"
        )
        return sha256(content.encode()).hexdigest()

    def get_parent_hash(self) -> str | None:
        """Return the parent commit hash, or None for root commits."""
        if self.parent_commit_pointer is None:
            return None
        if isinstance(self.parent_commit_pointer, str):
            return self.parent_commit_pointer
        return self.parent_commit_pointer.get_hash()
