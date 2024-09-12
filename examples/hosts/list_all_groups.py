#!/usr/bin/env python3
"""Caracara Examples Collection.

list_all_groups.py

This example will use the API credentials configured in your config.yml file to
list the IDs and names of all host groups within your Falcon tenant.

The example demonstrates how to use the Hosts API.
"""
import logging

from caracara import Client

from examples.common import (
    caracara_example,
    NoGroupsFound,
    Timer,
)


@caracara_example
def list_all_groups(**kwargs):
    """List All Host Groups."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]
    timer: Timer = Timer()

    logger.info("Listing all host groups within the tenant")

    with client:
        response_data = client.hosts.describe_groups()
        for group_id, group_data in response_data.items():
            groupname = group_data.get("name", "Unnamed")
            logger.info("%s (%s)", group_id, groupname)

        logger.info("Found %d groups in %f seconds", len(response_data), float(timer))
        if not response_data:
            raise NoGroupsFound


if __name__ in ["__main__", "examples.hosts.list_all_groups"]:
    try:
        list_all_groups()
        raise SystemExit
    except NoGroupsFound as no_groups:
        raise SystemExit(no_groups) from no_groups
