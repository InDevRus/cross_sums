from pipe import *


def get_symbols_from_file(file):
    """
    Reads files and returns every symbol from them.

    Args:
        file (file): File object.

    Yields (str): every symbol from file.
    """
    symbol = file.read(1)
    while symbol != '':
        yield symbol
        symbol = file.read(1)


def parse_token(token: str) -> object:
    message = 'Invalid token "{0}" in {1} line, {2} token.'
    if token == '_':
        return set()
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
    puzzle = {}
    line_number = token_number = 0
    token = ''

    for symbol in iter((get_symbols_from_file(file), ' ')) | chain:
        if symbol in (' ', '\n', '\r'):
            if iter(token) | count > 0:
                try:
                    cell = parse_token(token)
                except SyntaxError as exception:
                    raise SyntaxError(
                        str(exception)
                        .format(token, line_number, token_number))
                puzzle[line_number, token_number] = cell
                token_number += 1
            if symbol == '\n':
                line_number += 1
                token_number = 0
            token = ''
        else:
            token += symbol

    return puzzle
