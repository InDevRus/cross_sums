import pathmagic
from tests.__init__ import __all__ as tests
from unittest import main
import argparse

parser = argparse.ArgumentParser(
    description='Test running script')
parser.add_argument('-v', '--verbose',
                    help='verbose output',
                    action='store_true')
args = parser.parse_args()

for test in tests:
    main(module=test, exit=False,
         verbosity=2 if args.verbose else 0)
