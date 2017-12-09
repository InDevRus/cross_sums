from functools import singledispatch
from pipe import *


@singledispatch
def convert_to_token(item, filled):
    if item is None:
        return ':'


@convert_to_token.register(int)
def _(item, filled):
    return str(item)


@convert_to_token.register(set)
def _(item, filled):
    if filled:
        return str(item)
    return '_'


@convert_to_token.register(tuple)
def _(item, filled):
    return (iter(item)
            | select(lambda element: '' if element is None else element)
            | concat(':'))


def convert_puzzle(puzzle: dict, filled) -> str:
    maximum_length = (iter(puzzle.values())
                      | select(lambda value:
                               len(convert_to_token(value, filled)))
                      | max)

    converted = ''
    previous = (0, 0)
    for cell in puzzle:
        token = convert_to_token(puzzle.get(cell), filled)
        tabulation = ' ' * (maximum_length - len(token) + 1)
        if cell[0] > previous[0]:
            converted += '\n'
        converted += token + tabulation
        previous = cell

    return converted
