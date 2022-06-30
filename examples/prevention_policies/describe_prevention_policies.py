#!/usr/bin/env python3
"""
Caracara Examples Collection.

describe_prevention_policies.py

This example will use the API credentials configured in your config.yml file to
show all the prevention policies configured within the Falcon tenant.

This example demonstrates using a combination of the FalconFilter class and
the response policies API.
"""
import logging

from typing import List

from caracara import Client, Policy

from examples.common import caracara_example, pretty_print


@caracara_example
def describe_prevention_policies(**kwargs):
    """List Prevention Policies."""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Grabbing all Windows prevention policies from the Falcon tenant")

    filters = client.FalconFilter()
    filters.create_new_filter("OS", "Windows")
    policies: List[Policy] = client.prevention_policies.describe_policies(filters=filters)

    i = 1
    for policy in policies:
        print(f"Prevention policy {i}: {policy.name} ({policy.platform_name})")
        if policy.description:
            print(policy.description)

        logger.info("Policy JSON")
        logger.info(pretty_print(policy.dump()))

        logger.debug("Flat policy JSON for use with the Falcon API")
        logger.debug(pretty_print(policy.flat_dump()))

        i += 1


if __name__ == '__main__':
    describe_prevention_policies()
