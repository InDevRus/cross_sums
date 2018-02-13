from utilities.iterable import Iterable
from functools import wraps


def find_invalid_hints(puzzle: dict, vertical: bool):
    def possible_after_hint(hint_cell: tuple) -> bool:
        next_cell = puzzle.get((hint_cell[0] + vertical,
                                hint_cell[1] + (not vertical)))
        return isinstance(next_cell, int) or isinstance(next_cell, set)

    return (Iterable(puzzle).first_or_default(
        lambda point: (isinstance(puzzle.get(point), tuple)
                       and puzzle.get(point)[not vertical] is not None
                       and not possible_after_hint(point))))


def check(message):
    def decorator(func):
        @wraps(func)
        def wrapped(puzzle: dict):
            result = func(puzzle)
            if result is not None:
                raise (ValueError
                       (message.format
                        (*Iterable(result).map(lambda number: number + 1))))
        return wrapped
    return decorator


@check('Invalid horizontal hint found. '
       'Not a number and not a free cell '
       'after hint in {0} line, {1} token.')
def check_horizontal_hints(puzzle: dict):
    return find_invalid_hints(puzzle, False)


@check('Invalid vertical hint found. '
       'Not a number and not a free cell '
       'after hint in {0} line, {1} token.')
def check_vertical_hints(puzzle: dict):
    return find_invalid_hints(puzzle, True)


@check('Invalid free cell found. '
       'Not a number, the free cell or a hint '
       'before free cell in {0} line, {1} token.')
def find_impossible_free_cells(puzzle: dict):
    def possible_before_free_cell(free_cell: tuple) -> bool:
        for orientation in range(2):
            previous = (free_cell[0] - orientation,
                        free_cell[1] - (not orientation))
            previous_value = puzzle.get(previous)
            if not ((isinstance(previous_value, tuple)
                     and previous_value[not orientation])
                    or isinstance(previous_value, set)
                    or isinstance(previous_value, int)):
                return False
        return True

    return (Iterable(puzzle)
            .first_or_default(lambda cell: isinstance(puzzle.get(cell), set)
                              and not possible_before_free_cell(cell)))


def check_puzzle(puzzle: dict):
    (Iterable((check_horizontal_hints,
               check_vertical_hints,
               find_impossible_free_cells))
        .map(lambda func: func(puzzle))
        .to_tuple())
