"""Error Handling module."""


class LibraryError(Exception):
    """Base error class for all library errors."""


class MissingFalconPy(LibraryError):
    """FalconPy library is not available."""

    def __init__(self):
        """Initialize the error, print an alert and then exit."""
        super().__init__()
        raise SystemExit(
            "CrowdStrike FalconPy must be installed in order to use this application.\n"
            "Please execute `python3 -m pip install crowdstrike-falconpy` and try again."
            )
