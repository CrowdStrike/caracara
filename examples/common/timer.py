"""⏰ Caracara Example execution timer."""

import time

from math import ceil


class Timer:
    """Timer class to track example execution times."""

    def __init__(self):
        """Initialize the timer."""
        self.start = time.perf_counter()

    def __str__(self):
        """Return current progressed time in seconds as a string."""
        return f"{time.perf_counter() - self.start}"

    def __float__(self):
        """Return current progressed time in seconds as a float."""
        return float(time.perf_counter() - self.start)

    def __int__(self):
        """Return current progressed time in seconds as an integer (rounded up)."""
        return ceil(time.perf_counter() - self.start)

    def __call__(self):
        """Reset the timer."""
        self.__init__()
