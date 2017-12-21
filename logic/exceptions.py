class UnsolvablePuzzleError(RuntimeError):
    def __init__(self, message):
        message = 'Puzzle is unsolvable. {0}'.format(message)
        super(UnsolvablePuzzleError, self).__init__(message)
