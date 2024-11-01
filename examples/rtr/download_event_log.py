#!/usr/bin/env python3
"""
Caracara Example Collection.

download_event_log.py

This example will use the API credentials configuration in your config.yml file to
download an event log from every system that matches the filters you provide
in the configuration file.
The files will be downloaded, extracted from the 7-Zip container (password: infected)
and renamed according to their respective origin device IDs and SHA256 hashes.

Configuration Example
download_event_log:
  # How long to wait between attempts for the file to upload to Falcon
  attempt_delay: 30
  # Maximum number of attempts to retrieve files from Falcon
  attempt_limit: 10
  # Log filename
  filename: System.evtx
  # # Which machines to upload logs from
  filters:
    - OS: Windows
  # Output folder on disk to download the logs to
  output_folder: /tmp/logs
"""
import logging
import os
import time
from typing import Dict, List

from caracara import Client
from caracara.modules.rtr.batch_session import BatchGetCmdRequest, RTRBatchSession
from caracara.modules.rtr.get_file import GetFile
from examples.common import caracara_example, parse_filter_list


def download_loop(
    batch_get_cmd_reqs: List[BatchGetCmdRequest],
    batch_session: RTRBatchSession,
    settings: Dict,
    logger: logging.Logger,
):
    """
    File download loop.

    Keeps checking how many files have finished uploading to the CrowdStrike Cloud,
    decides when to download, and then carries out the downloads.
    """
    attempt_delay: int = settings.get("attempt_delay", 30)
    attempt_limit: int = settings.get("attempt_limit", 10)
    output_folder: str = settings["output_folder"]

    devices = list(x.devices.keys() for x in batch_get_cmd_reqs)

    current_attempt = 0
    uploads_complete = False
    expected_uploads = len(devices)

    get_files: List[GetFile] = []
    while not uploads_complete and current_attempt < attempt_limit:
        current_attempt += 1
        logger.info("Download attempt %d of %d", current_attempt, attempt_limit)

        logger.info("Waiting %ds before checking for upload completion", attempt_delay)
        time.sleep(attempt_delay)

        get_files = batch_session.get_status(batch_get_cmd_reqs)
        if len(get_files) >= expected_uploads:
            uploads_complete = True

        logger.info("%d systems have finished uploading the log file", len(get_files))
        logger.debug(get_files)

    logger.info(f"Downloading log files from {len(get_files)} systems")
    for get_file in get_files:
        get_file.download(output_path=output_folder, extract=True, preserve_7z=False)


@caracara_example
def download_event_log(**kwargs):  # pylint: disable=too-many-locals
    """Download a specified Windows Event Log from all online systems."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]
    settings: Dict = kwargs["settings"]

    filename: str = settings.get("filename")
    if not filename:
        logger.critical("Event log filename not provided. Aborting.")
        return

    output_folder: str = settings.get("output_folder")
    if not output_folder:
        logger.critical("Output folder not provided. Aborting.")
        return

    if not os.path.isdir(output_folder):
        logger.critical("Output folder not valid. Aborting.")
        return

    logger.info("Downloading the event log %s", filename)

    filters = client.FalconFilter(dialect="hosts")
    filter_list: List[Dict] = settings.get("filters")

    # This is a custom generic function to load filters from the config file. You can
    # inspect what it does to see how one might use the create_new_filter_from_kv_string
    # function contained within the FalconFilter class.
    parse_filter_list(filter_list, filters)

    logger.info("Getting a list of hosts that match the FQL string %s", filters.get_fql())
    device_ids = client.hosts.get_device_ids(filters=filters)
    if not device_ids:
        logger.warning("No devices matched the filter. Aborting.")
        return

    logger.info("Connecting to %d devices", len(device_ids))

    batch_session = client.rtr.batch_session()
    batch_session.connect(device_ids=device_ids)

    if not batch_session.batch_sessions:
        logger.warning(
            "No devices successfully connected within %ds. Aborting.",
            batch_session.default_timeout,
        )
        return

    log_file_path = f"C:\\Windows\\System32\\winevt\\Logs\\{filename}"
    logger.info("Requesting the file %s", log_file_path)
    batch_get_cmd_reqs: List[BatchGetCmdRequest] = batch_session.get(log_file_path)
    batch_get_cmd_req_ids = list(x.batch_get_cmd_req_id for x in batch_get_cmd_reqs)
    devices = list(x.devices.keys() for x in batch_get_cmd_reqs)
    logger.info(
        "%d batch get requests executed successfully against %d systems",
        len(batch_get_cmd_reqs),
        len(devices),
    )
    logger.info(batch_get_cmd_req_ids)
    logger.debug(devices)

    download_loop(
        batch_get_cmd_reqs=batch_get_cmd_reqs,
        batch_session=batch_session,
        settings=settings,
        logger=logger,
    )


if __name__ == "__main__":
    download_event_log()
