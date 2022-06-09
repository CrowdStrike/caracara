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
from typing import Dict
from datetime import datetime, timezone
from dateutil import parser as dparser
from caracara import Client
from examples.common import caracara_example


@caracara_example
def find_stale_sensors(**kwargs):
    """Find devices that have not checked in after X number of days."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']
    settings: Dict = kwargs['settings']

    def _get_stale_period(timestamp):
        right_now = dparser.parse(str(datetime.now(timezone.utc)))
        return (right_now - dparser.parse(timestamp)).days

    days = 7 if not settings else int(settings.get('days', 7))
    remove = False if not settings else bool(settings.get("remove", False))
    filters = client.FalconFilter()
    filters.create_new_filter("LastSeen", f"-{days}d", "LTE")

    logger.info("Using the FQL filter: %s", filters.get_fql())
    with client:
        response_data = client.hosts.describe_devices(filters=filters)
        logger.info("Found %d devices", len(response_data.keys()))

        if not remove:
            for device_id, device_data in response_data.items():
                logger.info(
                    "%s",
                    f"[{device_id}] {device_data['hostname']} "
                    f"({_get_stale_period(device_data['last_seen'])} days)"
                    )

            logger.info(f"{len(response_data.items())} devices found.")
        else:
            logger.info("%s sensors hidden.", len(client.hosts.hide(filters)))

if __name__ == '__main__':
    find_stale_sensors()
