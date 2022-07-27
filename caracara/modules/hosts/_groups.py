"""Caracara Hosts Module: host group functions.

In order to avoid the main hosts.py file getting too unwieldly, this file contains
the implementations of all functions associated with host groups.
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
from caracara.common.constants import HOST_GROUP_SCROLL_BATCH_SIZE
from caracara.common.exceptions import (
    GenericAPIError,
    HostGroupNotFound,
    MissingArgument,
    MissingArguments,
    MustProvideFilterOrID,
)
from caracara.common.pagination import all_pages_numbered_offset_parallel
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string

if TYPE_CHECKING:
    from caracara.modules.hosts import HostsApiModule


def _create_host_group(
    self: HostsApiModule,
    group_name: str = None,
    description: str = None,
    group_type: str = "static",
    assignment_rule: str = None,
) -> Dict[str, Dict]:
    """Create the requested host group within the tenant."""
    if not group_name:
        raise MissingArgument("group_name")
    if not group_type:
        self.logger.info("Group type not specified for creation, defaulting to static.")

    returned = self.host_group_api.create_host_groups(
        name=group_name,
        description=description,
        group_type=group_type,
        assignment_rule=assignment_rule
    )["body"]
    if returned["errors"]:
        raise GenericAPIError(returned["errors"])

    return returned["resources"]


def _perform_group_action(
    self: HostsApiModule,
    action_name: str,
    group_ids: List[str],
    device_ids: List[str],
) -> Dict:
    """Perform the specified action against the host group."""
    returned = self.host_group_api.perform_group_action(
        ids=group_ids,
        action_name=action_name,
        filter=f"(device_id:{device_ids})",
    )["body"]
    if returned["errors"]:
        raise GenericAPIError(returned["errors"])

    return returned


@filter_string
def add_to_group(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
    group_ids: List[str] or str = None,
    device_filters: FalconFilter or str = None,
    device_ids: List[str] or str = None,
) -> Dict:
    """Add a host or list of hosts to a host group within your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Group filter to apply to the host group search. Not required if group_ids are provided.
    group_ids: List[str] or str, optional
        List of host group IDs to update. Comma delimited strings are converted.
        Not required if a group filter is provided. Takes precedence over provided filters.
    device_filters: FalconFilter or str, optional
        Filters to apply to the device search. Not required if device_ids are provided.
    device_ids: List[str] or str, optional
        List of device IDs to add to the host group. Comma delimited strings are converted.
        Not required if a device filter is provided. Takes precedence over device filters.

    Returns
    -------
    dict: A dictionary containing details for the host group update result.
    """
    if isinstance(group_ids, str):
        group_ids = group_ids.split(",")

    if not group_ids and not filters:
        raise MustProvideFilterOrID

    if isinstance(device_ids, str):
        device_ids = device_ids.split(",")

    if not device_ids and not device_filters:
        raise MustProvideFilterOrID

    return self._perform_group_action(
        action_name="add-hosts",
        group_ids=group_ids if group_ids else self.get_group_ids(filters),
        device_ids=device_ids if device_ids else self.get_device_ids(device_filters),
    )["resources"]


def create_group(
    self: HostsApiModule,
    group_name: str = None,
    description: str = None,
    group_type: str = "static",
    assignment_rule: str = None,
) -> Dict:
    """Create a group based upon the provided arguments within your Falcon tenant.

    Arguments
    ---------
    assignment_rule: str, optional - Assignment rule to apply when creating the host group.
    description: str, optional - Description to use for the created host group.
    group_name: str, required - Name of the host group to create.
    group_type: str, optional - Type of host group to create. `dynamic` or `static`.
        Defaults to `static`.

    Returns
    -------
    dict: A dictionary containing details for the host group creation result.
    """
    return self._create_host_group(
        group_name,
        description,
        group_type,
        assignment_rule
    )


def delete_group(
    self: HostsApiModule,
    group_ids: List[str] = None,
    filters: FalconFilter or str = None,
) -> Dict:
    """Delete a host group from within your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Group filter to apply to the host group search. Not required if group_ids are provided.
    group_ids: List[str] or str, optional
        List of host group IDs to update. Comma delimited strings are converted.
        Not required if a group filter is provided. Takes precedence over provided filters.

    Returns
    -------
    dict: A dictionary containing details for the host group update result.
    """
    if isinstance(group_ids, str):
        group_ids = group_ids.split(",")

    if not group_ids and not filters:
        raise MustProvideFilterOrID

    returned = self.host_group_api.delete_host_groups(
        ids=group_ids if group_ids else self.get_group_ids(filters)
        )["body"]
    if returned["errors"]:
        raise GenericAPIError(returned["errors"])

    return returned["body"]["resources"]


@filter_string
def describe_group_member_ids(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict[str, List[str]]:
    """Return a dictionary with member IDs for all host groups matching the provided filter.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the host group search.

    Returns
    -------
    dict: A dictionary containing details for every host group discovered.
    """
    self.logger.info("Describing host group members according to the filter string %s", filters)
    group_ids = self.get_group_ids(filters)
    group_members = {}
    for group_id in group_ids:
        group_members[group_id] = self.get_group_member_ids(group_id)

    return group_members


@filter_string
def describe_group_members(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict:
    """Return a dictionary with member details for all host groups matching the provided filter.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the host group search.

    Returns
    -------
    dict: A dictionary containing details for every host group discovered.
    """
    self.logger.info("Describing host group members according to the filter string %s", filters)
    return self.get_group_members(filters)


@filter_string
def describe_groups(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict[str, Dict]:
    """Return a dictionary containing detail for every host group matching the provided filter.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the host group search.

    Returns
    -------
    dict: A dictionary containing details for every host group discovered.
    """
    self.logger.info("Describing host groups according to the filter string %s", filters)
    group_ids = self.get_group_ids(filters)
    group_data = batch_get_data(group_ids, self.host_group_api.get_host_groups)

    return group_data


@filter_string
def get_group_ids(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> List[str]:
    """Return a list of IDs (string) for every host group within your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the host group search.

    Returns
    -------
    List[str]: A list of all host group IDs discovered.
    """
    self.logger.info("Searching for host group IDs using the filter string %s", filters)
    func = partial(self.host_group_api.query_host_groups, filter=filters)
    id_list: List[str] = all_pages_numbered_offset_parallel(
        func=func,
        logger=self.logger,
        limit=HOST_GROUP_SCROLL_BATCH_SIZE
    )
    if not id_list:
        raise HostGroupNotFound

    return id_list


def get_group_member_ids(
    self: HostsApiModule,
    group_id: str = None,
) -> List[str]:
    """Return a list of IDs (string) for every host group member for the specified host group.

    Arguments
    ---------
    group_id: str, required
        ID of the host group to return members for.

    Returns
    -------
    List[str]: A list of all host group member IDs discovered.
    """
    self.logger.info("Searching for host group members using the group ID %s", group_id)
    func = partial(self.host_group_api.query_group_members, id=group_id)
    id_list: List[str] = all_pages_numbered_offset_parallel(
        func=func,
        logger=self.logger,
        limit=HOST_GROUP_SCROLL_BATCH_SIZE,
    )

    return id_list


@filter_string
def get_group_members(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
) -> Dict[str, Dict]:
    """Return a dictionary containing every host group and their members.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Filters to apply to the host group member search.

    Returns
    -------
    dict: A dictionary of all host groups and their members discovered.
    """
    groups = self.describe_groups()
    func = partial(self.host_group_api.query_combined_group_members, filter=filters)
    device_data = all_pages_numbered_offset_parallel(func, self.logger)
    all_group_data: Dict[str, Dict] = {}
    for group_id, group_data in groups.items():
        all_group_data[group_id] = group_data
        all_group_data[group_id]['devices'] = []

        for device in device_data:
            if 'groups' not in device:
                continue
            for group_identifier in device['groups']:
                if group_identifier == group_id:
                    all_group_data[group_identifier]['devices'].append(device)

    return all_group_data


def group(
    self: HostsApiModule,
    group_name: str = None,
    description: str = None,
    assignment_rule: str = None,
    device_ids: List[str] = None,
) -> Dict:
    """Group a list of device IDs into a newly created host group within the tenant.

    Arguments
    ---------
    assignment_rule: str, optional - Assignment rule to apply when creating the host group.
    description: str, optional - Description to use for the created host group.
    group_name: str, required - Name of the host group to create.
    device_ids: List[str], required - List of device IDs to add to the newly created group.

    Returns
    -------
    dict: A dictionary containing details for the host group creation result.
    """
    if not description:
        description = "Grouped collection of hosts"
    if not device_ids:
        raise MissingArgument("device_ids")
    new_group = self._create_host_group(
        group_name,
        description,
        "static",
        assignment_rule,
    )[0]["id"]
    return self.add_to_group(group_ids=new_group, device_ids=device_ids)["resources"]


@filter_string
def remove_from_group(
    self: HostsApiModule,
    filters: FalconFilter or str = None,
    group_ids: List[str] or str = None,
    device_filters: FalconFilter or str = None,
    device_ids: List[str] or str = None,
) -> Dict:
    """Remove a host or list of hosts to a host group within your Falcon tenant.

    Arguments
    ---------
    filters: FalconFilter or str, optional
        Group filter to apply to the host group search. Not required if group_ids are provided.
    group_ids: List[str] or str, optional
        List of host group IDs to update. Comma delimited strings are converted.
        Not required if a group filter is provided. Takes precedence over provided filters.
    device_filters: FalconFilter or str, optional
        Filters to apply to the device search. Not required if device_ids are provided.
    device_ids: List[str] or str, optional
        List of device IDs to add to the host group. Comma delimited strings are converted.
        Not required if a device filter is provided. Takes precedence over device filters.

    Returns
    -------
    dict: A dictionary containing details for the host group update result.
    """
    if isinstance(group_ids, str):
        group_ids = group_ids.split(",")

    if not group_ids and not filters:
        raise MustProvideFilterOrID

    if isinstance(device_ids, str):
        device_ids = device_ids.split(",")

    if not device_ids and not device_filters:
        raise MustProvideFilterOrID

    return self._perform_group_action(
        action_name="remove-hosts",
        group_ids=group_ids if group_ids else self.get_group_ids(filters),
        device_ids=device_ids if device_ids else self.get_device_ids(device_filters),
    )["resources"]


def ungroup(
    self: HostsApiModule,
    group_ids: List[str] or str = None,
    remove_groups: bool = False,
) -> Dict[str, Dict]:
    """Remove all members from host groups and then remove the group (if specified).

    Arguments
    ---------
    group_ids: List[str] or str, required - List of host group IDs to ungroup.
    remove_groups: bool, optional - Should host groups be removed after ungrouping.

    Returns
    -------
    dict: A dictionary containing details for the host group update results.
    """
    if not group_ids:
        raise MissingArgument("group_ids")
    returned = {}
    if isinstance(group_ids, str):
        group_ids = group_ids.split(",")
    for group_id in group_ids:
        members = self.get_group_member_ids(group_id)
        returned[group_id] = {}
        returned[group_id]["removed"] = False
        if members:
            returned[group_id]["result"] = self.remove_from_group(
                group_ids=group_id,
                device_ids=members,
            )
            self.logger.info(
                "Removed %d members from group %s",
                len(returned[group_id]["result"]),
                group_id
            )
        if remove_groups:
            self.logger.info("Remove group %s", group_id)
            delete_result = self.delete_group(group_ids=group_id)
            if delete_result:
                returned[group_id]["removed"] = True

    return returned["resources"]


def update_group(
    self: HostsApiModule,
    group_id: str = None,
    group_name: str = None,
    group_description: str = None,
    assignment_rule: str = None,
 ) -> Dict:
    """Update the name, assignment rule or description for a Host Group wihtin your tenant.

    Arguments
    ---------
    assignment_rule: str, optional - Assignment rule to apply when creating the host group.
    description: str, optional - Description to use for the created host group.
    group_name: str, optional - Name of the host group to create.
    group_id: str, required - ID of the host group to be updated.

    Returns
    -------
    dict: A dictionary containing details for the host group creation result.
    """
    if not group_id:
        raise MissingArgument("group_id")
    if not group_name and not assignment_rule and not group_description:
        raise MissingArguments(["group_name", "group_description", "assignment_rule"])

    return self.host_group_api.update_host_groups(
        id=group_id,
        assignment_rule=assignment_rule,
        description=group_description,
        name=group_name
    )["body"]["resources"]
