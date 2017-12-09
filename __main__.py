import argparse
from sys import stderr, stdin, exit
from logic.error_checker import check_puzzle
from logic.puzzle_maker import make_puzzle
from logic.solver import (solve_puzzle, is_puzzle_solved,
                          yield_all_possible_solutions)
from logic.converter import convert_puzzle


def print_puzzle(puzzle: dict, filled: bool):
    for string in convert_puzzle(puzzle, filled):
        print(string)
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Cross sums (also known as "Kakuro") puzzle solver.')
    parser.add_argument('-f', '--file', help='file with cross sums puzzle')
    multiple_solutions_group = parser.add_mutually_exclusive_group()
    multiple_solutions_group.add_argument('-a', '--all', action='store_true',
                                          help='show all possible solutions '
                                               'if there was more than one', )
    multiple_solutions_group.add_argument('-d', '--filled',
                                          action='store_true',
                                          help='fill unsolved cells')
    arguments = parser.parse_args()

    try:
        with (stdin if arguments.file is None
        else open(arguments.file, encoding='utf-8')) as file:
            puzzle = make_puzzle(file)
            check_puzzle(puzzle)
            solve_puzzle(puzzle)
            solved = is_puzzle_solved(puzzle)
            if solved:
                print_puzzle(puzzle, True)
            elif arguments.all:
                count = 0
                for solution in yield_all_possible_solutions(puzzle):
                    print_puzzle(solution, True)
                    count += 1
                print('Total {0} solutions.'.format(count))
            else:
                print('Puzzle has been partially solved.')
                print('This is the best solution for it.')
                print_puzzle(puzzle, arguments.filled)
                exit(4)

    except RuntimeError as exception:
        print('Puzzle is unsolvable. {0}'.format(str(exception)), file=stderr)
        exit(3)

    except Exception as exception:
        print(str(exception), file=stderr)
        exit(1)

    exit(0)


if __name__ == '__main__':
    main()
