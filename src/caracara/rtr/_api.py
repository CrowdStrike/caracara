"""Real Time Response APIs"""
try:
    from falconpy.real_time_response import RealTimeResponse
    from falconpy.real_time_response_admin import RealTimeResponseAdmin
except ImportError as no_falconpy:
    raise SystemExit(
        "CrowdStrike FalconPy must be installed in order to use this application.\n"
        "Please execute `python3 -m pip install crowdstrike-falconpy` and try again."
        ) from no_falconpy
from .._api import ToolboxAPI


class FalconAPI(ToolboxAPI):
    """Class to represent the Falcon API and all relevant service collections."""
    def __init__(self, key: str = None, secret: str = None, auth_object: object = None):
        super().__init__(key=key, secret=secret, auth_object=auth_object)

        self.rtr = RealTimeResponse(auth_object=self.auth)
        self.rtr_admin = RealTimeResponseAdmin(auth_object=self.auth)
