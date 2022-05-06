#!/usr/bin/env python3
"""
Caracara Examples Collection
describe_scripts.py

This example will use the API credentials configuration in your config.yml file to
list all the scripts that are stored in the associated Falcon tenant
"""
import logging

from caracara import Client

from examples.common import caracara_example, pretty_print


@caracara_example
def describe_scripts(**kwargs):
    """Desctibe all available cloud scripts and and write the output to the log"""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Listing available PUT files")
    scripts = client.rtr.describe_scripts()
    pretty_print(scripts)


describe_scripts()
