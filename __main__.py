import argparse
import sys

from logic.converter import convert_puzzle
from logic.error_checker import check_puzzle
from logic.puzzle_maker import make_puzzle
from logic.solver import solve_puzzle
from utilities.iterable import Iterable
from visual import visual


def print_puzzle(puzzle: dict):
    for string in convert_puzzle(puzzle):
        print(string)


def define_arguments() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Cross sums (also known as "Kakuro") puzzle solver.')
    parser.add_argument('-v', '--visual', help='launch visual interface',
                        action='store_true')
    parser.add_argument('-f', '--file', help='file with cross sums puzzle')
    parser.add_argument('-l', '--limit', metavar='n',
                        help='limit of possible solutions '
                             '(integer or asterisk)', default='1')
    return parser


def main(parser: argparse.ArgumentParser):
    arguments = parser.parse_args()

    if arguments.visual:
        visual.main()

    limit = arguments.limit
    if ((limit != '*' and not limit.isnumeric())
            or limit.isnumeric() and int(limit) < 1):
        raise SyntaxError('Limit value must be positive '
                          'number or asterisk.')
    with (sys.stdin if arguments.file is None
          else open(arguments.file, encoding='utf-8')) as file:
        puzzle = make_puzzle(file)
        check_puzzle(puzzle)
        solutions = enumerate(solve_puzzle(puzzle), start=1)
        solutions = (Iterable(solutions).take(int(limit))
                     if limit != '*' else solutions)
        for pair in solutions:
            print('Solution #{0}'.format(pair[0]))
            print_puzzle(pair[1])
            print()


if __name__ == '__main__':
    try:
        main(define_arguments())
    except Exception as exception:
        print(str(exception), file=sys.stderr)
        sys.exit(1)
