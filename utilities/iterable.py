from functools import reduce
from itertools import chain, islice
from operator import mul

__all__ = ['Iterable']


def perform_mapping(func):
    def wrapped(self, selector=lambda entry: entry):
        self._data = map(selector, self._data)
        return func(self)

    return wrapped


def perform_filtering(func):
    def wrapped(self, predicate=lambda entry: True):
        self._data = filter(predicate, self._data)
        return func(self)

    return wrapped


class Iterable:
    def __init__(self, *iterators):
        self._data = chain(*iterators)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return 'Iterable({0})'.format(self._data)

    def __iter__(self):
        return iter(self._data)

    def __next__(self):
        return next(self._data)

    @perform_filtering
    def filter(self):
        return self

    @perform_mapping
    def map(self):
        return self

    @perform_mapping
    def chain(self):
        self._data = chain(*self)
        return self

    def concat(self, other):
        self._data = chain(iter(self), other)
        return self

    def zip(self, other):
        self._data = zip(self, other)
        return self

    @perform_mapping
    def max(self):
        return max(self)

    @perform_mapping
    def min(self):
        return min(self)

    @perform_mapping
    def sum(self):
        return sum(self)

    @perform_mapping
    def composition(self):
        return reduce(mul, self)

    @perform_filtering
    def count(self) -> int:
        count = 0
        for _ in self:
            count += 1
        return count

    @perform_filtering
    def first(self):
        return next(self)

    def first_or_default(self, predicate=lambda entry: True, default=None):
        try:
            return self.first(predicate)
        except StopIteration:
            return default

    def take(self, amount: int):
        self._data = islice(self, amount)
        return self

    @perform_mapping
    def to_list(self) -> list:
        return [*self]

    @perform_mapping
    def to_tuple(self) -> tuple:
        return tuple(self)

    @perform_mapping
    def to_set(self) -> set:
        return {*self}

    def to_lookup(self, key_selector) -> dict:
        lookup = {}

        for element in self:
            key = key_selector(element)
            lookup.setdefault(key, [])
            lookup.get(key).append(key)

        return lookup
