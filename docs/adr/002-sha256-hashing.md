# ADR-002: Use SHA-256 for Content Hashing

## Status

Accepted

## Date

2024-01-15

## Context

Git uses SHA-1 for content-addressable storage. SHA-1 has known collision
vulnerabilities (SHAttered attack, 2017). We need to choose a hash function
for MiniGit's object identifiers.

Options considered:
1. **SHA-1** (160-bit) — matches real Git, but deprecated for security
2. **SHA-256** (256-bit) — industry standard, collision-resistant
3. **BLAKE3** — faster but requires external dependency

## Decision

Use SHA-256 from Python's `hashlib` (stdlib). All object hashes are 64-character
lowercase hexadecimal strings.

## Consequences

### Positive
- Strong collision resistance (no known practical attacks)
- Available in Python stdlib — no external dependencies
- Aligns with Git's migration direction (SHA-256 transition is underway)
- 64-char hex strings are easy to validate with regex

### Negative
- Different from current Git's SHA-1 (less educational for exact Git internals)
- Slightly longer hashes (64 vs 40 chars) — minor UX consideration
- Slower than BLAKE3 for large files (negligible for educational project)
