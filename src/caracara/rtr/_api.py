"""Real Time Response APIs"""
try:
    from falconpy import RealTimeResponse, RealTimeResponseAdmin
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

        self.rtr = RealTimeResponse(auth_object=self.auth)
        self.rtr_admin = RealTimeResponseAdmin(auth_object=self.auth)
