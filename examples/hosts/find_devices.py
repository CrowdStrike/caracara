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
    NoDevicesFound,
    Timer,
)


@caracara_example
def find_devices(**kwargs):
    """Find devices by hostname."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']
    settings: Dict = kwargs['settings']
    timer: Timer = Timer()

    filters = client.FalconFilter(dialect='hosts')
    if 'filters' in settings:
        filter_list: List[Dict] = settings['filters']
        parse_filter_list(filter_list, filters)

    if filters.filters:
        logger.info("Getting a list of hosts that match the FQL string %s", filters.get_fql())
    else:
        logger.info("No filter provided; getting a list of all devices within the tenant")

    with client:
        response_data = client.hosts.describe_devices(filters)

    for device_data in response_data.values():
        logger.info("%s", pretty_print(device_data))

    logger.info("Found %d devices in %f seconds", len(response_data), float(timer))
    if not response_data:
        raise NoDevicesFound(filters.get_fql())


if __name__ in ["__main__", "examples.hosts.find_devices"]:
    try:
        find_devices()
        raise SystemExit
    except NoDevicesFound as no_devices:
        raise SystemExit(no_devices) from no_devices
