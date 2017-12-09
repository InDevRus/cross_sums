from pipe import *
from re import finditer
from logic.enumerable import Enumerable


def parse_token(token: str) -> object:
    message = 'Invalid token "{0}" in {1} line, {2} token.'
    if token == '_':
        return {*range(1, 10)}
    elif token == ':':
        return None
    elif token.isdecimal():
        value = int(token)
        if not (1 <= value <= 9):
            raise SyntaxError(message)
        return value
    else:
        parts = token.split(':')
        if (iter(parts) | count != 2
            or (iter(parts)
                | where(lambda string: not string.isdecimal() and string != '')
                | count) != 0):
            raise SyntaxError(message)
        return (iter(parts)
                | select(lambda part: int(part) if part != '' else None)
                | as_tuple)


def make_puzzle(file) -> dict:
    """
    Makes puzzle from file.

    Args:
        file (file): File object.

    Raises:
          SyntaxError: If invalid token found somewhere.

    Returns (dict): Puzzle.
    """

    def yield_tokens():
        nonlocal line_number, token_number
        line = file.readline()
        while line != '':
            tokens = (Enumerable(finditer('\S+', line))
                .select(lambda match_object: match_object.group(0)))
            for part in tokens:
                yield part
                token_number += 1
            line = file.readline()
            line_number += 1
            token_number = 0

    line_number = token_number = 0
    puzzle = {}

    for token in yield_tokens():
        try:
            cell = parse_token(token)
            puzzle[line_number, token_number] = cell
        except SyntaxError as exception:
            raise SyntaxError(
                str(exception).format(token, line_number, token_number))

    return puzzle
