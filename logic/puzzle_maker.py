from re import finditer
from utilities.iterable import Iterable


def parse_token(token: str) -> object:
    message = 'Invalid token "{0}" in {1} line, {2} token.'
    if token == '_':
        return {*range(1, 10)}
    elif token == '\\':
        return None
    elif token.isdecimal():
        value = int(token)
        if not (1 <= value <= 9):
            raise SyntaxError(message)
        return value
    else:
        parts = token.split('\\')
        if (len(parts) != 2
            or (Iterable(parts)
                .count(lambda string:
                       not string.isdecimal() and string != '')) != 0):
            raise SyntaxError(message)
        return (Iterable(parts)
                .to_tuple(lambda part: int(part) if part != '' else None))


def make_puzzle(file) -> dict:
    def yield_tokens():
        nonlocal line_number, token_number
        line = file.readline()
        while line != '':
            tokens = (Iterable(finditer('\S+', line))
                      .map(lambda match_object: match_object.group(0)))
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
