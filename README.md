![CrowdStrike Falcon](https://raw.githubusercontent.com/CrowdStrike/falconpy/main/docs/asset/cs-logo.png) [![Twitter URL](https://img.shields.io/twitter/url?label=Follow%20%40CrowdStrike&style=social&url=https%3A%2F%2Ftwitter.com%2FCrowdStrike)](https://twitter.com/CrowdStrike)<br/>

# Caracara



<!--
![PyPI - Status](https://img.shields.io/pypi/status/caracara)
[![Pylint](https://github.com/CrowdStrike/caracara/actions/workflows/pylint.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/pylint.yml)
[![Flake8](https://github.com/CrowdStrike/caracara/actions/workflows/flake8.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/flake8.yml)
[![Bandit](https://github.com/CrowdStrike/caracara/actions/workflows/bandit.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/bandit.yml)
[![CodeQL](https://github.com/CrowdStrike/caracara/actions/workflows/codeql.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/codeql.yml)
-->
[![PyPI](https://img.shields.io/pypi/v/caracara)](https://pypi.org/project/caracara/)
![OSS Lifecycle](https://img.shields.io/osslifecycle/CrowdStrike/caracara)

A friendly wrapper to help you interact with the CrowdStrike Falcon API. Less code, less fuss, better performance, and full interoperability with [FalconPy](https://github.com/CrowdStrike/falconpy/).

- [Features](#features)
- [Installation](#installation-instructions)
- [Basic Usage](#basic-usage-example)
- [Examples](#examples-collection)
- [Documentation](#documentation)
- [Contributing](#contributing)

## Features

A few of the developer experience enhancements provided by the Caracara toolkit include:
| Feature | Details |
| :---  | :--- |
| __Automatic pagination with concurrency__ | Caracara will handle all request pagination for you, so you do not have to think about things like batch sizes, batch tokens or parallelisation. Caracara will also multithread batch data retrieval requests where possible, dramatically reducing data retrieval times for large datasets such as host lists. |
| __Friendly to your IDE (and you!)__ | Caracara is written with full support for IDE autocomplete in mind. We have tested autocomplete in Visual Studio Code and PyCharm, and will accept issues and patches for more IDE support where needed. Furthermore, all code, where possible, is written with type hints so you can be confident in parameters and return values. |
| __Logging__ | Caracara is built with the in-box `logging` library provided with Python 3. Simply set up your logging handlers in your main code file, and Caracara will forward over `debug`, `info` and `error` logs as they are produced. Note that the `debug` logs are very verbose, and we recommend writing these outputs to a file as opposed to the console when retrieving large amounts of lightly filtered data. |
| __Real Time Response (RTR) batch session abstraction__ | Caracara provides a rich interface to RTR session batching, allowing you to connect to as many hosts as possible. Want to download a specific file from every system in your Falcon tenant? Caracara will even extract it from the `.7z` container for you. |
| __Rich and detailed sample code__ | Every module of Caracara comes bundled with executable, fully configurable code samples that address frequent use cases. All samples are built around a common structure allowing for code reuse and easy reading. Just add your API credentials to `config.yml`, and all samples will be ready to go. |
| __Simple filter syntax__ | Caracara provides an object-orientated Falcon Query Language (FQL) generator. The `FalconFilter` object lets you specify filters such as `Hostname`, `OS` and `Role`, automatically converting them to valid FQL. Never write a FQL filter yourself again! |
| __Single authentication point of entry__ | Authenticate once and have access to every module. |
| __100% FalconPy compatibility__ | Caracara is built on FalconPy, and can even be configured with a FalconPy `OAuth2` object via the `auth_object` constructor parameter, allowing you to reuse FalconPy authentication objects across Caracara and FalconPy. Authenticate once with FalconPy, and access every feature of FalconPy and Caracara. |

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

## Basic Usage Examples

```python
"""List Windows devices.

This example will use the API credentials provided as keywords to list the
IDs and hostnames of all systems within your Falcon tenant that run Windows.
"""

from caracara import Client

client = Client(
    client_id="12345abcde",
    client_secret="67890fghij",
)

filters = client.FalconFilter()
filters.create_new_filter("OS", "Windows")

response_data = client.hosts.describe_devices(filters)
print(f"Found {len(response_data)} devices running Windows")

for device_id, device_data in response_data.items():
    hostname = device_data.get("hostname", "Unknown Hostname")
    print(f"{device_id} - {hostname}")
```

You can also leverage the built in context manager and environment variables.

```python
"""List stale sensors.

This example will use the API credentials set in the environment to list the
hostnames and IDs of all systems within your Falcon tenant that have not checked
into your CrowdStrike tenant within the past 7 days.

This is determined based on the filter LastSeen less than or equal (LTE) to 7 days ago (-7d).
"""

from caracara import Client


with Client(client_id="${CLIENT_ID_ENV_VARIABLE}", client_secret="${CLIENT_SECRET_ENV_VARIABLE}") as client:
    filters = client.FalconFilter()
    filters.create_new_filter("LastSeen", "-7d", "LTE")
    response_data = client.hosts.describe_devices(filters)

print(f"Found {len(response_data)} stale devices")

for device_id, device_data in response_data.items():
    hostname = device_data.get("hostname", "Unknown Hostname")
    print(f"{device_id} - {hostname}")
```

## Examples Collection

Each API wrapper is provided alongside example code. Cloning or downloading/extracting this repository allows you to execute examples directly.

Using the examples collection requires that you install our Python packaging tool of choice, [Poetry](https://python-poetry.org). Please refer to the Poetry project's [installation guide](https://python-poetry.org/docs/#installation) if you do not yet have Poetry installed.

Once Poetry is installed, make sure you run `poetry install` within the root repository folder to set up the Python virtual environment.

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

All examples are also configured in the `pyproject.toml` file as scripts, allowing them to be executed simply.

```shell
poetry run stale-sensors
```

> To get a complete list of available examples, execute the command `util/list-examples.sh` from the root of the repository folder.

</details>

## Documentation

__*Coming soon!*__

## Contributing

Interested in taking part in the development of the Caracara project? Start [here](CONTRIBUTING.md).

## Why Caracara?

Simple! We like birds at CrowdStrike, so what better bird to name a Python project after one that eats just about anything, including snakes :)
