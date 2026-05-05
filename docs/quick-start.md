# Quick Start Guide

Get up and running with Caracara in just a few minutes!

## Prerequisites

- Python 3.10 or higher
- CrowdStrike Falcon API credentials (Client ID and Client Secret)
- Basic familiarity with Python

## Installation

### Using Poetry (Recommended)

```bash
poetry add caracara
```

### Using Pip

```bash
pip install caracara
```

## Getting API Credentials

1. Log into your CrowdStrike Falcon console
2. Navigate to **Support** → **API Clients and Keys**
3. Click **Add new API Client**
4. Provide a name and description
5. Select appropriate **API Scopes** based on your needs:
   - **Hosts**: Read, Write (for device management)
   - **Host Group**: Read, Write (for group management)
   - **Real Time Response**: Read, Write, Admin (for RTR)
   - **Prevention Policies**: Read, Write (for policy management)
   - **Response Policies**: Read, Write
   - **Sensor Update Policies**: Read, Write
   - **User Management**: Read, Write (for user management)
   - **Flight Control**: Read, Write (for MSSP operations)
6. Click **Add** and save your Client ID and Client Secret

## Your First Caracara Script

Create a file called `list_devices.py`:

```python
#!/usr/bin/env python3
"""List all devices in your Falcon tenant."""

from caracara import Client

# Initialize the client with your credentials
client = Client(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    # cloud_name is auto-detected, but you can specify:
    # cloud_name="us-1"  # or "us-2", "eu-1", "us-gov-1", etc.
)

# Get all devices
devices = client.hosts.describe_devices()

# Display results
print(f"Total devices: {len(devices)}\n")

for device_id, device in devices.items():
    hostname = device.get('hostname', 'Unknown')
    os = device.get('platform_name', 'Unknown OS')
    last_seen = device.get('last_seen', 'Never')
    
    print(f"{hostname}")
    print(f"  OS: {os}")
    print(f"  Last Seen: {last_seen}")
    print(f"  Device ID: {device_id}\n")
```

Run it:
```bash
python list_devices.py
```

## Using Environment Variables

For better security, use environment variables instead of hardcoding credentials:

```python
import os
from caracara import Client

client = Client(
    client_id=os.environ.get('FALCON_CLIENT_ID'),
    client_secret=os.environ.get('FALCON_CLIENT_SECRET'),
)
```

Or use Caracara's built-in environment variable interpolation:

```python
from caracara import Client

# Caracara automatically expands ${VAR} syntax
client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)
```

Set your environment variables:
```bash
export FALCON_CLIENT_ID="your_client_id"
export FALCON_CLIENT_SECRET="your_client_secret"
```

## Filtering Devices

Use the `FalconFilter` class to build filters:

```python
from caracara import Client

client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)

# Create a filter for Windows devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")

# Get matching devices
windows_devices = client.hosts.describe_devices(filters)
print(f"Found {len(windows_devices)} Windows devices")

# Filter further - Windows devices not seen in 7 days
filters.create_new_filter("LastSeen", "-7d", "LTE")
stale_windows = client.hosts.describe_devices(filters)
print(f"Found {len(stale_windows)} stale Windows devices")
```

## Using Context Managers

Caracara supports Python's context manager protocol for automatic cleanup:

```python
from caracara import Client

with Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
) as client:
    devices = client.hosts.describe_devices()
    print(f"Total devices: {len(devices)}")
# Authentication token is automatically revoked here
```

## Common Use Cases

### Finding Stale Sensors

```python
from caracara import Client

client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)

# Find devices that haven't checked in for 30 days
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("LastSeen", "-30d", "LTE")

stale_devices = client.hosts.describe_devices(filters)

print(f"Found {len(stale_devices)} devices that haven't checked in for 30+ days:\n")

for device_id, device in stale_devices.items():
    hostname = device.get('hostname', 'Unknown')
    last_seen = device.get('last_seen', 'Never')
    print(f"  {hostname} - Last Seen: {last_seen}")
```

### Getting Online State

```python
from caracara import Client

client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)

# Get all devices with their online state
devices = client.hosts.describe_devices(enrich_with_online_state=True)

online_count = 0
offline_count = 0

for device_id, device in devices.items():
    state = device.get('state', 'unknown')
    if state == 'online':
        online_count += 1
    elif state == 'offline':
        offline_count += 1

print(f"Online: {online_count}")
print(f"Offline: {offline_count}")
```

### Organizing Devices into Groups

