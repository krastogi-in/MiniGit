"""CLI smoke tests for reset (BLRID-29)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

from frontend.operations import Operations


def _cli_env() -> dict[str, str]:
    src = os.path.join(os.path.dirname(__file__), "..", "src")
    return {**os.environ, "PYTHONPATH": src}


def _cli_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "src", "cli.py")


def _run_cli(tmp: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, _cli_path(), *args],
        cwd=tmp,
        capture_output=True,
        text=True,
        env=_cli_env(),
        check=False,
    )


def test_cli_reset_dry_run() -> None:
    """CLI reset --dry-run prints preview and leaves tip unchanged."""
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "README.md"), "w") as f:
            f.write("# a\n")
        assert _run_cli(tmp, "init", "--author", "T", "-m", "init").returncode == 0
        with open(os.path.join(tmp, "README.md"), "w") as f:
            f.write("# b\n")
        ops = Operations(tmp, os.path.join(tmp, ".minigit", "minigit.db"))
        ops.branch = "main"
        ops.add("README.md")
        tip1 = ops.create_new_commit("two", author="T")
        tip0 = ops.get_commit_history()[1]["hash"]
        result = _run_cli(tmp, "reset", "--dry-run", tip0)
        assert result.returncode == 0
        assert "Dry run only" in result.stdout
        assert "ancestor" in result.stdout
        assert ops.db.get_ref("main") == tip1
    finally:
        shutil.rmtree(tmp)


def test_cli_reset_yes_applies() -> None:
    """CLI reset --yes moves the tip."""
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "README.md"), "w") as f:
            f.write("# a\n")
        assert _run_cli(tmp, "init", "--author", "T", "-m", "init").returncode == 0
        with open(os.path.join(tmp, "README.md"), "w") as f:
            f.write("# b\n")
        ops = Operations(tmp, os.path.join(tmp, ".minigit", "minigit.db"))
        ops.branch = "main"
        ops.add("README.md")
        ops.create_new_commit("two", author="T")
        tip0 = ops.get_commit_history()[1]["hash"]
        result = _run_cli(tmp, "reset", "--yes", "--mixed", tip0)
        assert result.returncode == 0
        assert "Reset applied" in result.stdout
        assert ops.db.get_ref("main") == tip0
    finally:
        shutil.rmtree(tmp)


def test_cli_rejects_dry_run_and_yes() -> None:
    """CLI errors when both --dry-run and --yes are passed."""
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "README.md"), "w") as f:
            f.write("# a\n")
        assert _run_cli(tmp, "init", "--author", "T", "-m", "init").returncode == 0
        tip = Operations(tmp, os.path.join(tmp, ".minigit", "minigit.db")).db.get_ref(
            "main"
        )
        assert tip is not None
        result = _run_cli(tmp, "reset", "--dry-run", "--yes", tip)
        assert result.returncode == 1
        assert "either --dry-run or --yes" in result.stdout
    finally:
        shutil.rmtree(tmp)
