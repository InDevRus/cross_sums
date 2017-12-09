from pipe import *
from logic.enumerable import Enumerable


def convert_to_token(item, filled) -> str:
    if item is None:
        return ':'
    if isinstance(item, int):
        return str(item)
    if isinstance(item, set):
        return str(item) if filled else '_'
    if isinstance(item, tuple):
        return ':'.join(Enumerable(item)
                        .select(lambda element:
                                '' if element is None else str(element)))


def convert_puzzle(puzzle: dict, filled):
    def yield_strings():
        maximum_length = (iter(puzzle.values())
                          | select(lambda value:
                                   len(convert_to_token(value, filled)))
                          | max)

        converted = ''
        height, width = (iter((iter(puzzle)
                               | select(lambda subject: subject[position])
                               | max) for position in range(2))
                         | select(lambda subject: subject + 1))

        for x in range(height):
            for y in range(width):
                token = convert_to_token(puzzle.get((x, y)), filled)
                tabulation = ' ' * (maximum_length - len(token) + 1)
                converted += token + tabulation
            yield converted
            converted = ''

    return [*yield_strings()]
