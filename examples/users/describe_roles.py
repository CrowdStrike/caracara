#!/usr/bin/env python3
"""
Caracara Examples Collection.

describe_roles.py

This example will use the API credentials configured in your config.yml file to
show all the possible roles that may be assigned to users in the Falcon tenant.
"""
import logging

from caracara import Client
from examples.common import caracara_example, pretty_print


@caracara_example
def describe_roles(**kwargs):
    """List Roles Example."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]

    logger.info("Describing all possible roles in the Falcon tenant")
    available_role_info = client.users.describe_available_roles()
    logger.info(pretty_print(available_role_info))


if __name__ == "__main__":
    describe_roles()
