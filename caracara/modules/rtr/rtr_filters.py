"""RTR-specific FQL filters."""
from caracara.modules.rtr.constants import RTR_COMMANDS
from caracara.filters.fql import FalconFilterAttribute


class RtrBaseCommandFilterAttribute(FalconFilterAttribute):
    """Filter by Real Time Response (RTR) base command."""

    name = "Command"
    fql = "base_command"
    options = list(RTR_COMMANDS.keys())
    restrict = True
    types = [str]


FILTER_ATTRIBUTES = [
    RtrBaseCommandFilterAttribute,
]
