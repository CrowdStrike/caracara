#!/usr/bin/env python3
r"""Caracara Examples Collection.

list_sensor_versions.py

_    _ ____ ___    ____ ____ _  _ ____ ____ ____    _  _ ____ ____ ____ _ ____ _  _ ____
|    | [__   |     [__  |___ |\ | [__  |  | |__/    |  | |___ |__/ [__  | |  | |\ | [__
|___ | ___]  |     ___] |___ | \| ___] |__| |  \     \/  |___ |  \ ___] | |__| | \| ___]

List available Falcon sensor installer versions, with optional FQL filtering.

Results are sorted by platform (ascending), version (descending), OS name
(ascending), and OS version (ascending), so the newest build for each
platform appears first and variants of the same build are grouped together.

Credentials are loaded from the examples/config.yml profile.

Filter examples (the -f flag maps directly to the sensor_download FQL dialect):
  -f platform=Linux
  -f platform=Windows
  -f os=RHEL
  -f version__GTE=7.14.0
  -f lts=True
  -f release_date__GTE=-90d
"""

from typing import Tuple

import click
from packaging.version import InvalidVersion, Version
from tabulate import tabulate

from caracara import Client
from examples.common import load_client_from_profile


def _version_sort_key(version_str: str):
    """Return a sort key that orders PEP 440 versions numerically, others last."""
    try:
        return (0, Version(version_str))
    except InvalidVersion:
        return (1, version_str)


def _build_filters(client: Client, filter_kv_strings: Tuple[str, ...]):
    """Convert a sequence of key=value strings into a sensor_download FalconFilter."""
    filters = client.FalconFilter(dialect="sensor_download")
    for kv in filter_kv_strings:
        if "=" not in kv:
            raise click.BadParameter(
                f"'{kv}' is not in key=value format. "
                "Example: -f platform=Linux  or  -f version__GTE=7.14.0"
            )
        filters.create_new_filter_from_kv_string(*kv.split("=", 1))
    return filters


@click.command(
    name="list-sensor-versions",
    help=(
        "List available Falcon sensor installer versions.\n\n"
        "Use -f key=value to filter results using the sensor_download FQL dialect. "
        "Operator suffixes are supported via double-underscore notation, "
        "e.g. -f version__GTE=7.14.0.\n\n"
        "Results are sorted by platform ascending, then version descending, then OS "
        "name and OS version ascending within each platform/version group.\n\n"
        "Credentials are loaded from examples/config.yml.\n\n"
        "Examples:\n\n"
        "  list-sensor-versions\n\n"
        "  list-sensor-versions -f platform=Linux\n\n"
        "  list-sensor-versions -f platform=Linux -f os=RHEL -f version__GTE=7.14.0\n\n"
        "  list-sensor-versions -f lts=True"
    ),
)
@click.option(
    "--profile",
    default=None,
    metavar="NAME",
    help="Profile name from examples/config.yml (default: auto-select).",
)
@click.option(
    "-f",
    "--filter",
    "filter_kv_strings",
    type=click.STRING,
    multiple=True,
    metavar="KEY=VALUE",
    help=(
        "FQL filter in key=value format. Repeat to add multiple filters. "
        "Operators: KEY__GTE, KEY__GT, KEY__LTE, KEY__LT, KEY__NOT."
    ),
)
def list_sensor_versions(
    profile: str,
    filter_kv_strings: Tuple[str, ...],
):
    """List available Falcon sensor installer versions."""
    client, _ = load_client_from_profile(profile)
    filters = _build_filters(client, filter_kv_strings)

    fql = filters.get_fql()
    if fql:
        click.echo(click.style("FQL filter: ", bold=True), nl=False)
        click.echo(fql)

    with client:
        installers = client.sensor_download.describe_installers(filters=filters)

    if not installers:
        click.echo(click.style("No installers found.", fg="yellow"))
        raise SystemExit(1)

    # Four-pass stable sort, lowest priority first.
    # Final order: platform asc → version desc → os asc → os_version asc.
    # Empty os_version values sort last via the "~" sentinel (after all printable ASCII).
    installers.sort(key=lambda i: (i.get("os_version") or "~"))
    installers.sort(key=lambda i: i["os"])
    installers.sort(key=lambda i: _version_sort_key(i["version"]), reverse=True)
    installers.sort(key=lambda i: i["platform"])

    rows = []
    for inst in installers:
        rows.append(
            [
                inst["platform"],
                inst["version"],
                inst["os"],
                inst.get("os_version") or "—",
                inst["release_date"][:10],
                ", ".join(inst.get("architectures") or []) or "—",
                click.style("Yes", fg="green") if inst.get("is_lts") else "No",
                inst["sha256"],
            ]
        )

    click.echo(
        tabulate(
            rows,
            headers=["Platform", "Version", "OS", "OS Ver", "Released", "Arch", "LTS", "SHA256"],
            tablefmt="rounded_grid",
        )
    )
    click.echo(f"\n{len(installers)} installer(s) found.")


if __name__ == "__main__":
    list_sensor_versions()  # pylint: disable=no-value-for-parameter
