#!/usr/bin/env python3
"""
Caracara Examples Collection.

get_maintenance_token.py

This example will allow you to search for a system in the CID and get its maintenance token.
"""
from typing import Dict

from caracara import Client

from examples.common import (
    caracara_example,
    choose_item,
)


@caracara_example
def get_maintenance_token(**kwargs):
    """Search for a system and get its maintenance token."""
    client: Client = kwargs["client"]

    print("Getting all devices in the Falcon tenant")
    devices: Dict[str, Dict] = client.hosts.describe_devices()

    id_name_mapping = {
        "MAINTENANCE": "Bulk Maintenance Token",
    }
    for device_id, device_data in devices.items():
        id_name_mapping[device_id] = device_data["hostname"]

    chosen_id = choose_item(id_name_mapping, prompt_text="Search for a Device")

    maintenance_token = client.sensor_update_policies.get_maintenance_token(chosen_id)
    print(maintenance_token)
