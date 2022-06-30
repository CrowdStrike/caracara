#!/usr/bin/env python3
"""Caracara Examples Collection.

list_network_history.py

This example will use the API credentials configured in your config.yml file to
list the network history for systems within your Falcon tenant.

The example demonstrates how to use the Hosts API.
"""
import logging

from typing import Dict, List

from caracara import Client

from examples.common import (
    caracara_example,
    NoDevicesFound,
    Timer,
)


@caracara_example
def list_network_history(**kwargs):
    """List All Devices."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']
    timer: Timer = Timer()

    logger.info("Listing all network address changes within the tenant")

    with client:
        response_data = client.hosts.describe_network_address_history()

    for device_id, device_data in response_data.items():
        recents: List[Dict] = device_data.get("history")
        changes = "No recent changes"
        found = []
        if recents:
            for change in recents:
                change_detail = "".join([
                    f"{change.get('ip_address', 'IP Unknown')} ",
                    f"({change.get('mac_address', 'MAC Unknown')}) on ",
                    f"{change.get('timestamp', 'Unknown')}",
                ])
                if change_detail not in found:
                    found.append(change_detail)
            changes = ", ".join(found)

        logger.info("%s (%s)", device_id, changes)

    logger.info("Found %d devices in %f seconds", len(response_data), float(timer))
    if not response_data:
        raise NoDevicesFound


if __name__ in ["__main__", "examples.hosts.list_network_history"]:
    try:
        list_network_history()
        raise SystemExit
    except NoDevicesFound as no_devices:
        raise SystemExit(no_devices) from no_devices
