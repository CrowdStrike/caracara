![CrowdStrike Falcon](https://raw.githubusercontent.com/CrowdStrike/falconpy/main/docs/asset/cs-logo.png) [![Twitter URL](https://img.shields.io/twitter/url?label=Follow%20%40CrowdStrike&style=social&url=https%3A%2F%2Ftwitter.com%2FCrowdStrike)](https://twitter.com/CrowdStrike)<br/>

# FalconPy Tools
[![Pylint](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/pylint.yml/badge.svg)](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/pylint.yml)
[![Flake8](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/flake8.yml/badge.svg)](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/flake8.yml)
[![Bandit](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/bandit.yml/badge.svg)](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/bandit.yml)
[![CodeQL](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/codeql.yml/badge.svg)](https://github.com/CrowdStrike/falconpy-tools/actions/workflows/codeql.yml)
![Maintained](https://img.shields.io/maintenance/yes/2021)

A collection of tools for interacting with the CrowdStrike Falcon API.

## Basic usage example
The following example demonstrates using the Hosts Toolbox to retrieve a host AID.
```python
import os
from falconpytools.hosts import HostsToolbox, Host

hosts = HostsToolbox(os.environ["FALCON_CLIENT_ID"],
                     os.environ["FALCON_CLIENT_SECRET"],
                     verbose=True
                     )

host = Host(api=hosts.api, verbose=hosts.verbose)
aid = host.find_host_aid(hostname="SEARCH-STRING")
print(aid)
```