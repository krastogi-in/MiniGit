from components.blob import Blob


class TestBlob:
    def test_hash_deterministic(self):
        b1 = Blob("hello world")
        b2 = Blob("hello world")
        assert b1.get_hash() == b2.get_hash()

    def test_different_content_different_hash(self):
        b1 = Blob("hello")
        b2 = Blob("world")
        assert b1.get_hash() != b2.get_hash()

    def test_data_preserved(self):
        content = "line1\nline2\nline3"
        b = Blob(content)
        assert b.get_data() == content

    def test_equality(self):
        b1 = Blob("same content")
        b2 = Blob("same content")
        assert b1 == b2

    def test_inequality(self):
        b1 = Blob("a")
        b2 = Blob("b")
        assert b1 != b2

    def test_hash_is_hex_string(self):
        b = Blob("test")
        h = b.get_hash()
        assert isinstance(h, str)
        assert len(h) == 64
        int(h, 16)

    def test_empty_content(self):
        b = Blob("")
        assert b.get_data() == ""
        assert len(b.get_hash()) == 64

    def test_str_returns_hash(self):
        b = Blob("test")
        assert str(b) == b.get_hash()

    def test_usable_as_dict_key(self):
        b1 = Blob("key content")
        b2 = Blob("key content")
        d = {b1: "value"}
        assert d[b2] == "value"
