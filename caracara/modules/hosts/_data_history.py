"""Caracara Hosts Module: host data history functions.

In order to avoid the main hosts.py file getting too unwieldly, this file contains
the implementations of the functions required to retrieve data that Falcon gathers
on hosts' network and login histories.
"""
from __future__ import annotations
from typing import (
    Dict,
    TYPE_CHECKING,
)

from caracara.common.batching import batch_get_data
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string

if TYPE_CHECKING:
    from caracara.modules.hosts import HostsApiModule


@filter_string
def describe_network_address_history(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict:
    """Return a dictionary of network address history for all devices in your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    dict: A dictionary containing network address history for every device discovered.
    """
    device_ids = self.get_device_ids(filters)
    device_data = batch_get_data(device_ids, self.hosts_api.query_network_address_history)

    return device_data


@filter_string
def describe_login_history(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict:
    """Return a dictionary containing login history for every device in your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    dict: A dictionary containing login history for every device discovered.
    """
    self.logger.info("Describing login history for devices matching the filter: %s", filters)
    device_ids = self.get_device_ids(filters)
    device_data = batch_get_data(device_ids, self.hosts_api.query_device_login_history)

    return device_data


@filter_string
def describe_state(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict[str, Dict]:
    """Return a dictionary containing online state for devices matching the provided filter.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    dict: A dictionary containing state details for every device discovered.
    """
    self.logger.info("Describing device states according to the filter string %s", filters)
    device_ids = self.get_device_ids(filters)
    device_data = batch_get_data(device_ids, self.hosts_api.get_device_details)

    for device_id, state in batch_get_data(device_ids, self.hosts_api.get_online_state).items():
        if device_id in device_data:
            device_data[device_id]["state"] = state.get("state", "unknown")

    return device_data
