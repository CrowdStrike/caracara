#!/usr/bin/env python3
r"""Caracara Examples Collection.

find_stale_sensors.py

____ _ _  _ ___     ____ ___ ____ _    ____    ____ ____ _  _ ____ ____ ____ ____
|___ | |\ | |  \    [__   |  |__| |    |___    [__  |___ |\ | [__  |  | |__/ [__
|    | | \| |__/    ___]  |  |  | |___ |___    ___] |___ | \| ___] |__| |  \ ___]

This example will use the API credentials configured in your config.yml file to
find stale sensors deployments within your Falcon tenant.

The example demonstrates how to use the Hosts API and a FalconFilter using a date.
"""
import logging

from datetime import datetime, timezone
from typing import Dict

from dateutil import parser as dparser

from caracara import Client

from examples.common import (
    caracara_example,
    NoDevicesFound,
    Timer,
)


@caracara_example
def find_stale_sensors(**kwargs):
    """Find devices that have not checked in after X number of days."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']
    settings: Dict = kwargs['settings']
    timer: Timer = Timer()

    days = 7
    remove = False
    if settings:
        days = int(settings.get('days', days))
        remove = bool(settings.get("remove", remove))

    filters = client.FalconFilter()
    filters.create_new_filter("LastSeen", f"-{days}d", "LTE")

    logger.info("Using the FQL filter: %s", filters.get_fql())
    with client:
        response_data = client.hosts.describe_devices(filters=filters)
        if not response_data:
            raise NoDevicesFound(filters.get_fql())

        if remove:
            remove_result = client.hosts.hide(filters)
            logger.info(
                "%d sensors hidden in %f seconds.",
                len(remove_result),
                float(timer),
            )

        time_now = datetime.now(timezone.utc)

        for device_id, device_data in response_data.items():
            last_seen = dparser.isoparse(device_data['last_seen'])
            last_seen_days = (time_now - last_seen).days
            logger.info(
                "[%s] %s was last seen %d days ago",
                device_id,
                device_data['hostname'],
                last_seen_days,
            )

        logger.info("%d devices found in %f seconds.", len(response_data), float(timer))


if __name__ in ["__main__", "examples.hosts.find_stale_sensors"]:
    try:
        find_stale_sensors()
        raise SystemExit
    except NoDevicesFound as no_devices:
        raise SystemExit(no_devices) from no_devices
