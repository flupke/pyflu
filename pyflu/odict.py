from UserDict import IterableUserDict


class odict(IterableUserDict):
    def __init__(self, dict = None):
        self._keys = []
        IterableUserDict.__init__(self, dict)

    def __delitem__(self, key):
        IterableUserDict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        IterableUserDict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def __iter__(self):
        for key in self._keys:
            yield key

    def clear(self):
        IterableUserDict.clear(self)
        self._keys = []

    def copy(self):
        dict = IterableUserDict.copy(self)
        dict._keys = self._keys[:]
        return dict

    def items(self):
        return zip(self._keys, self.values())

    def insert(self, index, key, value):
        IterableUserDict.__setitem__(self, key, value)
        self._keys.insert(index, key)

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def pop(self, key, *default):
        ret = IterableUserDict.pop(self, key, *default)
        try:
            self._keys.remove(key)
        except ValueError:
            # This exception can happen when a default value is passed, so we
            # can safely ignore it
            pass
        return ret

    def setdefault(self, key, failobj=None):
        IterableUserDict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dict):
        IterableUserDict.update(self, dict)
        for key in dict.keys():
            if key not in self._keys: self._keys.append(key)

    def values(self):
        return map(self.get, self._keys)


