# MiniGit

A simplified Git clone built from scratch in Python. Implements content-addressable storage, tree structures, commit history, branching, and diffs.

## Also in this repo: AI SDLC factory

Alongside the MiniGit app there is a **ticket-driven AI SDLC skills registry** (Cursor skills + loop). Humans stay on the outer loop; agents process **any** Jira issue. Start here: **[docs/ai-sdlc/README.md](docs/ai-sdlc/README.md)**. To connect Jira and run a loop: **[docs/ai-sdlc/HOW-TO-EXECUTE.md](docs/ai-sdlc/HOW-TO-EXECUTE.md)**. Product coding conventions for agents remain in **[AGENTS.md](AGENTS.md)**.

## Architecture

``
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
├── skills/                 # AI SDLC factory (feature-agnostic)
├── evals/                  # Skill registry evals + rubrics
├── tests/                  # Test suite
├── docs/
│   ├── ai-sdlc/           # What the factory is / how to run
│   ├── examples/          # Optional sample features (not the loop)
│   ├── adr/               # Architecture Decision Records
│   ├── design/            # Design documentation
│   └── openapi.yaml       # API specification
├── repos/                  # Repositories created via web UI
├── pyproject.toml          # Project config (ruff, mypy, pytest, commitizen)
├── Makefile                # Development commands
└── .pre-commit-config.yaml # Git hooks for quality enforcement
```

## How It Works

MiniGit mirrors real Git's object model:

- **Blobs** store raw file content, identified by SHA-256 hash
- **Trees** store directory listings (name + type + hash), also hashed
- **Commits** point to a root tree + parent commit + metadata, also hashed
- **Refs** (branches) are name-to-commit-hash mappings

Every commit is a full snapshot. Unchanged files reuse the same blob across commits, and diffs are computed on-the-fly by comparing commit trees.

## Quick Start

```bash
# One-command setup (installs all dependencies + pre-commit hooks)
make setup

# Run all quality checks (lint + typecheck + tests)
make check

# AI SDLC registry smoke test
make eval-skills
```

## Setup (Manual)

```bash
python -m pip install -e ".[dev]"
pre-commit install
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

## Development

| Command | Description |
|---------|-------------|
| `make setup` | Install dependencies + pre-commit hooks |
| `make lint` | Run ruff linter (style + security) |
| `make typecheck` | Run mypy type checker |
| `make test` | Run pytest with coverage |
| `make check` | All checks (lint + typecheck + test + boundaries) |
| `make fmt` | Auto-format code |
| `make audit` | Dependency security audit |
| `make boundaries` | Check architectural layer violations |

## Running Tests

```bash
# With coverage report
pytest tests/ -v --cov=src --cov-report=term-missing

# Or via Makefile
make test
```

## Contributing

1. Follow [conventional commit](https://www.conventionalcommits.org/) messages
2. Add type annotations to all new functions
3. Add docstrings to all public functions
4. Ensure `make check` passes before opening a PR
5. See [AGENTS.md](AGENTS.md) for architectural rules
