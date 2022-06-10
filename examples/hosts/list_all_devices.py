#!/usr/bin/env python3
"""Caracara Examples Collection.

list_all_devices.py

This example will use the API credentials configured in your config.yml file to
list the names of all systems within your Falcon tenant.

The example demonstrates how to use the Hosts API.
"""
import logging

from caracara import Client

from examples.common import caracara_example, NoDevicesFound, Timer


@caracara_example
def list_all_devices(**kwargs):
    """List All Devices."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']
    timer: Timer = Timer()

    logger.info("Listing all devices within the tenant")

    with client:
        response_data = client.hosts.describe_devices()

    for device_id, device_data in response_data.items():
        hostname = device_data.get("hostname", "Unknown Hostname")
        logger.info("%s (%s)", device_id, hostname)

    logger.info("Found %d devices in %f seconds", len(response_data), float(timer))
    if not response_data:
        raise NoDevicesFound


if __name__ in ["__main__", "examples.hosts.list_all_devices"]:
    try:
        list_all_devices()
        raise SystemExit
    except NoDevicesFound as no_devices:
        raise SystemExit(no_devices) from no_devices
