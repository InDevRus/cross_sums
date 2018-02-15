import unittest
from io import StringIO
from functools import wraps

from utilities.iterable import Iterable

__all__ = ['assert_equality', 'append_arguments', 'assert_raises',
           'wrap_string_in_io', 'unittest', 'StringIO', 'Iterable']


def assert_equality(func=lambda subject: subject, iterable: bool = False,
                    out_type=tuple, assert_difference: bool = False,
                    orderless: bool = False):
    def decorator(test_method):
        @wraps(test_method)
        def wrapped(self: unittest.TestCase):
            self.maxDiff = None
            for args in test_method(self):
                result = func(*args[:-1])
                result = out_type(result) if iterable else result
                if orderless:
                    for element in result:
                        self.assertIn(element, args[-1])
                    for element in args[-1]:
                        self.assertIn(element, result)
                else:
                    comparator = (self.assertEqual if not assert_difference
                                  else self.assertNotEqual)
                    comparator(result, args[-1])
        return wrapped
    return decorator


def assert_raises(func, exception, regex: str = None,
                  iterable=True, out_type=tuple):
    def decorator(test_method):
        @wraps(test_method)
        def wrapped(self: unittest.TestCase):
            for args in test_method(self):
                with (self.assertRaises(exception) if regex is None else
                      self.assertRaisesRegex(exception, regex)):
                    func(*args) if not iterable else out_type(func(*args))
        return wrapped
    return decorator


def append_arguments(*args, position: int = -1):
    def decorator(test_method):
        @wraps(test_method)
        def wrapped(self: unittest.TestCase):
            data = test_method(self)
            for arguments in data:
                for argument in args:
                    arguments.insert(position, argument)
            return data
        return wrapped
    return decorator


def wrap_string_in_io(position: int = 0, iterable: bool = False):
    def decorator(test_method):
        @wraps(test_method)
        def wrapped(self: unittest.TestCase):
            data = test_method(self)
            for args in data:
                if iterable:
                    args[position] = (Iterable(args[position])
                                      .to_list(StringIO))
                else:
                    args[position] = StringIO(args[position])
            return data
        return wrapped
    return decorator
