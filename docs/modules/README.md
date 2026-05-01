# Caracara API Modules Reference

This document provides a quick reference for all available Caracara API modules.

## Available Modules

### [Hosts Module](hosts.md)
**Access:** `client.hosts`

Manage devices (hosts) and host groups within your Falcon tenant.

**Key capabilities:**
- Device inventory and search
- Host group management
- Device containment
- Tagging
- Login and network history
- Online state monitoring
- Device visibility control

**Common operations:**
```python
# Search for devices
devices = client.hosts.describe_devices(filters)

# Get device IDs only
device_ids = client.hosts.get_device_ids(filters)

# Manage groups
group_id = client.hosts.create_group(name="My Group")
client.hosts.add_to_group(group_id, device_ids)

# Containment
client.hosts.contain(device_ids)
client.hosts.release(device_ids)
```

### [Real Time Response (RTR) Module](rtr.md)
**Access:** `client.rtr`

Execute commands and manage files remotely on devices.

**Key capabilities:**
- Remote command execution
- File upload/download
- Script management
- Session management (supports unlimited hosts)
- Queued sessions for offline devices

**Common operations:**
```python
# Create session and run commands
session = client.rtr.batch_session()
session.connect(device_ids=device_ids)
results = session.run_generic_command("ps")

# File operations
session.get_file("C:\\path\\to\\file", output_folder="/local/path")
```

### Prevention Policies Module
**Access:** `client.prevention_policies`

Manage prevention policy configuration and assignment.

**Key capabilities:**
- List and describe prevention policies
- Create new policies
- Update policy settings
- Assign policies to host groups

**Common operations:**
```python
# List policies
policies = client.prevention_policies.describe_policies()

# Create a policy
policy_id = client.prevention_policies.create_policy(
    name="Strict Prevention",
    description="High-security prevention policy",
    settings={...}
)
```

### Response Policies Module
**Access:** `client.response_policies`

Manage response policy configuration.

**Key capabilities:**
- List and describe response policies
- Create and update policies
- Configure RTR permissions
- Manage response actions

**Common operations:**
```python
# List response policies
policies = client.response_policies.describe_policies()

# Create a response policy
policy_id = client.response_policies.create_policy(
    name="IR Response Policy",
    description="Incident response configuration"
)
```

### Sensor Update Policies Module
**Access:** `client.sensor_update_policies`

Control sensor version deployment and scheduling.

**Key capabilities:**
- Manage sensor update policies
- Configure update schedules
- Control sensor versions by group
- Generate maintenance tokens

**Common operations:**
```python
# Get maintenance token for manual updates
token = client.sensor_update_policies.get_maintenance_token()

# List update policies
policies = client.sensor_update_policies.describe_policies()
```

### Flight Control Module
**Access:** `client.flight_control`

Multi-tenant (MSSP) management operations.

**Key capabilities:**
- List child CIDs
- Manage child tenant access
- Cross-tenant operations

**Common operations:**
```python
# List child CIDs
children = client.flight_control.describe_child_cids()

for child_cid, child_data in children.items():
    print(f"{child_data['name']}: {child_cid}")
```

### Users Module
**Access:** `client.users`

Manage user accounts and roles.

**Key capabilities:**
- List and describe users
- Manage user roles
- Configure user permissions

**Common operations:**
```python
# List all users
users = client.users.describe_users()

# List available roles
roles = client.users.describe_roles()
```

### Custom IOA Module
**Access:** `client.custom_ioas`

Manage Custom Indicators of Attack (IOA) rules.

**Key capabilities:**
- Create and manage custom IOA rules
- Define behavioral detection logic
- Test and validate rules

**Common operations:**
```python
# List custom IOAs
ioas = client.custom_ioas.describe_ioas()
```

### Sensor Download Module
**Access:** `client.sensor_download`

Manage sensor installers and downloads.

**Key capabilities:**
- List available sensor installers
- Get download URLs
- Manage sensor versions

**Common operations:**
```python
# List available sensors
sensors = client.sensor_download.describe_installers()
```

## Module Architecture

All modules inherit from `FalconApiModule` and share common characteristics:

```python
from caracara.common.module import FalconApiModule

class MyApiModule(FalconApiModule):
    """Module for interacting with a specific Falcon API."""
    
    name = "My API Module"
    help = "Description of what this module does"
    
    def __init__(self, api_authentication, mapper):
        super().__init__(api_authentication, mapper)
        # Module-specific initialization
```

