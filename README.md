# FalconPy Tools
A collection of tools for interacting with the CrowdStrike Falcon API.



## Basic usage example
The following example demonstrates using the Hosts Toolbox to retrieve a host AID.
```python
from falconpytools.hosts import HostsToolbox, Host

hosts = HostsToolbox(os.environ["FALCON_CLIENT_ID"],
                     os.environ["FALCON_CLIENT_SECRET"],
                     verbose=True
                     )

host = Host(api=hosts.api, verbose=hosts.verbose)
aid = host.find_host_aid(hostname="SEARCH-STRING")
print(aid)
```