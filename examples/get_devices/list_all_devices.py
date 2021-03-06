#!/usr/bin/env python3
"""
Caracara Examples Collection.

list_all_devices.py

This example will use the API credentials configured in your config.yml file to
list the names of all systems within your Falcon tenant.

The example demonstrates how to use the Hosts API.
"""
import logging

from caracara import Client

from examples.common import caracara_example


@caracara_example
def list_all_devices(**kwargs):
    """List All Devices."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Listing all devices within the tenant")

    response_data = client.hosts.describe_devices()
    logger.info("Found %d devices", len(response_data))

    for device_id, device_data in response_data.items():
        hostname = device_data.get("hostname", "Unknown Hostname")
        logger.info("%s (%s)", device_id, hostname)


if __name__ == '__main__':
    list_all_devices()
