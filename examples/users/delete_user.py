#!/usr/bin/env python3
"""
Caracara Examples Collection.

delete_user.py

This example will use the API credentials configured in your config.yml file to
delete a user in the Falcon tenant.
"""
import logging

from caracara import Client
from examples.common import caracara_example, pretty_print


@caracara_example
def delete_user(uuid, **kwargs):
    """Delete Users Example."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]

    logger.info("Deleting a user in the Falcon tenant")
    deleted_user_data = client.users.add_user(uuid)
    logger.info(pretty_print(deleted_user_data))


@caracara_example
def get_uuid(email_address, **kwargs):
    """Get UUID for Delete Users Example."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]

    logger.info("Retrieving UUID for a user in the Falcon tenant")
    uuid_data = client.users.get_uuid_by_email(email_address)
    return uuid_data


if __name__ == "__main__":
    # delete_user requires a uuid, a string of characters
    # you can find this via get_uuid_by_email (from caracara) if needed
    EMAIL = "sample_email"
    fetched_uuid = get_uuid(EMAIL)
    delete_user(fetched_uuid)
