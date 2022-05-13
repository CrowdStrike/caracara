#!/usr/bin/env python3
"""
Caracara Examples Collection.

clear_queued_sessions.py

This example will use the API credentials configuration in your config.yml file to
search for all queued RTR sessions, and clear (delete) them.

Note that this can only access sessions that were created with this API token,
as the Falcon API will not let you clear somebody else's queued session.
"""
import logging

from caracara import Client

from examples.common import caracara_example


@caracara_example
def clear_queued_sessions(**kwargs):
    """Clear all RTR sessions queued up by this API client."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Clearing all queued RTR sessions")
    client.rtr.clear_queued_sessions()


clear_queued_sessions()
