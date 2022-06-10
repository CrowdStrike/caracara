"""Caracara Example execution timer."""

from datetime import datetime
from math import ceil


class Timer():
    """Timer class to track example execution times."""

    def __init__(self):
        """Initialize the timer."""
        self.start = datetime.utcnow()
        self.divider = 1000000

    def __str__(self):
        """Return current progressed time in seconds as a string."""
        return f"{float((datetime.utcnow() - self.start).microseconds / self.divider)}"

    def __float__(self):
        """Return current progressed time in seconds as a float."""
        return float((datetime.utcnow() - self.start).microseconds / self.divider)

    def __int__(self):
        """Return current progressed time in seconds as an integer (rounded up)."""
        return ceil((datetime.utcnow() - self.start).microseconds / self.divider)
