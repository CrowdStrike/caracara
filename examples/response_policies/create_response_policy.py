#!/usr/bin/env python3
"""
Caracara Examples Collection.

create_response_policy.py

This example will create a Windows response policy based on the included template.
You can use this code sample to customise the policy.
"""
import logging

from caracara import Client

from examples.common import caracara_example, pretty_print


@caracara_example
def create_response_policy(**kwargs):
    """Create a new Windows response policy with everything enabled."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]

    response_policy = client.response_policies.new_policy("Windows")
    logger.info(pretty_print(response_policy.flat_dump()))


if __name__ == "__main__":
    create_response_policy()
