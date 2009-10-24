"""
Profiling helpers.
"""

try:
    import cProfile as profile_
except ImportError:
    import profile as profile_
from pstats import Stats


def profile(func, args=None, kwargs=None, sort="time"):
    prof = profile_.Profile()
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    ret = prof.runcall(func, *args, **kwargs)
    stats = Stats(prof)
    stats.sort_stats(sort)
    stats.print_stats()
    return ret
