from hashlib import sha256


class Blob(object):
    """
    A blob is a piece of data that is stored in the repository.
    It is identified by its hash.
    It is immutable.
    """

    def __init__(self, data):
        self._data = data
        self._hash = sha256(data.encode()).hexdigest()

    def get_hash(self):
        return self._hash

    def get_data(self):
        return self._data

    def __str__(self):
        return self._hash

    def __repr__(self):
        return f"Blob({self._hash})"

    def __hash__(self):
        return hash(self._hash)

    def __eq__(self, other):
        return self.get_hash() == other.get_hash()