#!/usr/bin/env python3
"""
Caracara Examples Collection.

list_windows_devices.py

This example will use the API credentials configured in your config.yml file to
list the names of all systems within your Falcon tenant that run Windows.

The example demonstrates how to use the FalconFilter() class and the Hosts API.
"""
import logging

from caracara import Client
from examples.common import NoDevicesFound, Timer, caracara_example


@caracara_example
def list_windows_devices(**kwargs):
    """List Windows Devices."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]
    timer: Timer = Timer()

    logger.info("Grabbing all Windows devices within the tenant")

    filters = client.FalconFilter(dialect="hosts")
    filters.create_new_filter("OS", "Windows")
    logger.info("Using the FQL filter: %s", filters.get_fql())

    response_data = client.hosts.describe_devices(filters)

    if not response_data:
        raise NoDevicesFound(filters.get_fql())

    for device_id, device_data in response_data.items():
        hostname = device_data.get("hostname", "Unknown Hostname")
        logger.info("%s (%s)", device_id, hostname)

    logger.info(
        "Found %d devices running Windows in %s seconds",
        len(response_data),
        float(timer),
    )


if __name__ in ["__main__", "examples.hosts.list_windows_devices"]:
    try:
        list_windows_devices()
        raise SystemExit
    except NoDevicesFound as no_devices:
        raise SystemExit(no_devices) from no_devices
