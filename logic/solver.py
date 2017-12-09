from functools import lru_cache
from pipe import *
from logic.general import first_or_default


@lru_cache(maxsize=(sum(range(1, 10)) * 9 * 2 ** 9))
def find_unique_combinations(summary: int, parts_quantity: int,
                             restricted: frozenset = frozenset({})) -> set:
    @lru_cache(maxsize=(sum(range(1, 10)) * 9 * 2 ** 9))
    def yield_unique_combinations(number: int, part_count: int,
                                  restricted_numbers: frozenset):
        if part_count == 1:
            if 1 <= number <= 9 and number not in restricted_numbers:
                yield restricted_numbers.union([number])
        else:
            for part in set(range(1, 10)).difference(restricted_numbers):
                yield from yield_unique_combinations(number - part,
                                                     part_count - 1,
                                                     restricted_numbers.union
                                                     ([part]))

    return set(yield_unique_combinations(summary, parts_quantity, restricted))


def initialize_cells(puzzle: dict):
    free_cells = (iter(puzzle)
                  | where(lambda cell: puzzle.get(cell) == set()))
    for free_cell in free_cells:
        puzzle[free_cell] = {*range(1, 10)}
    return puzzle


def get_block(puzzle: dict, hint: tuple, horizontal: bool) -> (int, list):
    hint_sum = puzzle.get(hint)[horizontal]
    current = [*iter(hint)]
    block = []
    restricted = []

    while True:
        current[horizontal] += 1
        current_value = puzzle.get(iter(current) | as_tuple)
        if current_value is None or isinstance(current_value, tuple):
            break
        if isinstance(current_value, int):
            hint_sum -= current_value
            restricted.append(current_value)
        if isinstance(current_value, set):
            block.append(iter(current) | as_tuple)

    return hint_sum, block, frozenset(restricted)


def fill_block(puzzle: dict, hint: tuple, horizontal: bool):
    hint_sum, block, restricted = get_block(puzzle, hint, horizontal)
    if not block:
        return puzzle
    combinations = find_unique_combinations(hint_sum, len(block), restricted)
    if combinations == set():
        raise RuntimeError('No possible sum combination for {0} hint '
                           'in {1} line, {2} token.'
                           .format('horizontal' if horizontal else 'vertical',
                                   *hint))

    possible_numbers = set(iter(combinations) | chain)
    for cell in block:
        puzzle[cell] = puzzle.get(cell).intersection(possible_numbers)
        if puzzle.get(cell) == set():
            raise RuntimeError('No possible values to fill free cell in '
                               '{0} line, {1} token.'.format(*cell))
    return puzzle


def fill_free_cells(puzzle: dict):
    hints = (iter(puzzle)
             | where(lambda cell: isinstance(puzzle.get(cell), tuple)))
    for hint in hints:
        value = puzzle.get(hint)
        if value[0] is not None:
            fill_block(puzzle, hint, False)
        if value[1] is not None:
            fill_block(puzzle, hint, True)

    return puzzle


def get_neighbor_cells(puzzle: dict, cell: tuple):
    def update_current():
        nonlocal current
        offset = (iter(direction)
                  | select(lambda number: number * multiplier)
                  | as_tuple)
        current = (iter(offset)
                   | izip(cell)
                   | select(lambda iterable: iter(iterable) | add)
                   | as_tuple)

    directions = (iter((-1, 1))
                  | select(lambda number: ((0, number), (number, 0)))
                  | chain)
    for direction in directions:
        multiplier = 1
        current = None
        update_current()
        value = puzzle.get(current)
        while isinstance(value, int) or (isinstance(value, set)):
            if isinstance(value, set):
                yield current
            multiplier += 1
            update_current()
            value = puzzle.get(current)


def reduce_puzzle(puzzle: dict) -> dict:
    def is_cell_solved(cell: tuple):
        value = puzzle.get(cell)
        return isinstance(value, set) and (iter(value) | count) == 1

    was_reduce = True
    while was_reduce:
        was_reduce = False
        puzzle = fill_free_cells(puzzle)
        solved_cells = (iter(puzzle)
                        | where(lambda cell: is_cell_solved(cell))
                        | as_tuple)
        for solved_cell in solved_cells:
            was_reduce = True
            new_value = iter(puzzle.get(solved_cell)) | first
            puzzle[solved_cell] = new_value
            for neighbor in get_neighbor_cells(puzzle, solved_cell):
                reduced_cell = puzzle.get(neighbor) - {new_value}
                if reduced_cell == set():
                    raise RuntimeError('No possible number after reduce in '
                                       '{0} line, {1} token.'
                                       .format(*solved_cell))
                puzzle[neighbor] = reduced_cell

    return puzzle


def elementary_puzzle_reduce(puzzle: dict):
    function_sequence = (initialize_cells, reduce_puzzle)
    for func in function_sequence:
        func(puzzle)
    return puzzle


def exclude_impossible_numbers(puzzle: dict) -> dict:
    was_reduce = True
    while was_reduce:
        was_reduce = False
        for free_cell in (iter(puzzle)
                          | where(lambda cell: isinstance(puzzle.get(cell),
                                                          set))):
            for possible_number in puzzle.get(free_cell):
                new_puzzle = puzzle.copy()
                new_puzzle[free_cell] = {possible_number}
                try:
                    elementary_puzzle_reduce(new_puzzle)
                except RuntimeError:
                    reduced_cell = puzzle.get(free_cell) - {possible_number}
                    if reduced_cell == set():
                        raise RuntimeError(
                            'No possible number after reduce in '
                            '{0} line, {1} token.'.format(*free_cell))
                    was_reduce = True
                    puzzle[free_cell] = reduced_cell
            reduce_puzzle(puzzle)

    return reduce_puzzle(puzzle)


def solve_puzzle(puzzle: dict) -> dict:
    function_sequence = (elementary_puzzle_reduce, exclude_impossible_numbers)
    for func in function_sequence:
        puzzle = func(puzzle)
        if (iter(puzzle.values())
                | where(lambda value: not isinstance(value, set))
                | count) == 0:
            return puzzle

    return puzzle


def is_puzzle_solved(puzzle: dict) -> bool:
    return (iter(puzzle.values())
            | where(lambda value: isinstance(value, set))
            | count) == 0


def yield_all_possible_solutions(puzzle: dict):
    first_unfilled_cell = (iter(puzzle)
                           | where(lambda cell:
                                   isinstance(puzzle.get(cell), set))
                           | first_or_default)
    if first_unfilled_cell is None:
        yield puzzle
        return
    for possible_number in puzzle.get(first_unfilled_cell):
        new_puzzle = puzzle.copy()
        new_puzzle[first_unfilled_cell] = {possible_number}
        try:
            yield from yield_all_possible_solutions(solve_puzzle(new_puzzle))
        except RuntimeError:
            pass
