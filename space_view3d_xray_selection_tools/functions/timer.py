from contextlib import contextmanager
from time import perf_counter


@contextmanager
def time_section(label, prefix="", suffix="", debug=False):
    """Context manager to measure elapsed time for a code block."""
    if not debug:
        yield
        return

    start = perf_counter()
    yield
    end = perf_counter()
    print(f"{prefix}[{label}] elapsed time: {end - start:.3f} seconds{suffix}")
