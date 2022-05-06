#!/usr/bin/env python3
"""
Caracara Examples Collection
describe_put_files.py

This example will use the API credentials configuration in your config.yml file to
list all the files that can be used with the PUT command.
"""
import logging

from caracara import Client

from examples.common import caracara_example, pretty_print


@caracara_example
def describe_put_files(**kwargs):
    """Desctibe all available PUT files and and write the output to the log"""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Listing available PUT files")
    put_files = client.rtr.describe_put_files()
    pretty_print(put_files)


describe_put_files()
