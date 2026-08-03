# MiniGit

A simplified Git clone built from scratch in Python. Implements content-addressable storage, tree structures, commit history, branching, and diffs.

## Architecture

```
MiniGit/
├── src/
│   ├── components/         # Core git objects
│   │   ├── blob.py         # File content storage (SHA-256 hashed)
│   │   ├── tree.py         # Directory structure (recursive, hashed)
│   │   └── commit.py       # Commit snapshots (tree + parent + metadata)
│   ├── backend/
│   │   └── sqlite_client.py  # SQLite storage layer
│   ├── frontend/
│   │   └── operations.py   # Git operations (init, branch, diff, etc.)
│   ├── app.py              # Flask web UI
│   ├── cli.py              # Command-line interface
│   └── templates/          # HTML templates for web UI
├── tests/                  # Test suite
├── repos/                  # Repositories created via web UI
└── requirements.txt
```

## How It Works

MiniGit mirrors real Git's object model:

- **Blobs** store raw file content, identified by SHA-256 hash
- **Trees** store directory listings (name + type + hash), also hashed
- **Commits** point to a root tree + parent commit + metadata, also hashed
- **Refs** (branches) are name-to-commit-hash mappings

Every commit is a full snapshot. Unchanged files share the same blob across commits. Diffs are computed on-the-fly by comparing two commit trees.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### CLI

```bash
cd your-project/

# Initialize a repository
python src/cli.py init

# View commit history
python src/cli.py log

# List files
python src/cli.py ls

# View file content
python src/cli.py cat <blob_hash>

# Create a branch
python src/cli.py branch feature

# Switch branch
python src/cli.py checkout feature

# Show a commit
python src/cli.py show <commit_hash>

# Diff two commits
python src/cli.py diff <hash1> <hash2>

# Start web UI
python src/cli.py serve
```

### Web UI

```bash
python src/app.py
# Open http://localhost:5000
```

The web UI lets you create repos, browse files, view commit history with a timeline graph, and see color-coded diffs.

## Running Tests

```bash
pytest tests/ -v
```

## TODO (your part)

The following operations in `src/frontend/operations.py` are stubs:

- `add(file_path)` -- stage a file for the next commit
- `delete_file(file_path)` -- remove a file from tracking
- `create_new_commit(message, author)` -- create a new commit on the current branch
