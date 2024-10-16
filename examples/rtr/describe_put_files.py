#!/usr/bin/env python3
"""
Caracara Examples Collection.

describe_put_files.py

This example will use the API credentials configuration in your config.yml file to
list all the files that can be used with the PUT command.
"""
import logging

from caracara import Client
from examples.common import caracara_example, pretty_print


@caracara_example
def describe_put_files(**kwargs):
    """Describe all available PUT files and and write the output to the log."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]

    with client:
        logger.info("Listing available PUT files")
        for put_file_id, put_file_data in client.rtr.describe_put_files().items():
            logger.info("%s\n%s", put_file_id, pretty_print(put_file_data))


if __name__ == "__main__":
    describe_put_files()
