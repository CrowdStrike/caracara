#!/usr/bin/env python3
"""
Caracara Examples Collection.

add_user.py

This example will use the API credentials configured in your config.yml file to
add a user in the Falcon tenant.
"""
import logging

from caracara import Client
from examples.common import caracara_example, pretty_print


@caracara_example
def add_user(first_name, last_name, email_address, **kwargs):
    """Add User Example."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]

    logger.info("Adding a user in the Falcon tenant")
    new_user_data = client.users.add_user(first_name, last_name, email_address)
    logger.info(pretty_print(new_user_data))


if __name__ == "__main__":
    FIRST_NAME = "sampleName"
    LAST_NAME = "sampleLastName"
    EMAIL_ADDRESS = "sample.email@example.com"
    add_user(FIRST_NAME, LAST_NAME, EMAIL_ADDRESS)
