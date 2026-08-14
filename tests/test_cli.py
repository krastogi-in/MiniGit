"""CLI tests for branch-aware commands."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from cli import main
from frontend.operations import Operations

if TYPE_CHECKING:
    from pathlib import Path


def _run_cli(monkeypatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["minigit", *args])
    main()


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _init_repo(monkeypatch, capsys, tmp_path: Path) -> Operations:
    _write_file(tmp_path / "README.md", "# Test Project\n")
    _write_file(tmp_path / "src" / "main.py", "print('hello')\n")
    monkeypatch.chdir(tmp_path)
    _run_cli(monkeypatch, "init", "--author", "Tester", "-m", "Initial commit")
    capsys.readouterr()
    return Operations(str(tmp_path))


def test_rebase_command_replays_the_current_branch(monkeypatch, capsys, tmp_path) -> None:
    """The CLI rebase command should use the persisted current branch."""
    ops = _init_repo(monkeypatch, capsys, tmp_path)
    ops.create_branch("feature")
    _write_file(tmp_path / "README.md", "# Main branch\n")
    ops.add("README.md")
    ops.create_new_commit("main change", author="Tester")

    ops.checkout_branch("feature")
    feature_ops = Operations(str(tmp_path))
    _write_file(tmp_path / "src" / "main.py", "print('feature branch')\n")
    feature_ops.add("src/main.py")
    feature_ops.create_new_commit("feature change", author="Tester")

    _run_cli(monkeypatch, "rebase", "main")
    output = capsys.readouterr().out

    assert "Rebased 'feature' onto 'main' with 1 replayed commit(s)" in output

    reopened = Operations(str(tmp_path))
    history = reopened.get_commit_history()
    flat = reopened._flatten_tree(history[0]["tree_hash"])
    assert reopened.branch == "feature"
    assert history[0]["message"] == "feature change"
    assert history[1]["message"] == "main change"
    assert reopened.get_blob_content(flat["README.md"]) == "# Main branch\n"
    assert reopened.get_blob_content(flat["src/main.py"]) == "print('feature branch')\n"


def test_branch_checkout_log_and_rebase_status_commands(monkeypatch, capsys, tmp_path) -> None:
    """Branch-related CLI commands should print the expected repository state."""
    _init_repo(monkeypatch, capsys, tmp_path)

    _run_cli(monkeypatch, "branch", "feature")
    output = capsys.readouterr().out
    assert "Branch 'feature' created" in output

    _run_cli(monkeypatch, "checkout", "feature")
    output = capsys.readouterr().out
    assert "Switched to branch 'feature'" in output

    reopened = Operations(str(tmp_path))
    assert reopened.branch == "feature"

    _run_cli(monkeypatch, "branch")
    output = capsys.readouterr().out
    assert "* feature" in output
    assert "main" in output

    _run_cli(monkeypatch, "log")
    output = capsys.readouterr().out
    assert "commit" in output
    assert "Initial commit" in output

    _run_cli(monkeypatch, "rebase", "main")
    output = capsys.readouterr().out
    assert "Branch 'feature' is already up to date with 'main'" in output

    _run_cli(monkeypatch, "rebase", "feature")
    output = capsys.readouterr().out
    assert "Error: Cannot rebase a branch onto itself" in output


def test_show_ls_cat_and_diff_commands(monkeypatch, capsys, tmp_path) -> None:
    """Object inspection CLI commands should expose commit and tree content."""
    ops = _init_repo(monkeypatch, capsys, tmp_path)
    _write_file(tmp_path / "README.md", "# Updated Project\n")
    _write_file(tmp_path / "notes.txt", "hello from notes\n")
    ops.add("README.md")
    ops.add("notes.txt")
    second_hash = ops.create_new_commit("update readme", author="Tester")
    history = ops.get_commit_history()
    first_hash = history[1]["hash"]
    flat = ops._flatten_tree(history[0]["tree_hash"])

    _run_cli(monkeypatch, "show", second_hash)
    output = capsys.readouterr().out
    assert second_hash in output
    assert "update readme" in output

    _run_cli(monkeypatch, "ls")
    output = capsys.readouterr().out
    assert "README.md" in output
    assert "notes.txt" in output

    _run_cli(monkeypatch, "cat", flat["README.md"])
    output = capsys.readouterr().out
    assert output.strip().endswith("# Updated Project")

    _run_cli(monkeypatch, "diff", first_hash, second_hash)
    output = capsys.readouterr().out
    assert "modified: README.md" in output
    assert "added: notes.txt" in output
    assert "+# Updated Project" in output
