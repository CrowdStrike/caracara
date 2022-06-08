#!/usr/bin/env python3
"""
Caracara Examples Collection.

find_devices.py

This example will use the API credentials configured in your config.yml file to
find a specified device within your Falcon tenant. When no search is provide, all
hosts are returned.

The example demonstrates how to use the Hosts API.
"""
import logging
from argparse import ArgumentParser
import json
from caracara import Client

from examples.common import caracara_example


@caracara_example
def find_devices(**kwargs):
    """Find devices by hostname."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']
    target: str = kwargs.get("target", None)

    filters = None
    if target:
        logger.info("Searching tenant for %s", target)
        filters = client.FalconFilter()
        filters.create_new_filter("Hostname", target)
        logger.info("Using the FQL filter: %s", filters.get_fql())
    else:
        logger.info("Grabbing all devices within the tenant")

    response_data = client.hosts.describe_devices(filters)
    logger.info("Found %d devices", len(response_data.keys()))

    for _, device_data in response_data.items():
        logger.info("%s", json.dumps(device_data, indent=4))

    logger.info(f"{len(response_data.items())} devices found.")


if __name__ == '__main__':
    parser = ArgumentParser(description="Search for a device within your Falcon tenant")
    parser.add_argument("-f", "--find",
                        help="String to match against a device hostname within your tenant",
                        required=False,
                        default=None
                        )
    find_devices(target=parser.parse_args().find)
