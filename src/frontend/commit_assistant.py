"""AI-powered commit message generator using heuristic analysis of staged diffs."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import structlog

from frontend.operations import Operations

logger = structlog.get_logger(__name__)

_MAX_MESSAGE_LEN = 72

_TEST_PATTERNS: set[str] = {"tests/", "test_", "_test.py", "test/"}
_DOC_EXTENSIONS: set[str] = {".md", ".rst", ".txt", ".adoc"}
_DOC_DIRS: set[str] = {"docs/", "doc/"}
_CONFIG_EXTENSIONS: set[str] = {
    ".toml", ".cfg", ".ini", ".yml", ".yaml", ".json",
    ".env", ".conf",
}
_CONFIG_FILES: set[str] = {
    "Makefile", "Dockerfile", "docker-compose.yml",
    ".gitignore", ".flake8", "pyproject.toml", "setup.cfg",
    "setup.py", "requirements.txt", "tox.ini",
}
_STYLE_EXTENSIONS: set[str] = {".css", ".scss", ".less", ".sass"}

_ACTION_WORDS: dict[str, str] = {
    "added": "add",
    "modified": "update",
    "deleted": "remove",
}


@dataclass
class GenerationResult:
    """Result of commit message generation."""

    message: str
    commit_type: str
    summary: str
    file_count: int
    change_types: dict[str, int] = field(default_factory=dict)


class CommitMessageGenerator:
    """Generates conventional-commit messages from staged diffs."""

    def __init__(self, ops: Operations) -> None:
        self._ops = ops

    def generate(self) -> GenerationResult:
        """Analyze staged diffs and produce a commit message suggestion."""
        diffs = self._ops.get_staged_diffs()

        change_types: dict[str, int] = {}
        for d in diffs:
            action = d["action"]
            change_types[action] = change_types.get(action, 0) + 1

        commit_type = self._classify_type(diffs)
        summary = self._build_summary(diffs, change_types)
        message = f"{commit_type}: {summary}"

        if len(message) > _MAX_MESSAGE_LEN:
            available = _MAX_MESSAGE_LEN - len(commit_type) - 2
            message = f"{commit_type}: {summary[:available]}"

        return GenerationResult(
            message=message,
            commit_type=commit_type,
            summary=summary,
            file_count=len(diffs),
            change_types=change_types,
        )

    def _classify_type(self, diffs: list[dict[str, str]]) -> str:
        """Pick the conventional commit type based on file paths and actions."""
        votes: dict[str, int] = {}

        for d in diffs:
            path = d["path"]
            action = d["action"]
            file_type = self._classify_file(path)

            if file_type:
                votes[file_type] = votes.get(file_type, 0) + 1
            elif action == "deleted":
                votes["chore"] = votes.get("chore", 0) + 1
            elif action == "added":
                votes["feat"] = votes.get("feat", 0) + 1
            elif action == "modified":
                if self._is_whitespace_only(d["old_content"], d["new_content"]):
                    votes["style"] = votes.get("style", 0) + 1
                else:
                    votes["feat"] = votes.get("feat", 0) + 1

        if not votes:
            return "chore"

        return max(votes, key=lambda k: votes[k])

    def _classify_file(self, path: str) -> str | None:
        """Classify a file path to a commit type, or None for generic."""
        basename = os.path.basename(path)
        _, ext = os.path.splitext(basename)
        ext_lower = ext.lower()

        if any(pattern in path for pattern in _TEST_PATTERNS):
            return "test"

        if ext_lower in _DOC_EXTENSIONS or any(d in path for d in _DOC_DIRS):
            return "docs"

        if ext_lower in _CONFIG_EXTENSIONS or basename in _CONFIG_FILES:
            return "chore"

        if ext_lower in _STYLE_EXTENSIONS:
            return "style"

        return None

    @staticmethod
    def _is_whitespace_only(old: str, new: str) -> bool:
        """Check if the diff is whitespace-only."""
        return old.split() == new.split()

    def _build_summary(
        self,
        diffs: list[dict[str, str]],
        change_types: dict[str, int],
    ) -> str:
        """Build a concise summary line from the diffs."""
        if len(diffs) == 1:
            d = diffs[0]
            action_word = _ACTION_WORDS.get(d["action"], "update")
            basename = os.path.basename(d["path"])
            return f"{action_word} {basename}"

        dominant_action = max(change_types, key=lambda k: change_types[k])
        action_word = _ACTION_WORDS.get(dominant_action, "update")

        dirs = {os.path.dirname(d["path"]) or "root" for d in diffs}
        if len(dirs) == 1:
            dirname = dirs.pop()
            if dirname == "root":
                return f"{action_word} {len(diffs)} files"
            return f"{action_word} {len(diffs)} files in {dirname}"

        first_file = os.path.basename(diffs[0]["path"])
        others = len(diffs) - 1
        return f"{action_word} {first_file} and {others} other{'s' if others > 1 else ''}"
