"""Filter-Related Function Decorators."""
from functools import wraps
from inspect import signature
from typing import Callable

from caracara.filters import FalconFilter


def filter_string(func: Callable):
    """Decorate a function to ensure that a Falcon Filter object is converted to an FQL string."""
    # Load the function's signature, and confirm that self and filters are present
    sig = signature(func)
    if 'filters' not in sig.parameters:
        raise ValueError(f'The function {func.__name__} does not have a filters parameter')

    if 'self' not in sig.parameters:
        raise ValueError(
            f"The function {func.__name__} must be a class function with a self parameter"
        )

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Load in the arguments passed to the function and bind them to the function's signature
        _args = sig.bind(*args, **kwargs)
        # Apply any default parameters (e.g., the filters=None where filters is not specified)
        _args.apply_defaults()
        # Get references to the self and filters arguments for logging and processing purposes
        self = _args.arguments['self']
        filters = _args.arguments['filters']

        if hasattr(self, 'logger'):
            self.logger.debug(f"Entering filter_string wrapper for function {func.__name__}")

        if not filters:
            filter_str = None
        elif isinstance(filters, FalconFilter):
            if hasattr(self, 'logger'):
                self.logger.debug("Rewriting FalconFilter to a string via its get_fql() function")
            filter_str = filters.get_fql()
        elif isinstance(filters, str):
            filter_str = filters
        else:
            raise Exception(
                "A filter of an incorrect type was passed into the function. "
                "Expected a FalconFilter or a string"
            )

        if hasattr(self, 'logger'):
            self.logger.debug("Exiting decorator")

        # Overwrite the filters argument in the bound signature with the string representation.
        # This ensures that FalconPy is always passed a string, and never a FalconFilter object.
        _args.arguments['filters'] = filter_str

        # Return the original function with the modified arguments
        return func(*_args.args, **_args.kwargs)
    return wrapper
