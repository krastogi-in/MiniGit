"""Stash push / list / pop helpers for MiniGit Operations."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from frontend.operations import Operations


def stash_push(ops: Operations, message: str | None = None) -> dict[str, Any]:
    """Save staging (+ WD for staged paths), clear staging, reset paths to HEAD."""
    staged = ops.db.get_staged()
    if not staged:
        raise ValueError("Nothing staged to stash")

    head_files = _head_files(ops)
    payload: list[dict[str, Any]] = []
    for entry in staged:
        path = entry["path"]
        item: dict[str, Any] = {
            "path": path,
            "action": entry["action"],
            "blob_hash": entry.get("blob_hash"),
        }
        full = os.path.join(ops.repo_path, path)
        if os.path.isfile(full):
            with open(full, encoding="utf-8") as f:
                item["wd_content"] = f.read()
        else:
            item["wd_content"] = None
        payload.append(item)

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    msg = message or "WIP on stash"
    stash_id = ops.db.push_stash(created_at, msg, json.dumps(payload))
    ops.db.clear_staging()
    _reset_paths_to_head(ops, payload, head_files)
    return {"id": stash_id, "message": msg, "created_at": created_at}


def stash_list(ops: Operations) -> list[dict[str, Any]]:
    """Return stash stack newest-first without payload bodies."""
    rows = ops.db.list_stashes()
    result: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        result.append({
            "index": idx,
            "id": row["id"],
            "message": row["message"],
            "created_at": row["created_at"],
        })
    return result


def stash_pop(ops: Operations) -> dict[str, Any]:
    """Apply the top stash then drop it. Aborts on WD conflict."""
    top = ops.db.get_top_stash()
    if not top:
        raise ValueError("No stash entries")

    payload: list[dict[str, Any]] = json.loads(top["payload_json"])
    head_files = _head_files(ops)
    conflicts = _find_conflicts(ops, payload, head_files)
    if conflicts:
        raise ValueError(
            "Stash pop aborted due to conflicts: " + ", ".join(conflicts)
        )

    for entry in payload:
        _apply_entry(ops, entry)
    ops.db.delete_stash(int(top["id"]))
    return {
        "id": top["id"],
        "message": top["message"],
        "created_at": top["created_at"],
    }


def _head_files(ops: Operations) -> dict[str, str]:
    """Flatten the current branch HEAD tree to {path: blob_hash}."""
    commit_hash = ops.db.get_ref(ops.branch)
    if not commit_hash:
        return {}
    commit = ops.db.get_commit(commit_hash)
    if not commit:
        return {}
    result: dict[str, str] = ops._flatten_tree(commit["tree_hash"])
    return result


def _reset_paths_to_head(
    ops: Operations,
    payload: list[dict[str, Any]],
    head_files: dict[str, str],
) -> None:
    """Restore working-dir paths toward HEAD after a successful stash push."""
    for entry in payload:
        path = entry["path"]
        full = os.path.join(ops.repo_path, path)
        if path in head_files:
            content = ops.db.get_blob(head_files[path]) or ""
            parent = os.path.dirname(full)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
        elif os.path.isfile(full):
            os.remove(full)


def _find_conflicts(
    ops: Operations,
    payload: list[dict[str, Any]],
    head_files: dict[str, str],
) -> list[str]:
    """Paths whose WD differs from both HEAD and the stash payload."""
    conflicts: list[str] = []
    for entry in payload:
        path = entry["path"]
        expected = _expected_wd(ops, entry)
        full = os.path.join(ops.repo_path, path)
        if not os.path.isfile(full):
            continue
        with open(full, encoding="utf-8") as f:
            current = f.read()
        if expected is not None and current == expected:
            continue
        head_content = None
        if path in head_files:
            head_content = ops.db.get_blob(head_files[path])
        if head_content is not None and current == head_content:
            continue
        conflicts.append(path)
    return conflicts


def _expected_wd(ops: Operations, entry: dict[str, Any]) -> str | None:
    """Content we would write to WD when applying a stash entry."""
    if entry.get("wd_content") is not None:
        content = entry["wd_content"]
        return str(content) if content is not None else None
    blob_hash = entry.get("blob_hash")
    if entry.get("action") == "add" and blob_hash:
        data = ops.db.get_blob(str(blob_hash))
        return data
    return None


def _apply_entry(ops: Operations, entry: dict[str, Any]) -> None:
    """Restore one stash entry into staging and working directory."""
    path = entry["path"]
    action = entry["action"]
    full = os.path.join(ops.repo_path, path)
    if action == "add":
        content = _expected_wd(ops, entry)
        if content is None:
            content = ""
        parent = os.path.dirname(full)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        blob_hash = entry.get("blob_hash")
        if not blob_hash:
            from components.blob import Blob

            blob = Blob(content)
            blob_hash = blob.get_hash()
            ops.db.store_blob(blob_hash, content)
        ops.db.stage_file(path, "add", blob_hash)
    elif action == "delete":
        if os.path.isfile(full):
            os.remove(full)
        ops.db.stage_file(path, "delete")
