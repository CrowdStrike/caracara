"""Caracara Hosts Module: host tagging functions.

In order to avoid the main hosts.py file getting too unwieldly, this file contains
the implementations of functions that can tag and untag hosts within the Falcon UI.
"""
# Disable the protected access rule because this file is an extension of the class in hosts.py.
# pylint: disable=protected-access
from __future__ import annotations
from typing import (
    Dict,
    List,
    TYPE_CHECKING,
)

from caracara.common.exceptions import (
    MustProvideFilter,
)
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string

if TYPE_CHECKING:
    from caracara.modules.hosts import HostsApiModule


def _create_tag_list(potential_list: List[str] or str) -> List[str]:
    """Create a properly formatted list from a list, a string or a comma-delimited string."""
    tag_list = potential_list
    if not isinstance(potential_list, list):
        tag_list = potential_list.split(",")

    return tag_list


def _update_device_tags(
    self: HostsApiModule,
    action_name: str,
    device_ids: List[str],
    tag_list: List[str]
) -> Dict:
    """Tag or untag a device within the tenant."""
    return self.hosts_api.update_device_tags(
        action_name=action_name,
        ids=device_ids,
        tags=tag_list
    )["body"]


@filter_string
def tag(
    self: HostsApiModule,
    tags: List[str] or str, filters: FalconFilter or str = None,
) -> Dict:
    """Tag a host or list of hosts within your Falcon tenant.

    Arguments
    ---------
    tags: List of strings
        Tags to be applied to the discovered devices.
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    dict: A dictionary containing details for the device tagging result.
    """
    if not filters:
        raise MustProvideFilter

    return self._update_device_tags(
        action_name="add",
        tag_list=self._create_tag_list(tags),
        device_ids=self.get_device_ids(filters)
    )["resources"]


@filter_string
def untag(
    self: HostsApiModule,
    tags: List[str] or str, filters: FalconFilter or str = None,
) -> Dict:
    """Untag a host or list of hosts within your Falcon tenant.

    Arguments
    ---------
    tags: List of strings
        Tags to be applied to the discovered devices.
    filters: FalconFilter or str, optional
        Filters to apply to the device search.

    Returns
    -------
    dict: A dictionary containing details for the device tagging result.
    """
    if not filters:
        raise MustProvideFilter

    return self._update_device_tags(
        action_name="remove",
        tag_list=self._create_tag_list(tags),
        device_ids=self.get_device_ids(filters)
    )["resources"]
