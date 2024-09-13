"""Caracara Hosts Module: host online state functions.

In order to avoid the main hosts.py file getting too unwieldly, this file contains
the implementations of the host online state query functions.
"""

# Disable the protected access rule because this file is an extension of the class in hosts.py.
# pylint: disable=protected-access
from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from caracara.common.batching import batch_get_data
from caracara.common.constants import ONLINE_STATE_DATA_BATCH_SIZE, OnlineState
from caracara.common.exceptions import InvalidOnlineState

if TYPE_CHECKING:
    from caracara.modules.hosts import HostsApiModule


def validate_online_state(
    self: HostsApiModule,
    online_state: Union[OnlineState, str],
):
    """Raise an exception if the online_state_string is not a valid online state.

    Arguments
    ---------
    online_state: OnlineState or str, required
        OnlineState or string to validate.
    """
    if not isinstance(online_state, OnlineState) and online_state not in OnlineState:
        raise InvalidOnlineState(online_state)
    self.logger.debug(f"Validated online state {online_state}")


def get_online_state(
    self: HostsApiModule,
    device_ids: List[str],
) -> List[str]:
    """Return a dictionary containing online state details for every device specified by ID.

    You should only use this endpoint if you already have a list of Device IDs / AIDs,
    and want to retreive data about them directly. If you need to get device data via a
    filter, and you do not yet have a list of Device IDs, you should consider using the
    describe_devices() function.

    Arguments
    ---------
    device_ids: [str], required
        A list of Falcon Device IDs.

    Returns
    -------
    dict: A dictionary containing online state details for every device listed.
    """
    self.logger.info("Obtaining online state data for %s devices", len(device_ids))
    device_online_state_data = batch_get_data(
        device_ids,
        self.hosts_api.get_online_state,
        data_batch_size=ONLINE_STATE_DATA_BATCH_SIZE,
    )
    return device_online_state_data


def filter_device_ids_by_online_state(
    self: HostsApiModule,
    device_ids: List[str],
    online_state: Union[OnlineState, str],
) -> List[str]:
    """Filter a list of device IDs by an online state.

    Arguments
    ---------
    device_ids: List[str]
        Device IDs to filter against
    online_state: OnlineState or str
        Online state to filter device IDs on. Options are "online", "offline", "unknown"

    Returns
    -------
    List[str]: A list of device IDs with the specified online state
    """
    self.validate_online_state(online_state)

    device_state_data = self.get_online_state(device_ids)

    return list(
        filter(
            lambda device_id: device_state_data[device_id]["state"] == online_state,
            device_state_data,
        )
    )
