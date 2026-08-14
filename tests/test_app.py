"""Tests for Flask merge route wiring."""

from __future__ import annotations

import app as minigit_app


class _FakeOps:
    def __init__(self) -> None:
        self.checked_out: list[str] = []
        self.merged: list[str] = []

    def checkout_branch(self, branch_name: str) -> str:
        self.checked_out.append(branch_name)
        return branch_name

    def merge(self, source_branch: str) -> dict[str, str]:
        self.merged.append(source_branch)
        return {"status": "fast-forward", "commit_hash": "c" * 64}


def test_merge_route_calls_operations(monkeypatch) -> None:
    """Merge route checks out target branch and merges source branch."""
    fake_ops = _FakeOps()
    monkeypatch.setattr(minigit_app, "get_ops", lambda repo_name: fake_ops)

    minigit_app.app.config["TESTING"] = True
    client = minigit_app.app.test_client()
    resp = client.post(
        "/repo/sample/merge",
        data={"source_branch": "feature", "target_branch": "main"},
        follow_redirects=False,
    )

    assert resp.status_code == 302
    assert fake_ops.checked_out == ["main"]
    assert fake_ops.merged == ["feature"]
