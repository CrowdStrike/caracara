"""Falcon Prevention Policies API."""
from functools import partial
from typing import List, Dict

from falconpy import (
    OAuth2,
    PreventionPolicies,
)

from caracara.common.decorators import platform_name_check
from caracara.common.module import FalconApiModule
from caracara.common.pagination import all_pages_numbered_offset_parallel
from caracara.common.policy_wrapper import Policy
from caracara.common.sorting import SORT_ASC, SORTING_OPTIONS
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string
from caracara.modules.prevention_policies.template import generate_prevention_template


class PreventionPoliciesApiModule(FalconApiModule):
    """
    Prevention Policies API module.

    This module provides the logic to interact with the Falcon Prevention Policies API.
    """

    name = "CrowdStrike Prevention Policies API Module"
    help = "Describe, create, delete and edit Falcon Prevention policies"

    def __init__(self, api_authentication: OAuth2):
        """Construct an instance of the PreventionPoliciesApiModule class."""
        super().__init__(api_authentication)
        self.logger.debug("Configuring the FalconPy Prevention Policies API")
        self.prevention_policies_api = PreventionPolicies(auth_object=self.api_authentication)

    @filter_string
    def describe_policies_raw(
        self, filters: str or FalconFilter = None, sort: str = SORT_ASC
    ) -> List[Dict]:
        """Return a list of dictionaries containing all prevention policies in the Falcon tenant."""
        if sort not in SORTING_OPTIONS:
            raise ValueError("Sort must be SORT_ASC or SORT_DESC")

        self.logger.info("Describing all Falcon prevention policies")
        partial_func = partial(
            self.prevention_policies_api.query_combined_policies,
            filters=filters,
            sort=sort,
        )
        resources = all_pages_numbered_offset_parallel(func=partial_func, logger=self.logger)
        self.logger.debug(resources)
        return resources

    @filter_string
    def describe_policies(
        self, filters: str or FalconFilter = None, sort: str = SORT_ASC
    ) -> List[Policy]:
        """Return a list of all prevention policies packaged as custom Python Policy objects."""
        raw_policies_dict = self.describe_policies_raw(filters=filters, sort=sort)
        policies: List[Policy] = []
        for policy_dict in raw_policies_dict:
            policy = Policy(data_dict=policy_dict, style="prevention")
            policies.append(policy)

        return policies

    @platform_name_check
    def new_policy(self, platform_name: str) -> Policy:
        """
        Return a platform-specific prevention policy template ready for customisation.

        To create the policy in the CrowdStrike cloud, use the push_policy function.
        """
        return generate_prevention_template(platform_name=platform_name)

    def push_policy(self, policy: Policy) -> Policy:
        """Push a policy to the CrowdStrike Cloud, and return the resultant policy."""
        self.logger.info("Creating the prevention policy named %s", policy.name)
        response = self.prevention_policies_api.create_policies(body={
            "resources": [
                policy.flat_dump()
            ],
        })['body']
        new_policy = Policy(data_dict=response['resources'][0], style="prevention")
        return new_policy
