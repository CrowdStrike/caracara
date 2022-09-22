#!/usr/bin/env python3
"""
Caracara Examples Collection.

describe_child_cids.py

This example will show all Child CIDs within a Parent Falcon Flight Control / MSSP CID.
"""
from caracara import Client

from examples.common import caracara_example, pretty_print

@caracara_example
def describe_child_cids(**kwargs):
    client: Client = kwargs['client']

    child_cids = client.flight_control.describe_child_cids()
    print(pretty_print(child_cids))


if __name__ == "__main__":
    describe_child_cids()
