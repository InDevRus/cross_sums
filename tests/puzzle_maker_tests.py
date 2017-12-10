import pathmagic
import unittest
from test_decorators import *

from logic import puzzle_maker


class PuzzleTests(unittest.TestCase):
    @assert_equality(puzzle_maker.make_puzzle)
    @wrap_string_in_io()
    def test_puzzle_making(self):
        return [['1 :2 4:\n: _  10:3',
                 {(0, 0): 1, (0, 1): (None, 2), (0, 2): (4, None),
                  (1, 0): None, (1, 1): {*range(1, 10)}, (1, 2): (10, 3)}],
                [':   23: 30:   :     :     27: 12: 16:\n'
                 ':16 _   _     :     17:24 _   _   _\n'
                 ':17 _   _     15:29 _     _   _   _\n'
                 ':35 _   _     _     _     _   12: :\n'
                 ':   :7  _     _     7:8   _   _   7:\n'
                 ':   11: 10:16 _     _     _   _   _\n'
                 ':21 _   _     _     _     :5  _   _\n'
                 ':6  _   _     _     :     :3  _   _',
                 {(0, 0): None, (0, 1): (23, None), (0, 2): (30, None),
                  (0, 3): None, (0, 4): None, (0, 5): (27, None),
                  (0, 6): (12, None), (0, 7): (16, None), (1, 0): (None, 16),
                  (1, 1): {*range(1, 10)}, (1, 2): {*range(1, 10)},
                  (1, 3): None, (1, 4): (17, 24), (1, 5): {*range(1, 10)},
                  (1, 6): {*range(1, 10)}, (1, 7): {*range(1, 10)},
                  (2, 0): (None, 17), (2, 1): {*range(1, 10)},
                  (2, 2): {*range(1, 10)}, (2, 3): (15, 29),
                  (2, 4): {*range(1, 10)}, (2, 5): {*range(1, 10)},
                  (2, 6): {*range(1, 10)}, (2, 7): {*range(1, 10)},
                  (3, 0): (None, 35), (3, 1): {*range(1, 10)},
                  (3, 2): {*range(1, 10)}, (3, 3): {*range(1, 10)},
                  (3, 4): {*range(1, 10)}, (3, 5): {*range(1, 10)},
                  (3, 6): (12, None), (3, 7): None, (4, 0): None,
                  (4, 1): (None, 7), (4, 2): {*range(1, 10)},
                  (4, 3): {*range(1, 10)}, (4, 4): (7, 8),
                  (4, 5): {*range(1, 10)}, (4, 6): {*range(1, 10)},
                  (4, 7): (7, None), (5, 0): None, (5, 1): (11, None),
                  (5, 2): (10, 16), (5, 3): {*range(1, 10)},
                  (5, 4): {*range(1, 10)}, (5, 5): {*range(1, 10)},
                  (5, 6): {*range(1, 10)}, (5, 7): {*range(1, 10)},
                  (6, 0): (None, 21), (6, 1): {*range(1, 10)},
                  (6, 2): {*range(1, 10)}, (6, 3): {*range(1, 10)},
                  (6, 4): {*range(1, 10)}, (6, 5): (None, 5),
                  (6, 6): {*range(1, 10)}, (6, 7): {*range(1, 10)},
                  (7, 0): (None, 6), (7, 1): {*range(1, 10)},
                  (7, 2): {*range(1, 10)}, (7, 3): {*range(1, 10)},
                  (7, 4): None, (7, 5): (None, 3), (7, 6): {*range(1, 10)},
                  (7, 7): {*range(1, 10)}}],
                ['', {}]]

    @assert_raises(puzzle_maker.make_puzzle, SyntaxError,
                   'Invalid token .+ in \d+ line, \d+ token.')
    @wrap_string_in_io()
    def test_invalid_puzzle_making(self):
        return [['3 7::'], ['1:2:3'], [': : _\n _ None'], ['__ 1 2'],
                ['3:2 :2 _ 2.1'], ['4 5 :\n3:3 42 3:']]


if __name__ == '__main__':
    unittest.main()
