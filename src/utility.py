import json
from collections.abc import MutableMapping


class IgnoreCaseDict(MutableMapping):
    def __init__(self, **kwargs):
        self._store = {}
        for k, v in kwargs.items():
            self.__setitem__(k, v)

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][-1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __str__(self):
        return str(self._store)

    __repr__ = __str__


def dict2str(obj, ensure_ascii=False):
    return json.dumps(obj, ensure_ascii=ensure_ascii)


