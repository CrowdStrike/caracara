"""Caracara Indicator of Attack (IOA) API module."""
from functools import partial
from typing import Dict, List

from falconpy import OAuth2, CustomIOA

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
    def describe_ioa_rule_groups_raw(
        self, filters: str or FalconFilter = None, sort: str = "name.asc"
    ) -> List[Dict]:
        """Return a list of all IOA Rule Groups, as a list of dictionaries returned directly by the
        API, optionally filtered with FQL as `str` or `FalconFilter`"""
        self.logger.info("Describing all Falcon IOA Rule Groups matching filter: %s", repr(filters))
        partial_func = partial(
            self.custom_ioa_api.query_rule_groups_full,
            filter=filters,
            sort=sort,
        )
        resources = all_pages_numbered_offset_parallel(func=partial_func, logger=self.logger)
        self.logger.debug(resources)
        return resources

    @ filter_string
    def describe_ioa_rule_groups(
        self, filters: str or FalconFilter = None, sort: str = "name.asc"
    ) -> List[IoaRuleGroup]:
        """Return a list of all IOA Rule Groups, as a list of `IoaRuleGroup` objects, optionally
        filtered with FQL as `str` or `FalconFilter`"""
        raw_policies_dict = self.describe_ioa_rule_groups_raw(filters=filters, sort=sort)
        groups: List[IoaRuleGroup] = []
        for policy_dict in raw_policies_dict:
            group = IoaRuleGroup(data_dict=policy_dict)
            groups.append(group)

        return groups
