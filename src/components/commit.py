from components.tree import Tree
from datetime import datetime
import os
from hashlib import sha256


class Commit:
    def __init__(self, path, parent_commit_pointer=None,
                 author=None, message=None, timestamp=None):
        self.Tree_pointer = Tree(path)
        self.parent_commit_pointer = parent_commit_pointer
        if author is None:
            self.author = os.getenv("USER")
        else:
            self.author = author
        if message is None:
            self.message = "No message"
        else:
            self.message = message
        if timestamp is None:
            self.timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
        else:
            self.timestamp = timestamp

    def get_hash(self):
        if self.parent_commit_pointer is None:
            parent_hash = ""
        elif isinstance(self.parent_commit_pointer, str):
            parent_hash = self.parent_commit_pointer
        else:
            parent_hash = self.parent_commit_pointer.get_hash()
        content = (f"{self.Tree_pointer.get_hash()}"
                   f"{parent_hash}"
                   f"{self.author}"
                   f"{self.message}"
                   f"{self.timestamp}")
        return sha256(content.encode()).hexdigest()

    def get_parent_hash(self):
        if self.parent_commit_pointer is None:
            return None
        if isinstance(self.parent_commit_pointer, str):
            return self.parent_commit_pointer
        return self.parent_commit_pointer.get_hash()