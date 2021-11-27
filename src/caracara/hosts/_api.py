"""Hosts API."""
from .._error import MissingFalconPy
from .._api import ToolboxAPI

try:
    from falconpy import Hosts, HostGroup
except ImportError as no_falconpy:
    raise MissingFalconPy from no_falconpy


class FalconAPI(ToolboxAPI):
    """Class to represent the Falcon API and all relevant service collections."""

    def __init__(self, **kwargs):
        """Initialize the toolbox APIs."""
        super().__init__(**kwargs)

        self.hosts = Hosts(auth_object=self.auth)
        self.host_group = HostGroup(auth_object=self.auth)
