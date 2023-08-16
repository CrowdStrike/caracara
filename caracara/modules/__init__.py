"""
Caracara Modules Package Initialisation.

Proides pipework to link together the various modules within Caracara and expose them to
the Client object at setup.
"""
__all__ = [
    'CustomIoaApiModule',
    'FlightControlApiModule',
    'HostsApiModule',
    'PreventionPoliciesApiModule',
    'ResponsePoliciesApiModule',
    'RTRApiModule',
    'UsersApiModule',
]

from caracara.modules.custom_ioa import CustomIoaApiModule
from caracara.modules.flight_control import FlightControlApiModule
from caracara.modules.hosts import HostsApiModule
from caracara.modules.prevention_policies import PreventionPoliciesApiModule
from caracara.modules.response_policies import ResponsePoliciesApiModule
from caracara.modules.rtr import RTRApiModule
from caracara.modules.users import UsersApiModule
