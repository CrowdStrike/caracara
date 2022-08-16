"""Caracara Indicator of Attack (IOA) API module."""
from functools import partial
from typing import Dict, List, Optional

from falconpy import OAuth2, CustomIOA

from caracara.common.batching import batch_get_data
from caracara.common.pagination import all_pages_numbered_offset_parallel
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string
from caracara.common.module import FalconApiModule
from caracara.modules.custom_ioa.ioa_wrapper import IoaRuleGroup


class CustomIoaApiModule(FalconApiModule):
    """Caracara Custom Indicator of Attack (IOA) API module."""

    name = "CrowdStrike Custom IOA Module"
    help = "Interact with Custom IOA Rules and IOA Rule Groups within your Falcon tenant."

    def __init__(self, api_authentication: OAuth2):
        """Create an Custom IOA API object and configure it with a FalconPy OAuth2 object."""
        super().__init__(api_authentication)
        self.custom_ioa_api = CustomIOA(auth_object=api_authentication)

    @filter_string
    def describe_rule_groups_raw(self, filters: str or FalconFilter = None) -> Dict[str, dict]:
        """Return all IOA Rule Groups as raw dicts returned from the API, optionally filtered.

        Arguments
        ---------
        `filters`: `FalconFilter` or `str`, optional
            Filters to apply to IOA rule group search

        Returns
        -------
        `Dict[str, IoaRuleGroup]`:
            Dictionary mapping ID to IOA rule group as a raw dict for all the rule groups that match
            the filter.
        """
        self.logger.info("Describing all Falcon IOA Rule Groups matching filter: %s", repr(filters))
        partial_func = partial(
            self.custom_ioa_api.query_rule_groups_full,
            filter=filters,
        )
        resources = all_pages_numbered_offset_parallel(func=partial_func, logger=self.logger)
        self.logger.debug(resources)
        result = {}
        for rule_group in resources:
            result[rule_group["id"]] = rule_group
        return result

    @filter_string
    def describe_rule_groups(self, filters: str or FalconFilter = None) -> Dict[str, IoaRuleGroup]:
        """Return all IOA Rule Groups, optionally filtered.

        Arguments
        ---------
        `filters`: `FalconFilter` or `str`, optional
            Filters to apply to IOA rule group search

        Returns
        -------
        `Dict[str, IoaRuleGroup]`:
            Dictionary mapping ID to IoaRuleGroup for all the rule groups that match the filter.
        """
        raw_groups = self.describe_rule_groups_raw(filters=filters)
        groups = {}
        for (group_id, raw_group) in raw_groups.items():
            groups[group_id] = IoaRuleGroup(data_dict=raw_group)
        return groups

    @filter_string
    def get_rule_group_ids(
        self, filters: str or FalconFilter = None, sort: str = "name.asc"
    ) -> List[str]:
        """Return a list off IOA rule group IDs, optionally filtered.

        Arguments
        ---------
        `filters`: `FalconFilter` or `str`, optional
            Filters to apply to the search
        `sort`: `str`
            Sorting order, default: `"name.asc"`

        Returns
        -------
        `List[str]`: list of IOA rule group IDs
        """
        self.logger.info("Searching for IOA rule group IDs using the filter string %s", filters)
        func = partial(self.custom_ioa_api.query_rule_groups, filter=filters, sort=sort)
        id_list: List[str] = all_pages_numbered_offset_parallel(func=func, logger=self.logger)
        return id_list

    def get_rule_groups_raw(self, rule_group_ids: List[str]) -> Dict[str, Optional[dict]]:
        """Returns a dictionary with pairs (ID, raw IOA rule group dictionary) for each ID provided

        Arguments
        ---------
        `ids`: `List[str]`
            List of IOA rule group IDs to fetch

        Returns
        -------
        `Dict[str, dict]`:
            Dictionary mapping an ID to the IOA rule group associated with it, if it exists, None
            otherwise
        """
        self.logger.info("Obtaining data for %s IOA rule groups", len(rule_group_ids))
        device_data = batch_get_data(rule_group_ids, self.custom_ioa_api.get_rule_groups)
        return device_data
