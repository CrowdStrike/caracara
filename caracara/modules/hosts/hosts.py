r"""Hosts and Host Group API.

 ___ ___             __          ___ ___                                                    __
|   Y   .-----.-----|  |_.-----.|   Y   .---.-.-----.---.-.-----.-----.--------.-----.-----|  |_
|.  1   |  _  |__ --|   _|__ --||.      |  _  |     |  _  |  _  |  -__|        |  -__|     |   _|
|.  _   |_____|_____|____|_____||. \_/  |___._|__|__|___._|___  |_____|__|__|__|_____|__|__|____|
|:  |   |                       |:  |   |                 |_____|
|::.|:. |                       |::.|:. |
`--- ---'                       `--- ---'

This module handles interactions with the CrowdStrike Falcon Hosts and Host Group APIs.
"""
from functools import partial
from typing import (
    Dict,
    List,
)

from falconpy import (
    Hosts,
    HostGroup,
    OAuth2,
)

from caracara.common.batching import batch_get_data
from caracara.common.constants import SCROLL_BATCH_SIZE
from caracara.common.module import FalconApiModule
from caracara.common.pagination import (
    all_pages_numbered_offset_parallel,
    all_pages_token_offset,
)
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string


class HostsApiModule(FalconApiModule):
    """The HostsApiModule represents interactions with the Hosts and Host Group APIs."""

    name = "CrowdStrike Hosts API Module"
    help = "Interact with hosts and host groups within your Falcon tenant."

    def __init__(self, api_authentication: OAuth2):
        """Construct an instance of HostApiModule class."""
        super().__init__(api_authentication)

        self.logger.debug("Configuring the FalconPy Hosts API")
        self.hosts_api = Hosts(auth_object=self.api_authentication)

        self.logger.debug("Configuring the FalconPy Host Group API")
        self.host_group_api = HostGroup(auth_object=self.api_authentication)

    def describe_devices(self, filters: FalconFilter or str = None) -> Dict:
        """Return a dictionary containing details for every device in your Falcon tenant.

        Arguments
        ---------
        filters: FalconFilter or str, optional
            Filters to apply to the device search.

        Returns
        -------
        dict: A dictionary containing details for every device discovered.
        """
        self.logger.info("Describing devices according to the filter string %s", filters)

        device_ids = self.get_device_ids(filters)
        device_data = batch_get_data(device_ids, self.hosts_api.get_device_details)

        return device_data

    def describe_hidden_devices(self, filters: FalconFilter or str = None) -> Dict:
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

    def describe_login_history(self, filters: FalconFilter or str = None) -> Dict:
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

    def describe_network_address_history(self, filters: FalconFilter or str = None) -> Dict:
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

    def contain(self, filters: FalconFilter or str = None) -> Dict:
        """Contain a host or list of hosts within your Falcon tenant.

        Arguments
        ---------
        filters: FalconFilter or str, optional
            Filters to apply to the device search.

        Returns
        -------
        dict: A dictionary containing details for the device containment result.
        """
        return self._perform_action(
            action_name="contain",
            device_ids=self.get_device_ids(filters),
        )["resources"]

    def release(self, filters: FalconFilter or str = None) -> Dict:
        """Lift containment for a host or list of hosts within your Falcon tenant.

        Arguments
        ---------
        filters: FalconFilter or str, optional
            Filters to apply to the device search.

        Returns
        -------
        dict: A dictionary containing details for the device containment result.
        """
        return self._perform_action(
            action_name="lift_containment",
            device_ids=self.get_device_ids(filters),
        )["resources"]

    def hide(self, filters: FalconFilter or str = None) -> Dict:
        """Hide a host or list of hosts within your Falcon tenant.

        Arguments
        ---------
        filters: FalconFilter or str, optional
            Filters to apply to the device search.

        Returns
        -------
        dict: A dictionary containing details for the device hide result.
        """
        return self._perform_action(
            action_name="hide_host",
            device_ids=self.get_device_ids(filters),
        )["resources"]

    def unhide(self, filters: FalconFilter or str = None) -> Dict:
        """Unhide a host or list of hosts within your Falcon tenant.

        Arguments
        ---------
        filters: FalconFilter or str, optional
            Filters to apply to the device search.

        Returns
        -------
        dict: A dictionary containing details for the device unhide result.
        """
        return self._perform_action(action_name="unhide_host",
                                    device_ids=self.get_hidden_ids(filters)
                                    )["resources"]

    def tag(self, tags: List[str] or str, filters: FalconFilter or str = None) -> Dict:
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
        return self._update_device_tags(action_name="add",
                                        tag_list=self._create_tag_list(tags),
                                        device_ids=self.get_device_ids(filters)
                                        )["resources"]

    def untag(self, tags: List[str] or str, filters: FalconFilter or str = None) -> Dict:
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
        return self._update_device_tags(action_name="remove",
                                        tag_list=self._create_tag_list(tags),
                                        device_ids=self.get_device_ids(filters)
                                        )["resources"]

    def _perform_action(self, action_name: str, device_ids: List[str]) -> Dict:
        """Perform the specified action against the list of targets."""
        return self.hosts_api.perform_action(ids=device_ids, action_name=action_name)["body"]

    @staticmethod
    def _create_tag_list(potential_list: List[str] or str) -> List[str]:
        """Create a properly formatted list from a list, a string or a comma-delimited string."""
        tag_list = potential_list
        if not isinstance(potential_list, list):
            tag_list = potential_list.split(",")

        return tag_list

    def _update_device_tags(
        self,
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
    def get_device_ids(self, filters: FalconFilter or str = None) -> List[str]:
        """Return a list of IDs (string) for every device in your Falcon tenant.

        Arguments
        ---------
        filters: FalconFilter or str, optional
            Filters to apply to the device search.

        Returns
        -------
        List[str]: A list of all device IDs discovered.
        """
        self.logger.info("Searching for device IDs using the filter string %s", filters)
        func = partial(self.hosts_api.query_devices_by_filter_scroll, filter=filters)
        device_ids: List[str] = all_pages_token_offset(func=func, logger=self.logger)
        return device_ids

    @filter_string
    def get_hidden_ids(self, filters: FalconFilter or str = None) -> List[str]:
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
        device_ids = all_pages_numbered_offset_parallel(
            func=func,
            logger=self.logger,
            limit=SCROLL_BATCH_SIZE
        )
        return device_ids
