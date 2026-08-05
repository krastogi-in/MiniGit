"""Blob object — immutable content-addressable file storage."""

from hashlib import sha256


class Blob:
    """Immutable content-addressed data block identified by its SHA-256 hash.

    A blob stores raw file content. Two blobs with identical content
    always produce the same hash, enabling deduplication across commits.
    """

    def __init__(self, data: str) -> None:
        self._data: str = data
        self._hash: str = sha256(data.encode()).hexdigest()

    def get_hash(self) -> str:
        """Return the 64-character hex SHA-256 hash of this blob's content."""
        return self._hash

    def get_data(self) -> str:
        """Return the raw string content of this blob."""
        return self._data

    def __str__(self) -> str:
        return self._hash

    def __repr__(self) -> str:
        return f"Blob({self._hash})"

    def __hash__(self) -> int:
        return hash(self._hash)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Blob):
            return NotImplemented
        return self._hash == other._hash
