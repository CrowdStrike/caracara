#!/usr/bin/env python3
r"""Caracara Samples Library.

list_sensor_versions.py

_    _ ____ ___    ____ ____ _  _ ____ ____ ____
|    | [__   |     [__  |___ |\ | [__  |  | |__/
|___ | ___]  |     ___] |___ | \| ___] |__| |  \

                 _  _ ____ ____ ____ _ ____ _  _ ____
                 |  | |___ |__/ [__  | |  | |\ | [__
                  \/  |___ |  \ ___] | |__| | \| ___]

Lists device ID, Hostname, IP addresses and Agent version
for every device in your CrowdStrike Falcon tenant.

Requirements
  caracara 0.1.1+
  click
  tabulate

Created: 06.08.22, jshcodes@CrowdStrike
"""
from argparse import ArgumentParser, RawTextHelpFormatter

from caracara import Client
from click import echo_via_pager
from tabulate import tabulate


def list_sensor_versions():
    """Consume command line arguments, perform the request, and then display the result."""
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    req = parser.add_argument_group("required arguments")
    req.add_argument("-k", "--client_id", help="API client ID", required=True)
    req.add_argument("-s", "--client_secret", help="API client secret", required=True)

    args = parser.parse_args()

    HEADERS = {
        "device_id": "ID",
        "hostname": "Hostname",
        "local_ip": "Internal IP",
        "external_ip": "External IP",
        "agent_version": "Agent Version"
    }
    devices = []
    with Client(client_id=args.client_id, client_secret=args.client_secret) as client:
        for device in client.hosts.describe_devices().values():
            devices.append({item: device.get(item, "Unavailable") for item in HEADERS})

    echo_via_pager(tabulate(devices, headers=HEADERS, tablefmt="simple"))


if __name__ == '__main__':
    list_sensor_versions()
