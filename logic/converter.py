from utilities.iterable import Iterable


def convert_to_token(item) -> str:
    if item is None:
        return '\\'
    if isinstance(item, int):
        return str(item)
    if isinstance(item, set):
        return str(item)
    if isinstance(item, tuple):
        return '\\'.join(Iterable(item)
                         .map(lambda element:
                              '' if element is None else str(element)))


def convert_puzzle(puzzle: dict):
    def yield_strings():
        maximum_length = (Iterable(puzzle.values())
                          .map(lambda value: len(convert_to_token(value)))
                          .max())

        converted = ''
        height, width = (Iterable(Iterable(puzzle)
                                  .map(lambda subject: subject[position])
                                  .max()
                                  for position in range(2))
                         .map(lambda subject: subject + 1))

        for x in range(height):
            for y in range(width):
                token = convert_to_token(puzzle.get((x, y)))
                tabulation = ' ' * (maximum_length - len(token) + 1)
                converted += token + tabulation
            yield converted
            converted = ''

    return [*yield_strings()]
