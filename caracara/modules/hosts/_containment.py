"""Caracara Hosts Module: host containment functions.

In order to avoid the main hosts.py file getting too unwieldly, this file contains
the implementations of the host containment functions.
"""
# Disable the protected access rule because this file is an extension of the class in hosts.py.
# pylint: disable=protected-access
from __future__ import annotations
from typing import (
    Dict,
    TYPE_CHECKING,
)

from caracara.common.exceptions import MustProvideFilter
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string

if TYPE_CHECKING:
    from caracara.modules.hosts import HostsApiModule


@filter_string
def contain(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict:
    """Contain a host or list of hosts within your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    dict: A dictionary containing details for the device containment result.
    """
    if not filters:
        raise MustProvideFilter

    return self._perform_action(
        action_name="contain",
        device_ids=self.get_device_ids(filters),
    )["resources"]


@filter_string
def release(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict:
    """Lift containment for a host or list of hosts within your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    dict: A dictionary containing details for the device containment result.
    """
    if not filters:
        raise MustProvideFilter

    return self._perform_action(
        action_name="lift_containment",
        device_ids=self.get_device_ids(filters),
    )["resources"]
