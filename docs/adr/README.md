# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for MiniGit.

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-sqlite-storage.md) | Use SQLite for storage | Accepted | 2024-01-15 |
| [002](002-sha256-hashing.md) | Use SHA-256 for content hashing | Accepted | 2024-01-15 |
| [003](003-full-snapshot-commits.md) | Full-snapshot commits | Accepted | 2024-01-20 |
| [004](004-tag-storage.md) | Dedicated `tags` table for tag storage | Accepted | 2026-08-14 |

## Format

Each ADR follows the format:
- **Title**: Short descriptive title
- **Status**: Proposed / Accepted / Deprecated / Superseded
- **Context**: What is the issue we're facing?
- **Decision**: What did we decide?
- **Consequences**: What are the trade-offs?
