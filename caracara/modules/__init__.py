"""
Falcon Host module.

Exposes functions to get host data and perform actions on hosts, such as network containment.
"""
__all__ = [
    'HostsApiModule',
    'PreventionPoliciesApiModule',
    'ResponsePoliciesApiModule',
    'RTRApiModule',
    'MODULE_FILTER_ATTRIBUTES',
]

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

# Build up a list with all filter attributes from the includes modules.
# This makes makes for much easier importing when setting up Falcon Filters.
MODULE_FILTER_ATTRIBUTES = [
    *hosts_filter_attributes,
    *rtr_filter_attributes,
]
