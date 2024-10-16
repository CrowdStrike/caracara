"""Common constants to be shared throughout Caracara."""

from enum import Enum, EnumMeta

# Batch size of data downloaded via a multi-threaded data pull
DEFAULT_DATA_BATCH_SIZE = 500

# Batch size of data downloaded via a multi-threaded data pull from the online state endpoint
ONLINE_STATE_DATA_BATCH_SIZE = 100

# Default pagination limit
PAGINATION_LIMIT = 100

# Batch size of data downloaded from scrolled endpoints
SCROLL_BATCH_SIZE = 5000

# Host group batch size
HOST_GROUP_SCROLL_BATCH_SIZE = 100

# List of all platforms supported by Falcon
PLATFORMS = [
    "Linux",
    "Mac",
    "Windows",
]

#
DEFAULT_COMMENT = "This action was performed by the Caracara Python library."


# Device online states classes
class MetaEnum(EnumMeta):
    """Overrided class for the use of the in operator and to query for all valid enum values."""

    def __init__(cls, *kwargs):
        """Store all possible values of the Enum subclass."""
        cls.VALUES = [state.value for state in cls.__members__.values()]
        super().__init__(kwargs)

    def __contains__(cls: Enum, item: str) -> bool:
        """Override the __contains__ method to use the in operator with Enum subclasses."""
        return item in cls.VALUES


class OnlineState(Enum, metaclass=MetaEnum):
    """
    Falcon OnlineState class.

    Enum class of valid device online states. Valid states are 'online', 'offline', and 'unknown'.
    """

    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

    def __eq__(self, item: str) -> bool:
        """Override the __eq__ method for strings to compare the OnlineState's string value."""
        return str(self.value) == item
