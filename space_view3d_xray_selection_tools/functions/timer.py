import contextlib
import time


@contextlib.contextmanager
def time_section(label: str, prefix: str = "", suffix: str = "", debug: bool = False):
    """Context manager to measure elapsed time for a code block."""
    if not debug:
        yield
        return

    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"{prefix}[{label}] elapsed time: {end - start:.3f} seconds{suffix}")
