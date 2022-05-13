"""Main Caracara module. Exposes an API Client to interface with Falcon."""
__all__ = ["Client", "Policy"]

from caracara.client import Client
from caracara.common import Policy
from caracara.common.meta import _pkg_version

# According to PEP 8, dunders should be before imports; however,
# this import is needed for the dunder to function
__version__ = _pkg_version
