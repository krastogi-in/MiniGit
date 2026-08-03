from components.blob import Blob
import os
from hashlib import sha256


class Tree:
    def __init__(self, path):
        self.files = {}
        self._explore_project(path)

    IGNORE_DIRS = {
        ".minigit", ".git", "__pycache__", ".pytest_cache",
        "node_modules", ".venv", "venv", ".tox", ".mypy_cache",
        ".eggs", "*.egg-info", "dist", "build",
    }
    IGNORE_EXTENSIONS = {
        ".pyc", ".pyo", ".so", ".o", ".a", ".dylib",
        ".pkl", ".pt", ".pth", ".bin", ".h5", ".hdf5",
        ".npy", ".npz", ".onnx", ".pb",
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico",
        ".mp3", ".mp4", ".wav", ".avi",
        ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z",
        ".exe", ".dll", ".whl",
        ".db", ".sqlite", ".sqlite3",
    }

    def _explore_project(self, path):
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
                    with open(full_path, 'r') as f:
                        self.files[obj] = Blob(f.read())
                except (UnicodeDecodeError, PermissionError):
                    pass

    def get_file(self, path):
        obj_path = path.split('/')
        for obj in obj_path:
            if obj in self.files:
                if isinstance(self.files[obj], Blob):
                    return self.files[obj]
                else:
                    return self.files[obj].get_file("/".join(obj_path[1:]))
        return None

    def __str__(self):
        return str(self.files)

    def __repr__(self):
        return f"Tree(path={self.path}, hash={self.get_hash()})"

    def get_hash(self):
        entries = []
        for name in sorted(self.files.keys()):
            obj = self.files[name]
            if isinstance(obj, Blob):
                entries.append(f"blob {obj.get_hash()} {name}")
            else:
                entries.append(f"tree {obj.get_hash()} {name}")
        return sha256("\n".join(entries).encode()).hexdigest()

    def __hash__(self):
        return hash(self.get_hash())

    def __eq__(self, other):
        return self.get_hash() == other.get_hash()