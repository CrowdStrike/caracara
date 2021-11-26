"""Hosts API"""
try:
    from falconpy import Hosts, HostGroup
except ImportError as no_falconpy:
    raise SystemExit(
        "CrowdStrike FalconPy must be installed in order to use this application.\n"
        "Please execute `python3 -m pip install crowdstrike-falconpy` and try again."
        ) from no_falconpy
from .._api import ToolboxAPI


class FalconAPI(ToolboxAPI):
    """Class to represent the Falcon API and all relevant service collections."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.hosts = Hosts(auth_object=self.auth)
        self.host_group = HostGroup(auth_object=self.auth)
