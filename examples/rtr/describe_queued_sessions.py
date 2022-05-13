#!/usr/bin/env python3
"""
Caracara Examples Collection.

list_queued_sessions.py

This example will use the API credentials configuration in your config.yml file to
list all queued RTR sesisons, as well as the commands scheduled for exection.
"""
import logging

from caracara import Client

from examples.common import caracara_example, pretty_print


@caracara_example
def describe_queued_sessions(**kwargs):
    """Describe all currently queued RTR sessions and write the output to the log."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Listing queued RTR sessions")
    sessions = client.rtr.describe_queued_sessions()
    pretty_print(sessions)


describe_queued_sessions()