```python
from caracara import Client

client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)

# Create a group for web servers
web_servers_group = client.hosts.create_group(
    name="Production Web Servers",
    description="All production web server hosts",
    group_type="dynamic",
    assignment_rule="tags:'FalconGroupingTags/Role/WebServer'"
)

print(f"Created group with ID: {web_servers_group}")

# Or create a static group and add devices manually
database_group = client.hosts.create_group(
    name="Database Servers",
    description="Database server hosts",
    group_type="static"
)

# Find database servers and add them
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "db-*")
db_device_ids = client.hosts.get_device_ids(filters)

client.hosts.add_to_group(
    group_id=database_group,
    device_ids=db_device_ids
)

print(f"Added {len(db_device_ids)} devices to database group")
```

### Running Remote Commands

```python
from caracara import Client

client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)

# Get web server device IDs
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("tags", "FalconGroupingTags/Role/WebServer")
web_servers = client.hosts.get_device_ids(filters)

# Create an RTR session
session = client.rtr.batch_session()
session.connect(device_ids=web_servers)

# Check running processes
results = session.run_generic_command("ps")

for device_id, result in results.items():
    if result.get('complete'):
        print(f"\nDevice {device_id}:")
        print(result['stdout'])
    else:
        print(f"\nDevice {device_id}: Command failed")
```

## Configuration Options

### Client Parameters

```python
client = Client(
    client_id="...",              # Required (or use auth_object)
    client_secret="...",          # Required (or use auth_object)
    cloud_name="auto",            # Auto-detect cloud region, or specify explicitly
    member_cid=None,              # For MSSP: Child CID to operate on
    ssl_verify=True,              # Verify SSL certificates (should always be True)
    timeout=None,                 # Request timeout in seconds
    proxy=None,                   # Proxy URL: "http://proxy:8080"
    user_agent=None,              # Custom user agent string
    verbose=False,                # Enable verbose logging
    debug=False,                  # Enable debug logging in FalconPy
    debug_record_count=None,      # Number of records to log in debug mode
    sanitize_log=True,            # Sanitize sensitive data in logs
    falconpy_authobject=None,     # Use existing FalconPy OAuth2 object
)
```

### Cloud Regions

Valid `cloud_name` values:
- `"auto"` - Automatically detect (default)
- `"us-1"` - US Commercial 1
- `"us-2"` - US Commercial 2
- `"eu-1"` - EU
- `"us-gov-1"` - US GovCloud

### Proxy Configuration

```python
client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
    proxy="http://proxy.example.com:8080",
)

# Or with authentication
client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
    proxy="http://user:pass@proxy.example.com:8080",
)
```

## Logging

Caracara uses Python's built-in `logging` module:

```python
import logging
from caracara import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create client
client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)

# Operations will now log at INFO level
devices = client.hosts.describe_devices()
```

Logging levels:
- `DEBUG`: Verbose details including API responses (very verbose)
- `INFO`: High-level operation progress
- `WARNING`: Potential issues
- `ERROR`: Errors and exceptions

For production, consider logging to a file:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('caracara.log'),
        logging.StreamHandler()  # Also log to console
    ]
)
```

## Error Handling

```python
from caracara import Client
from caracara.common.exceptions import (
    BaseCaracaraError,
    GenericAPIError,
    DeviceNotFound,
)

client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)

try:
    # Try to get devices
    filters = client.FalconFilter(dialect="hosts")
    filters.create_new_filter("Hostname", "nonexistent-device")
    devices = client.hosts.describe_devices(filters)
    
    if not devices:
        print("No devices found matching the filter")
        
except DeviceNotFound as e:
    print(f"Device not found: {e}")
except GenericAPIError as e:
    print(f"API error: {e}")
    print(f"Error code: {int(e)}")
except BaseCaracaraError as e:
    print(f"Caracara error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Next Steps

Now that you've got the basics down, explore more advanced topics:

- **[Architecture Overview](architecture.md)** - Understand how Caracara is structured
- **[Filtering Guide](filtering.md)** - Master advanced filtering techniques
- **[Hosts Module](modules/hosts.md)** - Deep dive into device management
- **[RTR Module](modules/rtr.md)** - Remote command execution
- **[Policy Modules](modules/prevention-policies.md)** - Manage security policies

### Example Scripts

Caracara includes a comprehensive collection of example scripts. To use them:

1. Clone the repository:
   ```bash
   git clone https://github.com/CrowdStrike/caracara.git
   cd caracara
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Copy and configure the example config:
   ```bash
   cp examples/config.example.yml examples/config.yml
   # Edit examples/config.yml with your API credentials
   ```

4. Run examples:
   ```bash
   poetry run list-windows-devices
   poetry run stale-sensors
   poetry run list-all-groups
   ```

See the [examples directory](https://github.com/CrowdStrike/caracara/tree/main/examples) for the full collection.

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/CrowdStrike/caracara/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/CrowdStrike/caracara/discussions)
- **FalconPy Documentation**: [falconpy.io](https://falconpy.io)
