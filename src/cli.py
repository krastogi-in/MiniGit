#!/usr/bin/env python3
"""MiniGit CLI — a simplified git-like command-line interface.

Usage:
    minigit init                        Initialize a new repository
    minigit log                         Show commit history
    minigit branch                      List branches
    minigit branch <name>               Create a new branch
    minigit checkout <branch>           Switch to a branch
    minigit show <hash>                 Show commit details
    minigit diff <hash1> <hash2>        Diff two commits
    minigit ls [tree_hash]              List files at a tree
    minigit cat <blob_hash>             Show file content
    minigit reset [options] <hash>      Safe reset with loss preview
    minigit serve                       Start the web UI
"""

from __future__ import annotations

import argparse
import difflib
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(__file__))

from frontend.operations import Operations


def find_repo(start_path: str | None = None) -> str | None:
    """Walk up from start_path to find the nearest .minigit directory."""
    path = os.path.abspath(start_path or os.getcwd())
    while True:
        if os.path.isdir(os.path.join(path, ".minigit")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent


def get_ops(args: argparse.Namespace) -> Operations:
    """Resolve the repository path and return an Operations instance."""
    repo_path = find_repo()
    if not repo_path and args.command != "init":
        print("Error: not a MiniGit repository (no .minigit found)")
        sys.exit(1)
    if args.command == "init":
        repo_path = os.getcwd()
    db_path = os.path.join(repo_path, ".minigit", "minigit.db")  # type: ignore[arg-type]
    return Operations(repo_path, db_path)  # type: ignore[arg-type]


def cmd_init(args: argparse.Namespace) -> None:
    """Handle the 'init' subcommand."""
    ops = get_ops(args)
    commit_hash = ops.init_repo(
        author=args.author,
        message=args.message or "Initial commit",
    )
    print(f"Initialized MiniGit repository in {ops.repo_path}")
    print(f"Initial commit: {commit_hash[:8]}")


def cmd_log(args: argparse.Namespace) -> None:
    """Handle the 'log' subcommand — display commit history."""
    ops = get_ops(args)
    history = ops.get_commit_history(args.branch)
    if not history:
        print("No commits yet.")
        return
    for commit in history:
        print(f"\033[33mcommit {commit['hash']}\033[0m")
        if commit["parent_hash"]:
            print(f"parent {commit['parent_hash'][:8]}")
        print(f"Author: {commit['author']}")
        print(f"Date:   {commit['timestamp']}")
        print(f"\n    {commit['message']}\n")


def cmd_branch(args: argparse.Namespace) -> None:
    """Handle the 'branch' subcommand — list or create branches."""
    ops = get_ops(args)
    if args.name:
        try:
            ops.create_branch(args.name)
            print(f"Branch '{args.name}' created")
        except ValueError as e:
            print(f"Error: {e}")
    else:
        branches = ops.get_all_branches()
        for b in branches:
            prefix = "* " if b["name"] == ops.branch else "  "
            print(f"{prefix}{b['name']}  ({b['commit_hash'][:8]})")


def cmd_checkout(args: argparse.Namespace) -> None:
    """Handle the 'checkout' subcommand — switch branches."""
    ops = get_ops(args)
    try:
        ops.checkout_branch(args.branch_name)
        print(f"Switched to branch '{args.branch_name}'")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_show(args: argparse.Namespace) -> None:
    """Handle the 'show' subcommand — display commit details."""
    ops = get_ops(args)
    commit = ops.get_commit(args.hash)
    if not commit:
        print(f"Error: commit {args.hash} not found")
        return
    print(f"\033[33mcommit {commit['hash']}\033[0m")
    print(f"tree   {commit['tree_hash'][:8]}")
    if commit["parent_hash"]:
        print(f"parent {commit['parent_hash'][:8]}")
    print(f"Author: {commit['author']}")
    print(f"Date:   {commit['timestamp']}")
    print(f"\n    {commit['message']}\n")


def cmd_diff(args: argparse.Namespace) -> None:
    """Handle the 'diff' subcommand — show differences between two commits."""
    ops = get_ops(args)
    diffs = ops.get_diffs(args.hash1, args.hash2)
    if not diffs:
        print("No differences.")
        return
    for d in diffs:
        print(f"\n\033[1m{d['status']}: {d['path']}\033[0m")
        diff_lines = difflib.unified_diff(
            d["old_content"].splitlines(keepends=True),
            d["new_content"].splitlines(keepends=True),
            fromfile=f"a/{d['path']}",
            tofile=f"b/{d['path']}",
            lineterm="",
        )
        for line in diff_lines:
            if line.startswith("+") and not line.startswith("+++"):
                print(f"\033[32m{line}\033[0m")
            elif line.startswith("-") and not line.startswith("---"):
                print(f"\033[31m{line}\033[0m")
            else:
                print(line)


def cmd_ls(args: argparse.Namespace) -> None:
    """Handle the 'ls' subcommand — list files in a tree."""
    ops = get_ops(args)
    if args.tree_hash:
        tree_hash = args.tree_hash
    else:
        history = ops.get_commit_history()
        if not history:
            print("No commits yet.")
            return
        tree_hash = history[0]["tree_hash"]

    entries = ops.browse_tree(tree_hash)
    for entry in sorted(entries, key=lambda e: e["name"]):
        kind = "tree" if entry["type"] == "tree" else "blob"
        print(f"{kind}  {entry['hash'][:8]}  {entry['name']}")


def cmd_cat(args: argparse.Namespace) -> None:
    """Handle the 'cat' subcommand — display blob content."""
    ops = get_ops(args)
    content = ops.get_blob_content(args.blob_hash)
    if content is None:
        print(f"Error: blob {args.blob_hash} not found")
        return
    print(content)


def _print_reset_preview(preview: dict[str, Any]) -> None:
    """Print a short loss preview for reset."""
    print(f"Reset preview ({preview['mode']}) on branch '{preview['branch']}'")
    print(f"  current tip: {preview['current_tip'][:8]}")
    print(f"  target:      {preview['target'][:8]}")
    print("  note: target must be an ancestor of the current tip")
    dropped = preview["commits_to_drop"]
    if dropped:
        print(f"  commits that leave the tip path ({len(dropped)}):")
        for c in dropped:
            print(f"    - {c['hash'][:8]}  {c['message']}")
    else:
        print("  commits that leave the tip path: (none)")
    if preview["mode"] == "hard":
        impact = preview["hard_impact"]
        print(
            "  hard path impact: "
            f"overwrite={len(impact['overwritten'])} "
            f"delete={len(impact['deleted'])} "
            f"create={len(impact['created'])}"
        )
        _print_path_sample("    overwrite", impact["overwritten"])
        _print_path_sample("    delete", impact["deleted"])
        _print_path_sample("    create", impact["created"])
    dirty = preview["dirty_tracked"]
    if dirty:
        print(f"  dirty tracked files: {len(dirty)}")
        _print_path_sample("    dirty", dirty)
    if preview["staging_count"]:
        print(f"  staged entries: {preview['staging_count']}")
        if preview["mode"] == "soft":
            print("  note: soft keeps MiniGit staging rows (not a full Git index)")


def _print_path_sample(label: str, paths: list[str], limit: int = 10) -> None:
    """Print up to *limit* paths under a label."""
    if not paths:
        return
    shown = paths[:limit]
    for path in shown:
        print(f"{label}: {path}")
    remaining = len(paths) - len(shown)
    if remaining > 0:
        print(f"{label}: … and {remaining} more")


def cmd_reset(args: argparse.Namespace) -> None:
    """Handle safe reset with dry-run preview."""
    if args.dry_run and args.yes:
        print("Error: use either --dry-run or --yes, not both")
        sys.exit(1)
    ops = get_ops(args)
    mode = "mixed"
    if args.soft:
        mode = "soft"
    elif args.hard:
        mode = "hard"
    try:
        preview = ops.reset(
            args.hash,
            mode=mode,
            dry_run=args.dry_run,
            confirm=args.yes,
            force=args.force,
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    _print_reset_preview(preview)
    if args.dry_run:
        print("Dry run only — tip unchanged. Re-run with --yes to apply.")
    elif preview.get("applied"):
        print(f"Reset applied ({mode}) → {preview['target'][:8]}")


def cmd_serve(args: argparse.Namespace) -> None:
    """Handle the 'serve' subcommand — start the Flask web UI."""
    from app import app

    print(f"Starting MiniGit web UI on http://localhost:{args.port}")
    app.run(debug=True, port=args.port)


def main() -> None:
    """Parse arguments and dispatch to the appropriate command handler."""
    parser = argparse.ArgumentParser(
        prog="minigit",
        description="MiniGit -- a simplified version control system",
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_init = sub.add_parser("init", help="Initialize a new repository")
    p_init.add_argument("--author", default=None)
    p_init.add_argument("-m", "--message", default=None)

    p_log = sub.add_parser("log", help="Show commit history")
    p_log.add_argument("--branch", default=None)

    p_branch = sub.add_parser("branch", help="List or create branches")
    p_branch.add_argument("name", nargs="?", default=None)

    p_checkout = sub.add_parser("checkout", help="Switch branch")
    p_checkout.add_argument("branch_name")

    p_show = sub.add_parser("show", help="Show commit details")
    p_show.add_argument("hash")

    p_diff = sub.add_parser("diff", help="Diff two commits")
    p_diff.add_argument("hash1")
    p_diff.add_argument("hash2")

    p_ls = sub.add_parser("ls", help="List files in a tree")
    p_ls.add_argument("tree_hash", nargs="?", default=None)

    p_cat = sub.add_parser("cat", help="Show blob content")
    p_cat.add_argument("blob_hash")

    p_reset = sub.add_parser(
        "reset",
        help="Safe reset with loss preview (target must be an ancestor)",
    )
    p_reset.add_argument(
        "hash",
        help="Target ancestor commit hash (64-char hex)",
    )
    mode = p_reset.add_mutually_exclusive_group()
    mode.add_argument("--soft", action="store_true", help="Move tip; keep staging rows")
    mode.add_argument(
        "--mixed",
        action="store_true",
        help="Move tip and clear staging (default)",
    )
    mode.add_argument(
        "--hard",
        action="store_true",
        help="Move tip, clear staging, sync working tree",
    )
    p_reset.add_argument(
        "--dry-run",
        action="store_true",
        help="Show preview only; do not change tip (not with --yes)",
    )
    p_reset.add_argument(
        "--yes",
        action="store_true",
        help="Apply reset after printing preview (not with --dry-run)",
    )
    p_reset.add_argument(
        "--force",
        action="store_true",
        help="Allow hard reset with dirty tracked files",
    )

    p_serve = sub.add_parser("serve", help="Start web UI")
    p_serve.add_argument("--port", type=int, default=5000)

    args = parser.parse_args()
    commands: dict[str, Any] = {
        "init": cmd_init,
        "log": cmd_log,
        "branch": cmd_branch,
        "checkout": cmd_checkout,
        "show": cmd_show,
        "diff": cmd_diff,
        "ls": cmd_ls,
        "cat": cmd_cat,
        "reset": cmd_reset,
        "serve": cmd_serve,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
