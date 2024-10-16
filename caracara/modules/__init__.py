"""
Caracara Modules Package Initialisation.

Proides pipework to link together the various modules within Caracara and expose them to
the Client object at setup.
"""

__all__ = [
    "CustomIoaApiModule",
    "FlightControlApiModule",
    "HostsApiModule",
    "PreventionPoliciesApiModule",
    "ResponsePoliciesApiModule",
    "RTRApiModule",
    "SensorDownloadApiModule",
    "SensorUpdatePoliciesApiModule",
    "UsersApiModule",
]

from caracara.modules.custom_ioa import CustomIoaApiModule
from caracara.modules.flight_control import FlightControlApiModule
from caracara.modules.hosts import HostsApiModule
from caracara.modules.prevention_policies import PreventionPoliciesApiModule
from caracara.modules.response_policies import ResponsePoliciesApiModule
from caracara.modules.rtr import RTRApiModule
from caracara.modules.sensor_download import SensorDownloadApiModule
from caracara.modules.sensor_update_policies import SensorUpdatePoliciesApiModule
from caracara.modules.users import UsersApiModule
