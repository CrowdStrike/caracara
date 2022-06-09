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

from examples.common import caracara_example, NoDevicesFound


@caracara_example
def list_windows_devices(**kwargs):
    """List Windows Devices."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Grabbing all Windows devices within the tenant")

    filters = client.FalconFilter()
    filters.create_new_filter("OS", "Windows")
    logger.info("Using the FQL filter: %s", filters.get_fql())

    response_data = client.hosts.describe_devices(filters)
    logger.info("Found %d devices running Windows", len(response_data))

    if not response_data:
        raise NoDevicesFound(filters.get_fql())

    for device_id, device_data in response_data.items():
        hostname = device_data.get("hostname", "Unknown Hostname")
        logger.info("%s (%s)", device_id, hostname)


if __name__ in ["__main__", "examples.hosts.list_windows_devices"]:
    try:
        list_windows_devices()
        raise SystemExit
    except NoDevicesFound as no_devices:
        raise SystemExit(no_devices) from no_devices
