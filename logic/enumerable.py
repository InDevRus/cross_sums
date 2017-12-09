import py_linq
from py_linq.exceptions import NoElementsError


class Enumerable(py_linq.Enumerable):
    def __next__(self):
        yield from iter(self)
        raise StopIteration

    def element_at(self, n):
        try:
            for number in range(max(n, 0)):
                next(self)
            return next(self)
        except StopIteration:
            raise NoElementsError(u"No element found at index {0}".format(n))

    def to_list(self):
        return [*self]

    def to_tuple(self):
        return tuple(self)

    def to_set(self):
        return {*self}
