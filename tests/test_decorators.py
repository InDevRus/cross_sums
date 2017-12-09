from io import StringIO
from pipe import *


def assert_equality(func, iterable: bool = False, out_type=tuple,
                    assert_difference: bool = False,
                    orderless: bool = False):
    def decorator(test_method):
        def wrapped(self):
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


def assert_inclusion(func, iterable: bool = False, out_type=tuple,
                     assert_exclusion: bool = False):
    def decorator(test_method):
        def wrapped(self):
            self.maxDiff = None
            for args in test_method(self):
                result = func(*args[:-1])
                result = out_type(result) if iterable else result
                comparator = (self.assertIn if not assert_exclusion
                              else self.assertNotIn)
                comparator(result, args[-1])
        return wrapped
    return decorator


def assert_raises(func, exception, regex: str = None,
                  iterable=True, out_type=tuple):
    def decorator(test_method):
        def wrapped(self):
            for args in test_method(self):
                with (self.assertRaises(exception) if regex is None else
                      self.assertRaisesRegex(exception, regex)):
                    func(*args) if not iterable else out_type(func(*args))
        return wrapped
    return decorator


def append_arguments(*args, position: int = -1):
    def decorator(test_method):
        def wrapped(self):
            data = test_method(self)
            for arguments in data:
                for argument in args:
                    arguments.insert(position, argument)
            return data
        return wrapped
    return decorator


def wrap_string_in_io(position: int = 0, iterable: bool = False):
    def decorator(test_method):
        def wrapped(self):
            data = test_method(self)
            for args in data:
                if iterable:
                    args[position] =\
                        (args[position]
                         | select(lambda string: StringIO(string))
                         | as_list)
                else:
                    args[position] = StringIO(args[position])
            return data
        return wrapped
    return decorator
