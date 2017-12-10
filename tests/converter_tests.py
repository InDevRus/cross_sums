import pathmagic
import unittest
from tests.test_decorators import *
from logic import converter


class ConverterTests(unittest.TestCase):
    @assert_equality(converter.convert_puzzle, iterable=True)
    def test_convert_puzzle(self):
        puzzle = {(0, 0): 1, (0, 1): (1, None), (1, 0): {1, 2}, (1, 1): None,
                  (2, 0): {1}, (2, 1): (None, 3)}
        return [(puzzle, ('1      1:     ',
                          '{1, 2} :      ',
                          '{1}    :3     '))]


if __name__ == '__main__':
    unittest.main()
