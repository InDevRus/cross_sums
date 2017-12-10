import pathmagic
import unittest
from test_decorators import *

from logic import error_checker
from logic.puzzle_maker import make_puzzle


class ErrorCheckerTests(unittest.TestCase):
    @assert_equality(lambda subject:
                     error_checker.check_puzzle(make_puzzle(subject)))
    @wrap_string_in_io()
    @append_arguments(None, position=1)
    def test_check_valid_puzzle(self):
        return [[''], [':   23: 30:   :     :     27: 12: 16:\n'
                       ':16 _   _     :     17:24 _   _   _\n'
                       ':17 _   _     15:29 _     _   _   _\n'
                       ':35 _   _     _     _     _   12: :\n'
                       ':   :7  _     _     7:8   _   _   7:\n'
                       ':   11: 10:16 _     _     _   _   _\n'
                       ':21 _   _     _     _     :5  _   _\n'
                       ':6  _   _     _     :     :3  _   _']]

    @assert_raises(lambda subject:
                   error_checker.check_horizontal_hints(make_puzzle(subject)),
                   ValueError, 'Invalid horizontal hint found. '
                               'Not a number and not a free cell '
                               'after hint in 1 line, 2 token.')
    @wrap_string_in_io()
    def test_check_invalid_horizontal_hints(self):
        return [[': :3\n: :'], [': :3 3:4\n: : 2']]

    @assert_raises(lambda subject:
                   error_checker.check_vertical_hints(make_puzzle(subject)),
                   ValueError, 'Invalid vertical hint found. '
                               'Not a number and not a free cell '
                               'after hint in 2 line, 1 token.')
    @wrap_string_in_io()
    def test_check_invalid_vertical_hints(self):
        return [[': 4:\n3:4 4'], [': 4:\n3:4 4\n: :']]

    @assert_raises(lambda subject:
                   error_checker.find_impossible_free_cells
                   (make_puzzle(subject)),
                   ValueError, 'Invalid free cell found. '
                               'Not a number, the free cell or a hint '
                               'before free cell in 2 line, 2 token.')
    @wrap_string_in_io()
    def test_check_invalid_free_cells(self):
        return [[': : :\n: _ :'], [': 2: :\n: _ :']]


if __name__ == '__main__':
    unittest.main()
