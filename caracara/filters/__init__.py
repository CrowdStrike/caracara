"""
Falcon Query Language (FQL) filter string builder module.

Allows for the automatic creation of FQL strings.
"""

__all__ = [
    "FalconFilter",
]

from caracara_filters import FQLGenerator as FalconFilter
