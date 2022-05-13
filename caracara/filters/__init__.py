"""
Falcon Query Language (FQL) filter string builder module.

Allows for the automatic creation of FQL strings.
"""

__all__ = [
    "FalconFilter",
    "FalconFilterAttribute",
]

from caracara.filters.falcon_filter import FalconFilter
from caracara.filters.fql import FalconFilterAttribute
