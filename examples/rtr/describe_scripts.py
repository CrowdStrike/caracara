#!/usr/bin/env python3
"""
Caracara Examples Collection.

describe_scripts.py

This example will use the API credentials configuration in your config.yml file to
list all the scripts that are stored in the associated Falcon tenant
"""
import logging

from caracara import Client
from examples.common import caracara_example, pretty_print


@caracara_example
def describe_scripts(**kwargs):
    """Describe all available cloud scripts and and write the output to the log."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]

    with client:
        logger.info("Listing available PUT files")
        for script_id, script_data in client.rtr.describe_scripts().items():
            logger.info("%s\n%s", script_id, pretty_print(script_data))


if __name__ == "__main__":
    describe_scripts()
