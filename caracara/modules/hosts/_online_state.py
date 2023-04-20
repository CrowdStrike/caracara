"""Caracara Hosts Module: host online state functions.

In order to avoid the main hosts.py file getting too unwieldly, this file contains
the implementations of the host online state query functions.
"""
# Disable the protected access rule because this file is an extension of the class in hosts.py.
# pylint: disable=protected-access
from __future__ import annotations
from typing import (
    List,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from caracara.modules.hosts import HostsApiModule


def filter_by_online_state(
    self: HostsApiModule,
    device_ids: List[str],
    online_state: bool,
):
    """Filter a list of device IDs by an online state.

        Arguments
        ---------
        device_ids: List[str]
            Device IDs to filter against
        online_state: bool
            Online state to filter device IDs on

        Returns
        -------
        List[str]: A list of device IDs with the specified online state
    """
    device_online_state_data = self.get_online_state(device_ids)

    filtered_device_ids = []
    for device_id, device_data in device_online_state_data.items():
        if device_data['state'] == "online" and online_state:
            filtered_device_ids.append(device_id)
        elif device_data['state'] != "online" and not online_state:
            # Consider offline and unknown states to be equivalent
            filtered_device_ids.append(device_id)

    return filtered_device_ids