### Common Patterns

#### 1. Filtering

Most list/search methods accept filters:

```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
results = client.hosts.describe_devices(filters)
```

#### 2. ID-based Retrieval

Methods often come in pairs:
- `get_*_ids()`: Returns list of IDs
- `describe_*()`: Returns detailed information

```python
# Just IDs (faster if you only need IDs)
device_ids = client.hosts.get_device_ids(filters)

# Full details
devices = client.hosts.describe_devices(filters)
```

#### 3. Automatic Pagination

All list methods handle pagination automatically:

```python
# This returns ALL devices, paginating as needed
all_devices = client.hosts.describe_devices()
```

#### 4. Batch Operations

Operations on multiple items are batched and parallelized:

```python
# Efficiently retrieves details for 50,000 devices
device_ids = [...]  # 50,000 IDs
device_data = client.hosts.get_device_data(device_ids)
```

## Cross-Module Operations

Modules can work together via the `ModuleMapper`:

```python
# Get devices from hosts module
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
device_ids = client.hosts.get_device_ids(filters)

# Use those IDs in RTR module
session = client.rtr.batch_session()
session.connect(device_ids=device_ids)
results = session.run_generic_command("ps")
```

## Error Handling

All modules use consistent exception handling:

```python
from caracara.common.exceptions import (
    BaseCaracaraError,
    GenericAPIError,
    DeviceNotFound,
)

try:
    devices = client.hosts.describe_devices(filters)
except DeviceNotFound:
    print("No devices match the filter")
except GenericAPIError as e:
    print(f"API error: {e}")
except BaseCaracaraError as e:
    print(f"Caracara error: {e}")
```

## Logging

All modules support Python logging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Module operations will now log
devices = client.hosts.describe_devices(filters)
```

Logger hierarchy:
- `caracara` - Root logger
- `caracara.modules.HostsApiModule` - Hosts module
- `caracara.modules.RTRApiModule` - RTR module
- etc.

## Performance Considerations

### Automatic Optimization

Caracara automatically optimizes operations:

1. **Parallel pagination**: When possible, pages are fetched in parallel
2. **Batch data retrieval**: IDs are divided into batches and retrieved concurrently
3. **Thread pooling**: Managed thread pools prevent excessive parallelism

### Best Practices

1. **Use filters**: Always filter at the API level
   ```python
   # Good
   devices = client.hosts.describe_devices(filters)
   
   # Bad
   all_devices = client.hosts.describe_devices()
   windows_only = {k: v for k, v in all_devices.items() 
                   if v['platform_name'] == 'Windows'}
   ```

2. **Get IDs when possible**: If you only need IDs, don't fetch full details
   ```python
   # If you only need IDs
   device_ids = client.hosts.get_device_ids(filters)
   
   # If you need full details
   devices = client.hosts.describe_devices(filters)
   ```

3. **Reuse client instances**: Create one client and reuse it
   ```python
   # Good
   client = Client(...)
   for operation in operations:
       client.hosts.describe_devices(operation.filters)
   
   # Bad
   for operation in operations:
       client = Client(...)
       client.hosts.describe_devices(operation.filters)
   ```

## Module Status

| Module | Status | Completeness |
|--------|--------|--------------|
| Hosts | ✅ Stable | Full |
| RTR | ✅ Stable | Full |
| Prevention Policies | ✅ Stable | Full |
| Response Policies | ✅ Stable | Full |
| Sensor Update Policies | ✅ Stable | Full |
| Flight Control | ✅ Stable | Full |
| Users | ✅ Stable | Full |
| Custom IOA | ✅ Stable | Full |
| Sensor Download | ✅ Stable | Full |

## Further Reading

- [Architecture Overview](../architecture.md) - How modules fit together
- [Client Configuration](../client-configuration.md) - Configuring the client
- [Filtering Guide](../filtering.md) - Advanced filtering techniques
- [Pagination and Batching](../advanced/pagination-batching.md) - How data retrieval works

## Next Steps

Choose a module to learn more:

- **New to Caracara?** Start with [Hosts Module](hosts.md)
- **Need remote execution?** Check out [RTR Module](rtr.md)
- **Managing policies?** See [Prevention Policies](prevention-policies.md)
- **MSSP operations?** Read [Flight Control Module](flight-control.md)
