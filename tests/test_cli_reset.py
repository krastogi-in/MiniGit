"""CLI smoke tests for reset (BLRID-29)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile


def test_cli_reset_dry_run() -> None:
    """CLI reset --dry-run prints preview and leaves tip unchanged."""
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "README.md"), "w") as f:
            f.write("# a\n")
        cli = os.path.join(os.path.dirname(__file__), "..", "src", "cli.py")
        env = {**os.environ, "PYTHONPATH": os.path.join(os.path.dirname(__file__), "..", "src")}
        subprocess.run(
            [sys.executable, cli, "init", "--author", "T", "-m", "init"],
            cwd=tmp,
            check=True,
            capture_output=True,
            env=env,
        )
        with open(os.path.join(tmp, "README.md"), "w") as f:
            f.write("# b\n")
        # Stage+commit via Operations for simplicity
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from frontend.operations import Operations

        ops = Operations(tmp, os.path.join(tmp, ".minigit", "minigit.db"))
        ops.branch = "main"
        ops.add("README.md")
        tip1 = ops.create_new_commit("two", author="T")
        tip0 = ops.get_commit_history()[1]["hash"]
        result = subprocess.run(
            [sys.executable, cli, "reset", "--dry-run", tip0],
            cwd=tmp,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert result.returncode == 0
        assert "Dry run only" in result.stdout
        assert ops.db.get_ref("main") == tip1
    finally:
        shutil.rmtree(tmp)
