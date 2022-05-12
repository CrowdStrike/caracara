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

A friendly wrapper to help you interact with the CrowdStrike Falcon API. Less code, less fuss, better performance, and full interoperability with [FalconPy](https://github.com/CrowdStrike/falconpy/).

## Installation Instructions

Caracara supports all major Python packaging solutions. Instructions for [Poetry](https://python-poetry.org) and [Pip](https://pypi.org/project/pip/) are provided below.

<details>
<summary><h3>Installing Caracara from PyPI using Poetry (Recommended!)</h3></summary>

### Poetry: Installation

```shell
poetry add caracara
```

### Poetry: Upgrading

```shell
poetry update caracara
```

### Poetry: Removal

```shell
poetry remove caracara
```
</details>

<details>
<summary><h3>Installing Caracara from PyPI using Pip</h3></summary>

### Pip: Installation

```shell
python3 -m pip install caracara
```

### Pip: Upgrading

```shell
python3 -m pip install caracara --upgrade
```

### Pip: Removal

```shell
python3 -m pip uninstall caracara
```

</details>

## Basic Usage Example

```python
"""
This example will use the API credentials provided as parameters to
list the names of all systems within your Falcon tenant that run Windows.

The example demonstrates how to use the FalconFilter() class and the Hosts API.
"""

from caracara import Client

client = Client(
    client_id="12345abcde",
    client_secret="67890fghij",
)

filters = client.FalconFilter()
filters.create_new_filter("OS", "Windows")

response_data = client.hosts.describe_devices(filters)
print(f"Found {len(response_data.keys())} devices running Windows")

for device_id, device_data in response_data.items():
    hostname = device_data.get("hostname", "Unknown Hostname")
    print(f"{device_id} - {hostname}")
```

## Examples Collection

Each API wrapper is provided alongside example code. Cloning or downloading/extracting this repository allows you to execute examples directly.

Using the examples collection requires that you install our Python packaging tool of choice, [Poetry](https://python-poetry.org). Please refer to the Poetry project's [installation guide](https://python-poetry.org/docs/#installation) if you do not yet have Poetry installed.

Once Poetry is installed, make sure you run `poetry install` within the `caracara` folder to set up the Python virtual environment.

To configure the examples, first copy `examples/config.example.yml` to `examples/config.yml`. Then, add your API credentials and example-specific settings to `examples/config.yml`. Once you have set up profiles for each Falcon tenant you want to test with, execute examples using one of the two options below.

### Executing the Examples

There are two ways to use Poetry to execute the examples.

<details>
<summary><h4>Executing from a Poetry Shell</h4></summary>

The `poetry shell` command will enter you into the virtual environment. All future commands will run within the Caracara virtual environment using Python 3, until you run the `deactivate` command.

```shell
poetry shell
examples/get_devices/list_windows_devices.py
```

</details>

<details>
<summary><h4>Executing without Activating the Virtual Environment</h4></summary>

If you do not want to enter the Caracara virtual environment (e.g., because you are using your system's installation of Python for other purposes), you can use the `poetry run` command to temporarily invoke the virtual environment for one-off commands.

```shell
poetry run examples/get_devices/list_windows_devices.py
```

</details>
