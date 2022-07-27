r"""Hosts and Host Group APIs.

 ___ ___             __          ___ ___                                                    __
|   Y   .-----.-----|  |_.-----.|   Y   .---.-.-----.---.-.-----.-----.--------.-----.-----|  |_
|.  1   |  _  |__ --|   _|__ --||.      |  _  |     |  _  |  _  |  -__|        |  -__|     |   _|
|.  _   |_____|_____|____|_____||. \_/  |___._|__|__|___._|___  |_____|__|__|__|_____|__|__|____|
|:  |   |                       |:  |   |                 |_____|
|::.|:. |                       |::.|:. |                                   CrowdStrike Caracara
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
from caracara.common.exceptions import (
    GenericAPIError,
)
from caracara.common.module import FalconApiModule
from caracara.common.pagination import (
    all_pages_token_offset,
)
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string


# Allow importing from other files into this class so that the file does not end up
# being over 1000 lines long.
# pylint: disable=import-outside-toplevel
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

    # Import containment functions
    from caracara.modules.hosts._containment import (
        contain,
        release,
    )

    # Import data history functions
    from caracara.modules.hosts._data_history import (
        describe_login_history,
        describe_network_address_history,
        describe_state,
    )

    # Import functions pertaining to host groups
    from caracara.modules.hosts._groups import (
        _create_host_group,
        _perform_group_action,
        add_to_group,
        create_group,
        delete_group,
        describe_group_member_ids,
        describe_group_members,
        describe_groups,
        get_group_ids,
        get_group_member_ids,
        get_group_members,
        group,
        remove_from_group,
        ungroup,
        update_group,
    )

    # Import functions to hide, unhide and describe hidden devices
    from caracara.modules.hosts._hiding import (
        describe_hidden_devices,
        get_hidden_ids,
        hide,
        unhide,
    )

    # Import functions to create and modify device tags
    from caracara.modules.hosts._tagging import (
        _create_tag_list,
        _update_device_tags,
        tag,
        untag,
    )

    # Static methods have to be set within the class
    _create_tag_list = staticmethod(_create_tag_list)

    def _perform_action(self, action_name: str, device_ids: List[str]) -> Dict:
        """Perform the specified action against the list of targets."""
        returned = self.hosts_api.perform_action(ids=device_ids, action_name=action_name)["body"]

        if returned["errors"]:
            raise GenericAPIError(returned["errors"])

        return returned

    @filter_string
    def describe_devices(self, filters: FalconFilter or str = None) -> Dict[str, Dict]:
        """Return a dictionary containing details for every device matching the provided filter.

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
        device_data = self.get_device_data(device_ids)

        return device_data

    def get_device_data(self, device_ids: List[str]) -> Dict[str, Dict]:
        """Return a dictionary containing details for every device specified by ID.

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
        dict: A dictionary containing details for every device listed.
        """
        self.logger.info("Obtaining data for %s devices", len(device_ids))
        device_data = batch_get_data(device_ids, self.hosts_api.get_device_details)
        return device_data

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
        id_list: List[str] = all_pages_token_offset(func=func, logger=self.logger)
        return id_list
