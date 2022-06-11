"""Caracara exceptions."""


class BaseException(Exception):
    """Base exception class from which all other exceptions inherit."""


class GenericAPIError(BaseException):
    """A generic error from the API."""

    def __init__(self, error_list: list = None):
        """Construct an instance of the GenericAPIError class."""
        
        self.errors = [{
            "code": 500,
            "message": "An unexpected error has occurred"
        }]
        if error_list:
            self.errors = error_list
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
