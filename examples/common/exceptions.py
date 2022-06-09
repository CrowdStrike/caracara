"""Caracara Examples custom error handlers."""


class BaseError(Exception):
    """Base error class."""


class MissingArgument(BaseError):
    """A required argument was not provided. Check YAML configuration."""

    def __init__(self, argument_name, message="A required argument was not provided."):
        """Intialize a MissingArgument error."""
        self.argument_name = argument_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Output the missing argument name along with the message."""
        return f"No '{self.argument_name}' provided -> {self.message}"


class NoDevicesFound(BaseError):
    """No devices were found matching the filter provided."""

    def __init__(self,
                 filter_fql="No filters applied",
                 message="No devices matched the provided Falcon Filter."
                 ):
        """Initialize a NoDevicesFound error."""
        self.filter_fql = filter_fql
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Return the FQL filter along with the message."""
        return f"{self.filter_fql} -> {self.message}"


class NoSessionsConnected(BaseError):
    """No successful connections were made for the RTR batch request."""

    def __init__(self, message="No successful connections were made for this batch."):
        """Initialize a NoSessionsConnected error."""
        self.message = message
        super().__init__(self.message)
