![CrowdStrike Falcon](https://raw.githubusercontent.com/CrowdStrike/falconpy/main/docs/asset/cs-logo.png) [![Twitter URL](https://img.shields.io/twitter/url?label=Follow%20%40CrowdStrike&style=social&url=https%3A%2F%2Ftwitter.com%2FCrowdStrike)](https://twitter.com/CrowdStrike)<br/>

# Caracara
<!--
![PyPI - Status](https://img.shields.io/pypi/status/caracara)
[![PyPI](https://img.shields.io/pypi/v/caracara)](https://pypi.org/project/caracara/)
[![Pylint](https://github.com/CrowdStrike/caracara/actions/workflows/pylint.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/pylint.yml)
[![Flake8](https://github.com/CrowdStrike/caracara/actions/workflows/flake8.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/flake8.yml)
[![Bandit](https://github.com/CrowdStrike/caracara/actions/workflows/bandit.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/bandit.yml)
[![CodeQL](https://github.com/CrowdStrike/caracara/actions/workflows/codeql.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/codeql.yml)
-->
![OSS Lifecycle](https://img.shields.io/osslifecycle/CrowdStrike/caracara)

A collection of tools for interacting with the CrowdStrike Falcon API.

## Basic usage example

```python
"""
This example will use the API credentials configured in your config.yml file to
list the names of all systems within your Falcon tenant that run Windows.

The example demonstrates how to use the FalconFilter() class and the Hosts API.
"""
import logging

from caracara import Client

from examples.common import caracara_example


@caracara_example
def list_windows_devices(**kwargs):
    """List Windows Devices Example"""
    client: Client = kwargs['client']
    logger: logging.Logger = kwargs['logger']

    logger.info("Grabbing all Windows devices within the tenant")

    filters = client.FalconFilter()
    filters.create_new_filter("OS", "Windows")
    logger.info("Using the FQL filter: %s", filters.get_fql())

    response_data = client.hosts.describe_devices(filters)
    logger.info("Found %d devices running Windows", len(response_data.keys()))

    for device_id, device_data in response_data.items():
        hostname = device_data.get("hostname", "Unknown Hostname")
        logger.info("%s (%s)", device_id, hostname)

    logger.info("Done!")


if __name__ == '__main__':
    list_windows_devices()

```

## Installation
```shell
python3 -m pip install caracara
```

## Upgrading
```shell
python3 -m pip install caracara --upgrade
```

## Removal
```shell
python3 -m pip uninstall caracara
```