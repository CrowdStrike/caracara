# pylint: disable=too-few-public-methods
"""Common functions available to filters across all modules."""
import re

from datetime import datetime, timedelta


class IPChecker:
    """Check IP address strings for validity via regex."""

    def __init__(self):
        """Set up an IP address checked object and pre-compile the regex."""
        self._ipv4_re = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

    def check_ipv4(self, addr: str) -> bool:
        """Check whether an IPv4 address matches the specification regex."""
        return self._ipv4_re.match(addr) is not None


class ISOTimestampChecker:
    """Check timestamp strings to see whether they conform to the ISO8601 UTC Zulu format."""

    def __init__(self):
        """Set up an ISO timestamp checker object and pre-compile the regex."""
        self._iso_re = re.compile(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'
        )

    def is_iso_format(self, timestamp: str):
        """Perform the check based on the regex expression compiled within the class."""
        return self._iso_re.match(timestamp) is not None


class RelativeTimestamp:
    """
    Relative Timestamp generator class.

    This class contains the logic required to convert from a string (e.g., -30m) to an absolute
    UTC ISO8601 timestamp. This is the format expected by the Falcon API, and enables filters
    such as LastSeen.

    Examples:
    -1hr = take one hour away from the current time
    -30m = take thirty mins away from the current time
    -2d  = take 2 days away from the current time
    +4d  = add 4 days to the current time
    """

    def __init__(self):
        """Set up a RelativeTimestamp object and pre-compile the regex."""
        self._relative_re = re.compile(
            r"^(?P<sign>[-+])(?P<number>\d+)(?P<scale>(s|m|h|d))$"
        )

    def check_relative_timestamp(self, relative_timestamp: str) -> bool:
        """Check whether a relative timestamp matches the specification regex."""
        return self._relative_re.match(relative_timestamp) is not None

    def convert_relative_timestamp(
        self,
        original_timestamp: datetime,
        relative_timestamp: str
    ) -> datetime:
        """Convert a relative timestamp into an absolute ISO8601 timestamp."""
        match = self._relative_re.match(relative_timestamp)
        if match is None:
            # This should be impossible, as we have the check function
            # above to make sure this ridiculous situation doesn't happen
            raise Exception("The timestamp did not match the prescribed format")

        sign = match.group('sign')
        number = int(match.group('number'))
        scale = match.group('scale')

        # Convert to seconds to save code and effort
        if scale == 's':
            seconds = number
        elif scale == 'm':
            seconds = number * 60
        elif scale == 'h':
            seconds = number * 60 * 60
        elif scale == 'd':
            seconds = number * 60 * 60 * 24
        else:
            # Assuming the regex did The Thing, this should be impossible
            raise Exception("The relative timestamp did not contain a supported unit")

        if sign == '-':
            new_timestamp = original_timestamp - timedelta(seconds=seconds)
        else:
            new_timestamp = original_timestamp + timedelta(seconds=seconds)

        return new_timestamp
