"""Tests for MiniGit CLI merge command."""

from __future__ import annotations

import sys

import cli


class _FakeOps:
    def __init__(self, result: dict[str, str] | None = None, error: str | None = None) -> None:
        self.result = result or {"status": "already-up-to-date", "commit_hash": "a" * 64}
        self.error = error

    def merge(self, source_branch: str) -> dict[str, str]:
        if self.error:
            raise ValueError(self.error)
        return self.result


def test_cli_merge_fast_forward_output(monkeypatch, capsys) -> None:
    """CLI merge prints fast-forward status."""
    fake_ops = _FakeOps(result={"status": "fast-forward", "commit_hash": "b" * 64})
    monkeypatch.setattr(cli, "get_ops", lambda args: fake_ops)
    monkeypatch.setattr(sys, "argv", ["minigit", "merge", "feature"])

    cli.main()
    output = capsys.readouterr().out
    assert "Fast-forwarded" in output


def test_cli_merge_error_output(monkeypatch, capsys) -> None:
    """CLI merge prints merge errors without crashing."""
    fake_ops = _FakeOps(error="Source ref 'missing' does not exist")
    monkeypatch.setattr(cli, "get_ops", lambda args: fake_ops)
    monkeypatch.setattr(sys, "argv", ["minigit", "merge", "missing"])

    cli.main()
    output = capsys.readouterr().out
    assert "Error: Source ref 'missing' does not exist" in output
