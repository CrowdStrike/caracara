"""Falcon Response Policies API."""
from functools import partial
from typing import Dict, List

from falconpy import (
    OAuth2,
    ResponsePolicies,
)

from caracara.common.decorators import platform_name_check
from caracara.common.module import FalconApiModule
from caracara.common.pagination import all_pages_numbered_offset_parallel
from caracara.common.policy_wrapper import Policy
from caracara.common.sorting import SORT_ASC, SORTING_OPTIONS
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string
from caracara.modules.response_policies.template import generate_response_template


class ResponsePoliciesApiModule(FalconApiModule):
    """
    Response Policies API module.

    This module provides the logic to interact with the Falcon Response Policies API.
    """

    name = "CrowdStrike Response Policies API Module"
    help = "Describe, create, delete and edit Falcon Response policies"

    def __init__(self, api_authentication: OAuth2):
        """Construct an instance of the ResponsePoliciesApiModule class."""
        super().__init__(api_authentication)
        self.logger.debug("Configuring the FalconPy Response Policies API")
        self.response_policies_api = ResponsePolicies(auth_object=self.api_authentication)

    @filter_string
    def describe_policies_raw(
        self, filters: str or FalconFilter = None, sort: str = SORT_ASC
    ) -> List[Dict]:
        """Return a list of dictionaries containing all response policies in the Falcon tenant."""
        if sort not in SORTING_OPTIONS:
            raise ValueError("Sort must be SORT_ASC or SORT_DESC")

        self.logger.info("Describing all Falcon Response policies")
        partial_func = partial(
            self.response_policies_api.query_combined_policies,
            filter=filters,
            sort=sort,
        )
        resources = all_pages_numbered_offset_parallel(func=partial_func, logger=self.logger)
        self.logger.debug(resources)
        return resources

    @filter_string
    def describe_policies(
        self, filters: str or FalconFilter = None, sort: str = SORT_ASC
    ) -> List[Policy]:
        """Return a list of all response policies packaged as custom Python Policy objects."""
        raw_policies_dict = self.describe_policies_raw(filters=filters, sort=sort)
        policies: List[Policy] = []
        for policy_dict in raw_policies_dict:
            policy = Policy(data_dict=policy_dict, style="response")
            policies.append(policy)

        return policies

    @platform_name_check
    def new_policy(self, platform_name: str) -> Policy:  # pylint: disable=R0201
        """
        Return a platform-specific response policy template ready for customisation.

        To create the policy in the CrowdStrike cloud, use the push_policy function.
        """
        # We disable pylint rule R0201 as the decorator existence means that this function
        # cannot be a @staticmethod. The decorator expects the self parameter.
        return generate_response_template(platform_name=platform_name)

    def push_policy(self, policy: Policy) -> Policy:
        """Push a policy to the CrowdStrike Cloud, and return the resultant policy."""
        self.logger.info("Creating the response policy named %s", policy.name)
        response = self.response_policies_api.create_policies(body={
            "resources": [
                policy.flat_dump()
            ],
        })['body']
        new_policy = Policy(data_dict=response['resources'][0], style="response")
        return new_policy

    def add_policy_to_group(self, policy: Policy or str, group: str) -> Policy:
        """
        Add a policy to a group.

        Takes a policy object or policy ID and a group object or group ID as parameters.
        """
        if isinstance(policy, Policy):
            policy_id = policy.policy_id
        else:
            policy_id = policy

        # Eventually we will likely have support for host group objects and handle them here
        group_id = group

        action_parameters = [
            {
                "name": "group_id",
                "value": group_id,
            }
        ]

        self.response_policies_api.perform_policies_action(
            action_name="add-host-group",
            action_parameters=action_parameters,
            ids=[policy_id],
        )

        updated_policy_dict = self.response_policies_api.query_combined_policies(
            filter=f"id: '{policy_id}'",
        )['body']['resources'][0]

        new_policy = Policy(data_dict=updated_policy_dict, style="response")
        return new_policy

    def modify_policy(self, policy: Policy) -> Policy:
        """
        Modify a pre-existent policy in the CrowdStrike Cloud.

        Accepts a Policy object and patches the policy in the CrowdStrike Cloud to match
        the configuration of the passed Policy object.
        """
        if policy.policy_id is None:
            raise Exception(
                "You must supply a policy containing an ID. To retrieve a complete policy,"
                "use the describe_policies function"
            )

        self.logger.info("Updating the response policy named %s", policy.name)
        response = self.response_policies_api.update_policies(body={
            "resources": [
                policy.flat_dump()
            ],
        })['body']['resources'][0]
        new_policy = Policy(data_dict=response, style="response")
        return new_policy
