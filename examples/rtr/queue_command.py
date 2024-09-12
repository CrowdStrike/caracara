#!/usr/bin/env python3
"""
Caracara Examples Collection.

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

from examples.common import (
    caracara_example,
    parse_filter_list,
    MissingArgument,
    NoDevicesFound,
    NoSessionsConnected,
)


@caracara_example
def queue_command(**kwargs):
    """Run a single RTR command against all hosts matching the filter, even if offline."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]
    settings: Dict = kwargs["settings"]

    if not settings or "command" not in settings:
        error_message = "".join(
            [
                "You must configure the 'cmd' argument within your "
                "YAML file to proceed with this example."
            ]
        )
        logger.critical(error_message)
        raise MissingArgument("cmd", error_message)

    cmd: str = settings["command"]
    logger.info("Running the command: %s", cmd)

    filters = client.FalconFilter(dialect="rtr")
    filter_list: List[Dict] = settings.get("filters")
    parse_filter_list(filter_list, filters)

    logger.info(
        "Getting a list of hosts that match the FQL string %s", filters.get_fql()
    )
    device_ids = client.hosts.get_device_ids(filters=filters)
    if not device_ids:
        logger.warning("No devices matched the filter. Aborting.")
        raise NoDevicesFound(filters.get_fql())

    logger.info("Connecting to %d devices with queueing enabled", len(device_ids))

    batch_session = client.rtr.batch_session()
    batch_session.connect(device_ids=device_ids, queueing=True)

    connected_devices = batch_session.device_ids()
    if not connected_devices:
        logger.warning(
            "No devices successfully connected within %ds. Aborting.",
            batch_session.default_timeout,
        )
        raise NoSessionsConnected

    logger.info("Connected to %d systems", len(connected_devices))

    for device_id, device_result in batch_session.run_generic_command(cmd).items():
        logger.info("[%s] Task queued: %s", device_id, device_result["task_id"])


if __name__ in ["__main__", "examples.rtr.queue_command"]:
    try:
        queue_command()
        print("Command queued for execution across specified hosts.")
        raise SystemExit
    except MissingArgument as no_command:
        raise SystemExit(no_command) from no_command
    except NoDevicesFound as no_devices:
        raise SystemExit(no_devices) from no_devices
    except NoSessionsConnected as no_sessions:
        raise SystemExit(no_sessions) from no_sessions
