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
    minigit tag                         List tags
    minigit tag <name>                  Tag current HEAD
    minigit tag <name> <commit-hash>    Tag a specific commit
    minigit tag -d <name>               Delete a tag
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
    commit_hash = ops.resolve_ref(args.hash)
    if not commit_hash:
        print(f"Error: ref {args.hash} not found")
        return
    commit = ops.get_commit(commit_hash)
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


def cmd_tag(args: argparse.Namespace) -> None:
    """Handle the 'tag' subcommand — create, list, or delete lightweight tags."""
    ops = get_ops(args)
    if args.delete:
        if not args.name:
            print("Error: tag name required for delete")
            sys.exit(1)
        try:
            ops.delete_tag(args.name)
            print(f"Deleted tag '{args.name}'")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        return

    if args.name is None:
        tags = ops.list_tags()
        if not tags:
            print("No tags.")
            return
        for tag in tags:
            print(f"{tag['name']}  ({tag['commit_hash'][:8]})")
        return

    try:
        commit_hash = ops.create_tag(args.name, args.commit_hash)
        print(f"Tagged '{args.name}' at {commit_hash[:8]}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


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

    p_tag = sub.add_parser("tag", help="List, create, or delete tags")
    p_tag.add_argument("name", nargs="?", default=None, help="Tag name to create or delete")
    p_tag.add_argument("commit_hash", nargs="?", default=None, help="Commit to tag")
    p_tag.add_argument("-d", "--delete", action="store_true", help="Delete a tag")

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
        "tag": cmd_tag,
        "serve": cmd_serve,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
