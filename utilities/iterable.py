import itertools
from functools import reduce, wraps
from operator import mul

__all__ = ['Iterable', 'compose']


def compose(*functions):
    return reduce(lambda f, g: lambda x: g(f(x)), functions)


def perform_mapping(func=lambda subject: subject):
    @wraps(func)
    def wrapped(self, selector=lambda entry: entry, *selectors):
        self._data = map(compose(selector, *selectors), self)
        return func(self)

    return wrapped


def perform_filtering(func=lambda subject: subject):
    @wraps(func)
    def wrapped(self, predicate=lambda entry: True):
        self._data = filter(predicate, self)
        return func(self)

    return wrapped


class Iterable:
    def __init__(self, *iterators):
        self._data = itertools.chain(*iterators)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return 'Iterable({0})'.format(self._data)

    def __iter__(self):
        return iter(self._data)

    def __next__(self):
        return next(self._data)

    def __contains__(self, item):
        for entry in self:
            if entry == item:
                return True
        return False

    @perform_filtering
    def filter(self):
        return self

    @perform_mapping
    def map(self):
        return self

    @perform_mapping
    def chain(self):
        self._data = itertools.chain(*self)
        return self

    def concat(self, other):
        self._data = itertools.chain(iter(self), other)
        return self

    def zip(self, other):
        self._data = zip(self, other)
        return self

    def distinct(self, key_selector=lambda subject: subject,
                 hashable: bool = False, comparable: bool = False):
        passed = []
        if hashable:
            iterator = iter({*map(key_selector, self)})
        elif comparable:
            iterator = map(lambda pair: pair[0],
                           itertools.groupby(sorted(self, key=key_selector)))
        else:
            iterator = (entry for entry in self if
                        (entry not in passed and
                         (passed.append(key_selector(entry)) or True)))
        self._data = iterator
        return self

    def sort(self, key_selector=lambda entry: entry):
        self._data = sorted(self, key=key_selector)
        return self

    def max(self, key_selector=lambda entry: entry):
        return max(self, key=key_selector)

    def min(self, key_selector=lambda entry: entry):
        return min(self, key=key_selector)

    @perform_mapping
    def sum(self):
        return sum(self)

    @perform_mapping
    def composition(self):
        return reduce(mul, self)

    def product(self, other):
        self._data = itertools.product(self, other)
        return self

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
        perform_filtering()(self, predicate)
        return next(self, default)

    def take(self, amount: int):
        self._data = itertools.islice(self, amount)
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
            lookup.get(key).append(element)

        return lookup
