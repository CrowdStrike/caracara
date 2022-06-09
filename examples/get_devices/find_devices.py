#!/usr/bin/env python3
r"""Caracara Examples Collection.

find_devices.py

____ _ _  _ ___     ___  ____ _  _ _ ____ ____ ____
|___ | |\ | |  \    |  \ |___ |  | | |    |___ [__
|    | | \| |__/    |__/ |___  \/  | |___ |___ ___]

___  _   _    _  _ ____ ____ ___ _  _ ____ _  _ ____
|__]  \_/     |__| |  | [__   |  |\ | |__| |\/| |___
|__]   |      |  | |__| ___]  |  | \| |  | |  | |___

This example will use the API credentials configured in your config.yml file to
find a specified device within your Falcon tenant. When no search is provided, all
hosts are returned.

The example demonstrates how to use the Hosts API.
"""
import logging

from typing import Dict, List

from caracara import Client

from examples.common import (
    caracara_example,
    parse_filter_list,
    pretty_print,
)


@caracara_example
def find_devices(**kwargs):
    """Find devices by hostname."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']
    settings: Dict = kwargs['settings']

    filters = client.FalconFilter()
    filter_list: List[Dict] = settings.get("filters") if settings else [{}]
    parse_filter_list(filter_list, filters)
    if filters.filters:
        logger.info("Getting a list of hosts that match the FQL string %s", filters.get_fql())
    else:
        logger.info("No filter provided, getting a list of all devices within the tenant")

    response_data = client.hosts.describe_devices(filters)
    logger.info("Found %d devices", len(response_data))

    for _, device_data in response_data.items():
        logger.info("%s", pretty_print(device_data))


if __name__ == '__main__':
    find_devices()
