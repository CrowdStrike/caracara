"""Falcon Users API."""
from functools import partial
from typing import Dict, List

from falconpy import (
    OAuth2,
    UserManagement,
)

from caracara.common.batching import batch_get_data
from caracara.common.module import FalconApiModule
from caracara.common.pagination import (
    all_pages_numbered_offset_parallel,
    generic_parallel_list_execution,
)
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string


class UsersApiModule(FalconApiModule):
    """
    Users API module.

    This module provides the logic to interact with the Falcon User Management
    APIs. With the functions provided herein, one can list and create users, and
    assign access roles.
    """

    name = "CrowdStrike User Management API Module"
    help = "Describe, create, delete and edit users in a Falcon tenant"

    def __init__(self, api_authentication: OAuth2):
        """Construct an instance of the UsersApiModule class."""
        super().__init__(api_authentication)
        self.logger.debug("Configuring the FalconPy User Management API")
        self.user_management_api = UserManagement(auth_object=self.api_authentication)

    @filter_string
    def get_user_uuids(self, filters: FalconFilter or str = None) -> List[str]:
        """Get a list of IDs of users (UUIDs) configured in the Falcon tenant."""
        self.logger.info("Obtaining a list of all users in the Falcon tenant")

        query_users_func = partial(self.user_management_api.query_users, filter=filters)
        user_uuids: List[str] = all_pages_numbered_offset_parallel(
            query_users_func,
            self.logger,
            500,
        )
        return user_uuids

    def get_user_data(self, user_uuids: List[str]) -> Dict[str, Dict]:
        """Fetch a dictionary of data for each of the User IDs (UUIDs) passed into the function."""
        self.logger.info("Obtaining data for the %d User IDs provided", len(user_uuids))

        user_data: Dict[str, Dict] = batch_get_data(
            user_uuids,
            self.user_management_api.retrieve_users,
        )
        return user_data

    @filter_string
    def describe_users(self, filters: FalconFilter or str = None) -> Dict[str, Dict]:
        """Describe the users in a Falcon tenant."""
        self.logger.info("Describing users")

        user_uuids = self.get_user_uuids(filters=filters)
        user_data = self.get_user_data(user_uuids)
        user_roles = self.get_assigned_user_roles(user_uuids)

        # Set up an empty set to contain all roles assigned to each user
        for user_data_dict in user_data.values():
            user_data_dict['roles'] = set()

        # Iterate over all roles in the CID and add them to each user's role set
        for user_role in user_roles:
            if user_role['uuid'] in user_data:
                user_data[user_role['uuid']]['roles'].add(user_role['role_id'])

        # Convert the sets to sorted list objects so that they can be JSON serialised
        for user_data_dict in user_data.values():
            user_data_dict['roles'] = sorted(list(user_data_dict['roles']))

        return user_data

    def get_available_role_ids(self) -> List[str]:
        """Obtain a list of role IDs enabled on the Falcon tenant."""
        self.logger.info("Fetching a list of role IDs")

        # Endpoint does not support offsets, so we do not need to parallelise here
        role_ids: List[str] = self.user_management_api.get_available_role_ids()['body']['resources']
        return role_ids

    def get_role_information(self, role_ids: List[str]) -> Dict[str, Dict]:
        """Fetch a dictionary describing each of the Role IDs passed into the function."""
        self.logger.info("Getting information on the %d role IDs provided", len(role_ids))

        role_info: Dict[str, Dict] = batch_get_data(
            role_ids,
            self.user_management_api.get_roles_mssp,
        )
        return role_info

    def describe_available_roles(self) -> Dict[str, Dict]:
        """Describe the roles that are available within the current Falcon tenant."""
        self.logger.info("Describing available roles")

        role_ids = self.get_available_role_ids()
        role_info = self.get_role_information(role_ids)
        return role_info

    def get_assigned_user_roles(self, user_uuids: List[str]) -> Dict[str, Dict]:
        """Retrieve a list of roles assigned to a list of User UUIDs."""
        self.logger.info("Retrieving roles for %d User IDs", len(user_uuids))

        get_user_grants_func = partial(
            self.user_management_api.get_user_grants,
            direct_only=False,
            sort="cid",
        )
        user_roles = generic_parallel_list_execution(
            get_user_grants_func,
            logger=self.logger,
            param_name="user_uuid",
            value_list=user_uuids,
        )
        return user_roles
