#!/usr/bin/env python3
"""
Caracara Examples Collection
queue_command.py

This example will use the API credentials configuration in your config.yml file to
run a command defined in the config.yml with queueing enabled.
This shows how one can set up a batch session and execute a command against
all those hosts, regardless of whether they are online or not.

Configuration
queue_command:
  filters:
    - Filter1Name__Operator: Filter1Value
    - Filter2Name__Operator: Filter2Value
  command: CommandToRun
"""
import logging

from typing import Dict, List

from caracara import Client

from examples.common import caracara_example, parse_filter_list, pretty_print


@caracara_example
def queue_command(**kwargs):
    """Run a single RTR command against all hosts matching the filter, even if offline"""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']
    settings: Dict = kwargs['settings']

    cmd = settings.get("command")
    if not cmd:
        logger.critical("No command argument provided. Aborting.")
        return

    logger.info("Running the command: %s", cmd)

    filters = client.FalconFilter()
    filter_list: List[Dict] = settings.get("filters")
    parse_filter_list(filter_list, filters)

    logger.info("Getting a list of hosts that match the FQL string %s", filters.get_fql())
    device_ids = client.hosts.get_device_ids(filters=filters)
    if not device_ids:
        logger.warning("No devices matched the filter. Aborting.")
        return

    logger.info("Connecting to %d devices with queueing enabled", len(device_ids))

    batch_session = client.rtr.batch_session()
    batch_session.connect(device_ids=device_ids, queueing=True)

    connected_devices = batch_session.device_ids()

    if not connected_devices:
        logger.warning(
            "No devices successfully connected within %ds. Aborting.",
            batch_session.default_timeout,
        )
        return

    logger.info("Connected to %d systems", len(connected_devices))

    result = batch_session.run_generic_command(cmd)
    pretty_print(data=result, rewrite_new_lines=True)


queue_command()
