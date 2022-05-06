#!/usr/bin/env python3
"""
Caracara Examples Collection
list_windows_devices.py

This example will use the API credentials configured in your config.yml file to
list the names of all systems within your Falcon tenant that run Windows.

The example demonstrates how to use the FalconFilter() class and the Hosts API.
"""
import logging

from caracara import Client

from examples.common import caracara_example


@caracara_example
def list_windows_devices(**kwargs):
    """List Windows Devices Example"""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Grabbing all Windows devices within the tenant")

    filters = client.FalconFilter()
    filters.create_new_filter("OS", "Windows")
    logger.info("Using the FQL filter: %s", filters.get_fql())

    response_data = client.hosts.describe_devices(filters)
    logger.info("Found %d devices running Windows", len(response_data.keys()))

    for device_id, device_data in response_data.items():
        hostname = device_data.get("hostname", "Unknown Hostname")
        logger.info("%s (%s)", device_id, hostname)

    logger.info("Done!")


if __name__ == '__main__':
    list_windows_devices()
