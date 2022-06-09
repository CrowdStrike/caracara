#!/usr/bin/env python3
r"""Caracara Examples Collection.

show_agent_versions.py

____ _  _ ____ _ _ _    ____ ____ ____ _  _ ___    _  _ ____ ____ ____ _ ____ _  _ ____
[__  |__| |  | | | |    |__| | __ |___ |\ |  |     |  | |___ |__/ [__  | |  | |\ | [__
___] |  | |__| |_|_|    |  | |__] |___ | \|  |      \/  |___ |  \ ___] | |__| | \| ___]

This example will use the API credentials configured in your config.yml file to
find a specified device within your Falcon tenant. Devices are then displayed in a
scrolling tabular format listing Device ID, Hostname, IP addresses and agent version.

The example demonstrates how to use the Hosts API and the Client context.
"""
import logging

from tabulate import tabulate

from caracara import Client

from examples.common import caracara_example, NoDevicesFound


@caracara_example
def show_agent_versions(**kwargs):
    """List all devices and agent versions."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Grabbing all devices within the tenant")

    # Display these data elements in our results table
    elements = {
        "device_id": "ID",
        "hostname": "Hostname",
        "local_ip": "Internal IP",
        "external_ip": "External IP",
        "agent_version": "Agent Version"
    }
    devices = []
    with client:
        for device in client.hosts.describe_devices().values():
            devices.append({itm: device.get(itm, "Unavailable") for itm in elements})

    # Display a scrollable table containing our results
    logger.info("\n%s", tabulate(devices, headers=elements, tablefmt="simple"))
    # Report our total found
    logger.info("Found %d devices", len(devices))
    if not devices:
        raise NoDevicesFound


if __name__ in ["__main__", "examples.hosts.show_agent_versions"]:
    try:
        show_agent_versions()
        raise SystemExit
    except NoDevicesFound as no_devices:
        raise SystemExit(no_devices) from no_devices
