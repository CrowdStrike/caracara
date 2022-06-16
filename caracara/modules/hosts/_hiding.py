"""Caracara Hosts Module: host hiding functions.

In order to avoid the main hosts.py file getting too unwieldly, this file contains
the implementations of the functions required to hide and unhide hosts from the
Falcon UI.
"""
# Disable the protected access rule because this file is an extension of the class in hosts.py.
# pylint: disable=protected-access
from __future__ import annotations
from functools import partial
from typing import (
    Dict,
    List,
    TYPE_CHECKING,
)

from caracara.common.batching import batch_get_data
from caracara.common.constants import SCROLL_BATCH_SIZE
from caracara.common.exceptions import (
    DeviceNotFound,
    MustProvideFilter,
)
from caracara.common.pagination import all_pages_numbered_offset_parallel
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string

if TYPE_CHECKING:
    from caracara.modules.hosts import HostsApiModule


@filter_string
def describe_hidden_devices(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict:
    """Return a dictionary containing details for every hidden device in your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the hidden device search.

    Returns
    -------
    dict: A dictionary containing details for every hidden device discovered.
    """
    self.logger.info("Describing hidden devices based on the filter string %s", filters)
    device_ids = self.get_hidden_ids(filters)
    device_data = batch_get_data(device_ids, self.hosts_api.get_device_details)

    return device_data


@filter_string
def get_hidden_ids(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> List[str]:
    """Return a list of IDs (string) for every hidden device in your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    List[str]: A list of all device IDs discovered.
    """
    self.logger.info("Getting the IDs of all hidden devices using the filter: %s", filters)
    func = partial(self.hosts_api.query_hidden_devices, filter=filters)
    id_list: List[str] = all_pages_numbered_offset_parallel(
        func=func,
        logger=self.logger,
        limit=SCROLL_BATCH_SIZE,
    )
    if not id_list:
        return DeviceNotFound

    return id_list


@filter_string
def hide(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict:
    """Hide a host or list of hosts within your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    dict: A dictionary containing details for the device hide result.
    """
    if not filters:
        raise MustProvideFilter

    return self._perform_action(
        action_name="hide_host",
        device_ids=self.get_device_ids(filters),
    )["resources"]


@filter_string
def unhide(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict:
    """Unhide a host or list of hosts within your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    dict: A dictionary containing details for the device unhide result.
    """
    if not filters:
        raise MustProvideFilter

    return self._perform_action(
        action_name="unhide_host",
        device_ids=self.get_hidden_ids(filters)
    )["resources"]
