#!/usr/bin/env python3
"""
Caracara Examples Collection
create_prevention_policy.py

This example will create a Windows prevention rolicy based on the included template.
You can use this code sample to customise the policy.
"""
from caracara import Client

from examples.common import caracara_example, pretty_print


@caracara_example
def create_prevention_policy(**kwargs):
    """Creates a new Windows prevention policy with everything enabled"""
    client: Client = kwargs['client']

    prevention_policy = client.prevention_policies.new_policy("Windows")
    pretty_print(prevention_policy.flat_dump())


create_prevention_policy()
