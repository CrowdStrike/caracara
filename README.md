![CrowdStrike Falcon](https://raw.githubusercontent.com/CrowdStrike/falconpy/main/docs/asset/cs-logo.png) [![Twitter URL](https://img.shields.io/twitter/url?label=Follow%20%40CrowdStrike&style=social&url=https%3A%2F%2Ftwitter.com%2FCrowdStrike)](https://twitter.com/CrowdStrike)<br/>

# FalconPy Tools
[![Pylint](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/pylint.yml/badge.svg)](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/pylint.yml)
[![Flake8](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/flake8.yml/badge.svg)](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/flake8.yml)
[![Bandit](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/bandit.yml/badge.svg)](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/bandit.yml)
[![CodeQL](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/codeql.yml/badge.svg)](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/codeql.yml)
![Maintained](https://img.shields.io/maintenance/yes/2021)

A collection of tools for interacting with the CrowdStrike Falcon API.

## Basic usage example
The following example demonstrates using the Hosts Toolbox to retrieve a host AID,
and then using the RTR Toolbox to initiate a session and execute `ifconfig`.
```python
import os
from falconpytools.hosts import HostsToolbox, Host
from falconpytools.rtr import RTRToolbox, SingleTarget

# Open the RTR toolbox
rtr = RTRToolbox(os.environ["FALCON_CLIENT_ID"],
                 os.environ["FALCON_CLIENT_SECRET"],
                 verbose=True
                 )
# Open the Hosts toolbox
hosts = HostsToolbox(auth_object=rtr.api.rtr.auth_object,
                     verbose=True
                     )
# Host helper
host = Host(api=hosts.api, verbose=hosts.verbose)
# Lookup the AID for our search string
target_aid = host.find_host_aid(hostname="SEARCH-STRING")
hostname = host.get_host(target_aid)[0]["hostname"]
# RTR Single Target helper
target = SingleTarget(api=rtr.api, verbose=rtr.verbose)
# Initialize a RTR session
target_session = target.connect_to_host(target_aid)
# Execute a RTR command
command_result = host.execute_command("ifconfig", target_session)
# Disconnect from the RTR session
host.disconnect_from_host(target_session)
# Output the results
print(command_result)
```

## Installation
```shell
python3 -m pip install crowdstrike-falconpy-tools
```

## Upgrading
```shell
python3 -m pip install crowdstrike-falconpy-tools --upgrade
```

## Removal
```shell
python3 -m pip uninstall crowdstrike-falconpy-tools
```