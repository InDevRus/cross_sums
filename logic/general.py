from pipe import *


@Pipe
def first_or_default(iterable, default=None):
    try:
        return next(iter(iterable))
    except StopIteration:
        return default
