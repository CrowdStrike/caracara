"""Caracara module-agnostic decorators."""
from functools import wraps
from inspect import signature
from typing import Callable

from caracara.common.constants import PLATFORMS


def platform_name_check(func: Callable):
    """Decorate a function to ensure that a platform_name argument is within the specified list."""
    # Load the function's signature, and confirm that the platform_name parameter has been added
    sig = signature(func)
    if 'platform_name' not in sig.parameters:
        raise ValueError(f'The function {func.__name__} does not have a platform_name parameter')

    if 'self' not in sig.parameters:
        raise ValueError(
            f"The function {func.__name__} must be a class function with a self parameter"
        )

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Load in the arguments passed to the function and bind them to the function's signature
        _args = sig.bind(*args, **kwargs)
        # Apply any default parameters (e.g., platform_name=None where this is not specified)
        _args.apply_defaults()
        # Get references to the self and platform_name arguments for logging and processing purposes
        self = _args.arguments['self']
        platform_name = _args.arguments['platform_name']

        if hasattr(self, 'logger'):
            self.logger.debug(f"Entering filter_string wrapper for function {func.__name__}")

        if platform_name and isinstance(platform_name, str):
            if platform_name not in PLATFORMS:
                raise Exception(
                    f"The platform_name value supplied ({platform_name}) is not valid. "
                    f"Valid options are: {PLATFORMS}"
                )

        # If we get this far, either the platform_name given is reasonable, or it was None (which
        # is reasonable if the function signature allows this)

        if hasattr(self, 'logger'):
            self.logger.debug("Exiting decorator")

        # Return to the original function
        return func(*_args.args, **_args.kwargs)
    return wrapper
