#!/usr/bin/env python3
r"""Caracara Examples Collection.

download_sensor_installer.py

___  ____ _ _ _ _  _ _    ____ ____ ___     ____ ____ _  _ ____ ____ ____
|  \ |  | | | | |\ | |    |  | |__| |  \    [__  |___ |\ | [__  |  | |__/
|__/ |__| |_|_| | \| |___ |__| |  | |__/    ___] |___ | \| ___] |__| |  \

Download a Falcon sensor installer to disk, and print the tenant CCID.

When --sha256 is not given, the most recently released installer matching the
provided filters is selected automatically.

Credentials are loaded from the examples/config.yml profile.

Examples:
  # Latest Linux sensor for RHEL 8, saved to /tmp/sensors
  download-sensor-installer -f platform=Linux -f os=RHEL -f os_version=8 \
      --destination /tmp/sensors

  # Latest LTS Windows sensor, version embedded in filename
  download-sensor-installer -f platform=Windows -f lts=True \
      --destination C:/Installers --include-version

  # A specific build by SHA256, with a custom filename
  download-sensor-installer --sha256 <hash> --destination /tmp/sensors \
      --filename my-sensor.exe
"""

import os
from typing import Tuple

import click

from caracara import Client
from examples.common import load_client_from_profile


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
    name="download-sensor-installer",
    help=(
        "Download a Falcon sensor installer to disk.\n\n"
        "Without --sha256, the newest installer matching the provided filters is chosen. "
        "If multiple installers match the filters, --include-version is required to avoid "
        "filename collisions (e.g. multiple Windows builds all share FalconSensor_Windows.exe). "
        "The tenant CCID is always printed at the end for convenience.\n\n"
        "Credentials are loaded from examples/config.yml.\n\n"
        "Examples:\n\n"
        "  download-sensor-installer -f platform=Linux --destination /tmp/sensors\n\n"
        "  download-sensor-installer -f platform=Windows -f lts=True "
        "--destination C:/Installers --include-version\n\n"
        "  download-sensor-installer --sha256 <hash> --destination /tmp/sensors"
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
@click.option(
    "--sha256",
    default=None,
    metavar="HASH",
    help="Download a specific installer by SHA256 instead of using filters.",
)
@click.option(
    "--destination",
    required=True,
    type=click.Path(file_okay=False, writable=True),
    metavar="DIR",
    help="Directory to save the installer into (created if absent).",
)
@click.option(
    "--filename",
    default=None,
    metavar="NAME",
    help=(
        "Override the saved filename. Mutually exclusive with --include-version. "
        "Default: canonical cloud name (e.g. FalconSensor_Windows.exe)."
    ),
)
@click.option(
    "--include-version",
    is_flag=True,
    default=False,
    help=(
        "Embed the sensor version in the filename "
        "(e.g. FalconSensor_Windows-7.32.20406.exe). "
        "Required when filters match more than one installer."
    ),
)
@click.option(
    "--if-exists",
    type=click.Choice(["error", "skip", "overwrite"], case_sensitive=False),
    default="error",
    show_default=True,
    help="Behaviour when the destination file already exists.",
)
def download_sensor_installer(  # pylint: disable=too-many-arguments
    profile: str,
    filter_kv_strings: Tuple[str, ...],
    sha256: str,
    destination: str,
    filename: str,
    include_version: bool,
    if_exists: str,
):
    """Download the latest matching Falcon sensor installer and display the CCID."""
    if not sha256 and not filter_kv_strings:
        raise click.UsageError(
            "Provide at least one -f filter or --sha256 to identify the installer to download."
        )
    if filename and include_version:
        raise click.UsageError("--filename and --include-version are mutually exclusive.")

    client, _ = load_client_from_profile(profile)

    os.makedirs(destination, exist_ok=True)

    with client:
        ccid = client.sensor_download.get_cid(include_checksum=True)

        if sha256:
            click.echo(
                click.style("Downloading installer by SHA256: ", bold=True) + sha256[:16] + "..."
            )
        else:
            filters = _build_filters(client, filter_kv_strings)
            fql = filters.get_fql()
            click.echo(click.style("FQL filter: ", bold=True), nl=False)
            click.echo(fql)

            installers = client.sensor_download.describe_installers(
                filters=filters,
                sort="release_date|desc",
            )
            if not installers:
                click.echo(click.style("No installers matched the provided filters.", fg="red"))
                raise SystemExit(1)

            if len(installers) > 1 and not filename and not include_version:
                if len({i["name"] for i in installers}) < len(installers):
                    raise click.UsageError(
                        f"{len(installers)} installers matched but their canonical filenames "
                        "are not all unique — add --include-version to embed the version in "
                        "each filename, or narrow your filters to a single result."
                    )

            chosen = installers[0]
            sha256 = chosen["sha256"]
            click.echo(
                click.style("Selected: ", bold=True)
                + f"{chosen['name']}  "
                + click.style(f"version {chosen['version']}", fg="cyan")
                + f"  released {chosen['release_date'][:10]}"
            )

        try:
            saved_path = client.sensor_download.download_installer(
                sha256=sha256,
                destination_path=destination,
                filename=filename,
                include_version=include_version,
                if_exists=if_exists,
            )
        except FileExistsError as exc:
            raise click.ClickException(str(exc)) from exc

        click.echo(click.style("Saved to:  ", bold=True) + saved_path)
        click.echo(click.style("CCID:      ", bold=True) + click.style(ccid, fg="green", bold=True))


if __name__ == "__main__":
    download_sensor_installer()  # pylint: disable=no-value-for-parameter
