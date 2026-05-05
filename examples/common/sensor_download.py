"""Shared utilities for sensor download examples."""

from typing import Tuple

import click

from caracara import Client


def build_sensor_download_filters(client: Client, filter_kv_strings: Tuple[str, ...]):
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
