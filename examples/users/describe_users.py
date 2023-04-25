#!/usr/bin/env python3
"""
Caracara Examples Collection.

describe_users.py

This example will use the API credentials configured in your config.yml file to
show all the users configured within the Falcon tenant.
"""
import logging

from caracara import Client

from examples.common import caracara_example, pretty_print


@caracara_example
def describe_users(**kwargs):
    """List Users Example."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Describing all users in the Falcon tenant")

    users = client.users.describe_users()
    logger.info(pretty_print(users))


if __name__ == '__main__':
    describe_users()
