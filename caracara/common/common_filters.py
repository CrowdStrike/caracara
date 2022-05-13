"""Caracara FQL filters that can be used in multiple modules."""
from caracara.filters.fql import FalconFilterAttribute


class GenericNameFilterAttribute(FalconFilterAttribute):
    """Generic filter for any 'name' attribute."""

    name = "Name"
    fql = "name"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts any string to be passed as a 'name' "
            "attribute. Examples of named objects in FQL include "
            "response and prevention policies."
        )


FILTER_ATTRIBUTES = [
    GenericNameFilterAttribute,
]
