"""Caracara Indicator of Attack (IOA) API module."""
from falconpy import OAuth2, CustomIOA

from caracara.common.module import FalconApiModule


class CustomIoaApiModule(FalconApiModule):
    """Caracara Custom Indicator of Attack (IOA) API module."""

    def __init__(self, api_authentication: OAuth2):
        """Create an Custom IOA API object and configure it with a FalconPy OAuth2 object."""
        super().__init__(api_authentication)
        self.custom_ioa_api = CustomIOA(auth_object=api_authentication)
