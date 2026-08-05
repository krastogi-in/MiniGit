"""Tree object — recursive directory structure with content-addressed hashing."""

from __future__ import annotations

import os
from hashlib import sha256

from components.blob import Blob


class Tree:
    """Recursive directory snapshot that maps filenames to Blobs or sub-Trees.

    Walks the filesystem at construction time, skipping ignored directories
    and binary file extensions. The tree hash is computed from sorted entries,
    enabling change detection by comparing hashes.
    """

    IGNORE_DIRS: set[str] = {
        ".minigit", ".git", "__pycache__", ".pytest_cache",
        "node_modules", ".venv", "venv", ".tox", ".mypy_cache",
        ".eggs", "*.egg-info", "dist", "build",
    }
    IGNORE_EXTENSIONS: set[str] = {
        ".pyc", ".pyo", ".so", ".o", ".a", ".dylib",
        ".pkl", ".pt", ".pth", ".bin", ".h5", ".hdf5",
        ".npy", ".npz", ".onnx", ".pb",
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico",
        ".mp3", ".mp4", ".wav", ".avi",
        ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z",
        ".exe", ".dll", ".whl",
        ".db", ".sqlite", ".sqlite3",
    }

    def __init__(self, path: str) -> None:
        self.files: dict[str, Blob | Tree] = {}
        self._explore_project(path)

    def _explore_project(self, path: str) -> None:
        """Recursively walk the directory at *path*, populating self.files."""
        for obj in os.listdir(path):
            if obj.startswith(".") and obj in self.IGNORE_DIRS:
                continue
            if obj in self.IGNORE_DIRS:
                continue
            full_path = os.path.join(path, obj)
            if os.path.isdir(full_path):
                self.files[obj] = Tree(full_path)
            elif os.path.isfile(full_path):
                _, ext = os.path.splitext(obj)
                if ext.lower() in self.IGNORE_EXTENSIONS:
                    continue
                try:
                    with open(full_path, "r") as f:
                        self.files[obj] = Blob(f.read())
                except (UnicodeDecodeError, PermissionError):
                    pass

    def get_file(self, path: str) -> Blob | None:
        """Lookup a file by slash-separated relative path within this tree."""
        obj_path = path.split("/")
        for obj in obj_path:
            if obj in self.files:
                if isinstance(self.files[obj], Blob):
                    return self.files[obj]
                else:
                    return self.files[obj].get_file("/".join(obj_path[1:]))
        return None

    def get_hash(self) -> str:
        """Compute the SHA-256 hash of this tree's sorted entry list."""
        entries: list[str] = []
        for name in sorted(self.files.keys()):
            obj = self.files[name]
            if isinstance(obj, Blob):
                entries.append(f"blob {obj.get_hash()} {name}")
            else:
                entries.append(f"tree {obj.get_hash()} {name}")
        return sha256("\n".join(entries).encode()).hexdigest()

    def __str__(self) -> str:
        return str(self.files)

    def __repr__(self) -> str:
        return f"Tree(hash={self.get_hash()})"

    def __hash__(self) -> int:
        return hash(self.get_hash())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tree):
            return NotImplemented
        return self.get_hash() == other.get_hash()
