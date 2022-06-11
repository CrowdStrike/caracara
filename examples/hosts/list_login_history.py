#!/usr/bin/env python3
"""Caracara Examples Collection.

list_login_history.py

This example will use the API credentials configured in your config.yml file to
list the login history for systems within your Falcon tenant.

The example demonstrates how to use the Hosts API.
"""
import logging

from typing import Dict, List

from caracara import Client

from examples.common import (
    caracara_example,
    NoDevicesFound,
    NoLoginsFound,
    Timer,
)


@caracara_example
def list_login_history(**kwargs):
    """List All Devices."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']
    timer: Timer = Timer()

    logger.info("Listing login history for all devices within the tenant")

    with client:
        response_data = client.hosts.describe_login_history()

    for device_id, device_data in response_data.items():
        recents: List[Dict] = device_data.get('recent_logins')
        if recents:
            found = []
            for login in recents:
                login_detail = "".join([
                    f"{login.get('user_name', 'Username not found')}: ",
                    f"{login.get('login_time', 'Unknown')}",
                ])
                if login_detail not in found:
                    found.append(login_detail)

            logins = ", ".join(found)
        else:
            logins = "No logins found"

        logger.info("%s (%s)", device_id, logins)

    logger.info("Found %d devices in %f seconds", len(response_data), float(timer))
    if not response_data:
        raise NoDevicesFound
    if not found:
        raise NoLoginsFound


if __name__ in ["__main__", "examples.hosts.list_login_history"]:
    try:
        list_login_history()
        raise SystemExit
    except NoDevicesFound as no_devices:
        raise SystemExit(no_devices) from no_devices
    except NoLoginsFound as no_logins:
        raise SystemExit(no_logins) from no_logins
