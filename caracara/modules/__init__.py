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
    'MODULE_FILTER_ATTRIBUTES',
]

from caracara.modules.custom_ioa import CustomIoaApiModule
from caracara.modules.flight_control import FlightControlApiModule
from caracara.modules.hosts import (
    FILTER_ATTRIBUTES as hosts_filter_attributes,
    HostsApiModule,
)
from caracara.modules.prevention_policies import PreventionPoliciesApiModule
from caracara.modules.response_policies import ResponsePoliciesApiModule
from caracara.modules.rtr import (
    FILTER_ATTRIBUTES as rtr_filter_attributes,
    RTRApiModule,
)
from caracara.modules.users import (
    FILTER_ATTRIBUTES as users_filter_attributes,
    UsersApiModule,
)

# Build up a list with all filter attributes from the includes modules.
# This makes makes for much easier importing when setting up Falcon Filters.
MODULE_FILTER_ATTRIBUTES = [
    *hosts_filter_attributes,
    *rtr_filter_attributes,
    *users_filter_attributes,
]
