#!/usr/bin/env python3
r"""Caracara Examples Collection.

get_ccid.py

____ ____ ___    ____ ____ _ ___
| __ |___  |     |    |    | |  \
|__] |___  |     |___ |___ | |__/

Print the Checksummed Customer ID (CCID) for the authenticated Falcon tenant.

The CCID is required when installing the Falcon sensor (e.g. --cid=<CCID>).

Credentials are loaded from the examples/config.yml profile.
"""

import click

from examples.common import load_client_from_profile


@click.command(
    name="get-ccid",
    help=(
        "Print the Checksummed Customer ID (CCID) for the Falcon tenant.\n\n"
        "The CCID is the value passed to the sensor installer via --cid=<CCID>. "
        "The plain CID (without the two-character checksum suffix) is also shown.\n\n"
        "Credentials are loaded from examples/config.yml."
    ),
)
@click.option(
    "--profile",
    default=None,
    metavar="NAME",
    help="Profile name from examples/config.yml (default: auto-select).",
)
def get_ccid(profile: str):
    """Print the tenant CID and CCID."""
    client, _ = load_client_from_profile(profile)

    with client:
        ccid = client.sensor_download.get_cid(include_checksum=True)
        cid = client.sensor_download.get_cid(include_checksum=False)

    click.echo(click.style("CID  (plain):        ", bold=True) + cid)
    click.echo(
        click.style("CCID (with checksum): ", bold=True)
        + click.style(ccid, fg="green", bold=True)
    )


if __name__ == "__main__":
    get_ccid()
