"""Caracara exceptions."""
from typing import Dict, List


class BaseCaracaraError(Exception):
    """Base exception class from which all other exceptions inherit."""


class GenericAPIError(BaseCaracaraError):
    """A generic error from the API."""

    def __init__(self, errors: List[Dict] = None):
        """Construct an instance of the GenericAPIError class."""
        self.errors = [{
            "code": 500,
            "message": "An unexpected error has occurred"
        }]
        if errors:
            self.errors = errors
        super().__init__(self.errors)

    def __str__(self):
        """Return all errors as a comma-delimited list."""
        return ", ".join([f"[{x['code']}] {x['message']}" for x in self.errors])

    def __int__(self):
        """Return the first error code as an integer."""
        return int(self.errors[0]["code"])

    def __float__(self):
        """Return the first error code as a float."""
        return float(self.errors[0]["code"])


class MustProvideFilterOrID(GenericAPIError):
    """You must provide either a Falcon Filter or an ID to use this method."""

    def __init__(self):
        """Construct an instance of the MustProvideFilterOrID class."""
        self.errors = [{
            "code": 500,
            "message": "You must provide either a Falcon Filter or an ID to use this method"
        }]
        super().__init__(self.errors)


class MustProvideFilter(GenericAPIError):
    """You must provide a Falcon Filter in order to use this method."""

    def __init__(self):
        """Construct an instance of the MustProvideFilter class."""
        self.errors = [{
            "code": 500,
            "message": "You must provide a Falcon Filter in order to use this method"
        }]
        super().__init__(self.errors)


class HostGroupNotFound(GenericAPIError):
    """The host group you specified is not found."""

    def __init__(self):
        """Construct an instance of the HostGroupNotFound class."""
        self.errors = [{
            "code": 404,
            "message": "The Falcon Filter you provided returned no Host Group matches"
        }]
        super().__init__(self.errors)


class DeviceNotFound(GenericAPIError):
    """The device you specified is not found."""

    def __init__(self):
        """Construct an instance of the DeviceNotFound class."""
        self.errors = [{
            "code": 404,
            "message": "The Falcon Filter you provided returned no device matches"
        }]
        super().__init__(self.errors)


class MissingArgument(GenericAPIError):
    """A required argument was not provided."""

    def __init__(self, arg_name: str = None):
        """Construct an instance of the MissingArgument class."""
        if not arg_name:
            arg_name = "A required argument"
        else:
            arg_name = f"The required argument {arg_name}"
        arg_str = f"{arg_name} was not provided"

        self.errors = [{
            "code": 500,
            "message": arg_str
        }]
        super().__init__(self.errors)


class MissingArguments(GenericAPIError):
    """A required argument was not provided."""

    def __init__(self, arg_names: List[str] = None):
        """Construct an instance of the MissingArguments class."""
        if not arg_names:
            arg_names = "Required arguments"
        else:
            arg_names = f"The required arguments {', '.join(arg_names)}"
        arg_str = f"{arg_names} were not provided"

        self.errors = [{
            "code": 500,
            "message": arg_str
        }]
        super().__init__(self.errors)
