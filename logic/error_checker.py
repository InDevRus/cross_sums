from pipe import *
from logic.general import first_or_default


def find_invalid_hints(puzzle: dict, vertical: bool):
    def possible_after_hint(hint_cell: tuple) -> bool:
        next_cell = puzzle.get((hint_cell[0] + vertical,
                                hint_cell[1] + (not vertical)))
        return isinstance(next_cell, int) or isinstance(next_cell, set)

    return (iter(puzzle)
            | where(lambda point:
                    (isinstance(puzzle.get(point), tuple)
                     and puzzle.get(point)[not vertical] is not None))
            | where(lambda hint: not possible_after_hint(hint))
            | first_or_default)


def check(message):
    def decorator(func):
        def wrapped(puzzle: dict):
            result = func(puzzle)
            if result is not None:
                raise (ValueError
                       (message.format
                        (*result | select(lambda number: number + 1))))
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
        return (iter(((free_cell[0] - 1, free_cell[1]),
                      (free_cell[0], free_cell[1] - 1)))
                | select(lambda cell: puzzle.get(cell))
                | where(lambda cell: isinstance(cell, tuple)
                        or isinstance(cell, set) or isinstance(cell, int))
                | count) == 2

    return (iter(puzzle)
            | where(lambda cell:
                    isinstance(puzzle.get(cell), set))
            | where(lambda cell: not possible_before_free_cell(cell))
            | first_or_default)


def check_puzzle(puzzle: dict):
    (iter((check_horizontal_hints,
           check_vertical_hints,
           find_impossible_free_cells))
     | select(lambda func: func(puzzle))
     | as_tuple)