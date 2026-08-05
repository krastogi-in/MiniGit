"""Tests for the Blob component."""

from components.blob import Blob


class TestBlob:
    """Verify Blob hashing, equality, and data preservation."""

    def test_hash_deterministic(self) -> None:
        """Identical content produces the same hash."""
        b1 = Blob("hello world")
        b2 = Blob("hello world")
        assert b1.get_hash() == b2.get_hash()

    def test_different_content_different_hash(self) -> None:
        """Different content produces different hashes."""
        b1 = Blob("hello")
        b2 = Blob("world")
        assert b1.get_hash() != b2.get_hash()

    def test_data_preserved(self) -> None:
        """get_data() returns the original content unchanged."""
        content = "line1\nline2\nline3"
        b = Blob(content)
        assert b.get_data() == content

    def test_equality(self) -> None:
        """Blobs with same content are equal."""
        b1 = Blob("same content")
        b2 = Blob("same content")
        assert b1 == b2

    def test_inequality(self) -> None:
        """Blobs with different content are not equal."""
        b1 = Blob("a")
        b2 = Blob("b")
        assert b1 != b2

    def test_hash_is_hex_string(self) -> None:
        """Hash is a 64-character hexadecimal string."""
        b = Blob("test")
        h = b.get_hash()
        assert isinstance(h, str)
        assert len(h) == 64
        int(h, 16)

    def test_empty_content(self) -> None:
        """Empty string is valid blob content."""
        b = Blob("")
        assert b.get_data() == ""
        assert len(b.get_hash()) == 64

    def test_str_returns_hash(self) -> None:
        """str(blob) returns the hash."""
        b = Blob("test")
        assert str(b) == b.get_hash()

    def test_usable_as_dict_key(self) -> None:
        """Blobs can be used as dictionary keys via __hash__."""
        b1 = Blob("key content")
        b2 = Blob("key content")
        d = {b1: "value"}
        assert d[b2] == "value"
