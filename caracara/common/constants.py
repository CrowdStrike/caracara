"""Common constants to be shared throughout Caracara."""

FILTER_OPERATORS = {
    "EQUAL": '',
    "NOT": '!',
    "GREATER": '>',
    "GTE": '>=',
    "LESS": '<',
    "LTE": '<=',
}

# Batch size of data downloaded via a multi-threaded data pull
DATA_BATCH_SIZE = 500

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
