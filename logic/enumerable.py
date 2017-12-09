import py_linq


class Enumerable(py_linq.Enumerable):
    def to_list(self):
        return [*self]

    def to_tuple(self):
        return tuple(self)

    def to_set(self):
        return {*self}

    def to_lookup(self, key_selector) -> dict:
        lookup = {}

        for element in self:
            key = key_selector(element)
            lookup.setdefault(key, [])
            lookup.get(key).append(key)

        return lookup
