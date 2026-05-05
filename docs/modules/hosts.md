# Hosts Module

The Hosts module (`client.hosts`) provides comprehensive functionality for managing devices (hosts) and host groups within your CrowdStrike Falcon tenant.

## Overview

The Hosts module is one of the most frequently used Caracara modules, providing access to:
- Device inventory and details
- Host groups management
- Device containment operations
- Device tagging
- Login and network history
- Device online state monitoring
- Device visibility (hide/unhide)

## Key Design Principle: Filter-First API

**Important:** Most device action methods in Caracara accept **filters**, not device IDs. This is a deliberate design choice that simplifies common operations.

Instead of this two-step process:
```python
# Get device IDs first
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "compromised-server")
device_ids = client.hosts.get_device_ids(filters)

# Then perform action
some_action(device_ids)
```

Caracara lets you do this in one step:
```python
# Single step - filter is automatically converted to device IDs internally
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "compromised-server")
client.hosts.contain(filters)  # Internally gets IDs and performs action
```

This pattern reflects how Falcon administrators think: in terms of device categories and attributes, not lists of device IDs.

## Quick Start

```python
from caracara import Client

client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret",
)

# Get all Windows devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
devices = client.hosts.describe_devices(filters)

for device_id, device_data in devices.items():
    print(f"{device_data['hostname']} - {device_data['platform_name']}")
```

## Device Operations

### Querying Devices

#### `describe_devices(filters=None, online_state=None, enrich_with_online_state=False)`

Get detailed information about devices matching the specified filters. This is the most commonly used method.

**Parameters:**
- `filters` (FalconFilter | str, optional): FQL filter to apply
- `online_state` (str, optional): Filter by online state ("online", "offline", "unknown")
- `enrich_with_online_state` (bool, optional): Add online state to each device's data

**Returns:** `Dict[str, Dict]` - Device ID → device data dictionary

**Example:**
```python
# Get all Windows devices that haven't checked in within 7 days
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("LastSeen", "-7d", "LTE")

stale_devices = client.hosts.describe_devices(filters)

for device_id, device in stale_devices.items():
    print(f"{device['hostname']} last seen: {device['last_seen']}")
```

**Example with online state:**
```python
# Get only online Linux devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Linux")

online_linux = client.hosts.describe_devices(
    filters,
    online_state="online",
    enrich_with_online_state=True
)

for device_id, device in online_linux.items():
    print(f"{device['hostname']} - State: {device['state']}")
```

#### `get_device_ids(filters=None, online_state=None)`

Get just the device IDs without full details. Useful when you only need IDs for further operations.

**Parameters:**
- `filters` (FalconFilter | str, optional): FQL filter to apply
- `online_state` (str, optional): Filter by online state

**Returns:** `List[str]` - List of device IDs

**Example:**
```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Mac")

mac_device_ids = client.hosts.get_device_ids(filters)
print(f"Found {len(mac_device_ids)} Mac devices")
```

#### `get_device_data(device_ids)`

Get detailed data for specific device IDs. Use this when you already have device IDs and want their details.

**Parameters:**
- `device_ids` (List[str]): List of device IDs to retrieve

**Returns:** `Dict[str, Dict]` - Device ID → device data dictionary

**Example:**
```python
known_device_ids = ["abc123...", "def456..."]
device_details = client.hosts.get_device_data(known_device_ids)
```

### Device Online State

#### `get_online_state(device_ids)`

Get the current online state for specific devices.

**Parameters:**
- `device_ids` (List[str]): Device IDs to check

**Returns:** `Dict[str, Dict]` - Device ID → state dictionary with `'state'` key

**Example:**
```python
device_ids = client.hosts.get_device_ids()
states = client.hosts.get_online_state(device_ids)

for device_id, data in states.items():
    print(f"{device_id}: {data['state']}")
```

#### Valid Online States

- `"online"`: Device is currently connected to Falcon
- `"offline"`: Device is not connected to Falcon
- `"unknown"`: State cannot be determined

## Device Containment

**Network containment** in Falcon isolates a device from the network while maintaining its connection to the CrowdStrike cloud. This allows security teams to prevent lateral movement during an incident while still being able to investigate and remediate the device.

**Important:** Containment methods accept filters, not device IDs directly.

#### `contain(filters)`

Contain (network isolate) devices matching the specified filters.

**Parameters:**
- `filters` (FalconFilter | str, required): Filters to identify devices to contain

**Returns:** `Dict` - API response with containment results

**Raises:** `MustProvideFilter` if filters is None

**Example:**
```python
# Contain devices by hostname
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "compromised-server-01")
result = client.hosts.contain(filters)

# Contain all devices with a specific tag
filters = client.FalconFilter(dialect="hosts")
# Use raw FQL for tag filtering
fql = "tags:'FalconGroupingTags/IncidentResponse/Compromised'"
client.hosts.contain(fql)
```

**Working with specific device IDs:**
If you have specific device IDs, create a filter from them:
```python
device_ids = ["abc123...", "def456..."]

# Option 1: Single device - use device_id filter
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("device_id", device_ids[0])
client.hosts.contain(filters)

# Option 2: Multiple devices - use raw FQL with OR logic
id_filter = ",".join([f"device_id:'{id}'" for id in device_ids])
# Results in: "device_id:'abc123...',device_id:'def456...'"
client.hosts.contain(id_filter)
```

#### `release(filters)`

Release (lift containment from) devices matching the specified filters.

**Parameters:**
- `filters` (FalconFilter | str, required): Filters to identify devices to release

**Returns:** `Dict` - API response with release results

**Raises:** `MustProvideFilter` if filters is None

**Example:**
```python
# Release devices after investigation complete
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "compromised-server-01")
client.hosts.release(filters)
```

## Host Groups

Host groups in Falcon allow you to organize devices for policy assignment and management. Groups can be **static** (manually managed membership) or **dynamic** (automatically populated based on rules).

### Group Management

#### `describe_groups(filters=None, group_ids=None)`

Get detailed information about host groups.

**Parameters:**
- `filters` (FalconFilter | str, optional): FQL filter for groups
- `group_ids` (List[str], optional): Specific group IDs to retrieve

**Returns:** `Dict[str, Dict]` - Group ID → group data dictionary

**Example:**
```python
# Get all groups
all_groups = client.hosts.describe_groups()

for group_id, group in all_groups.items():
    print(f"{group['name']}: {group.get('host_ids_count', 0)} members")

# Get specific groups
specific_groups = client.hosts.describe_groups(
    group_ids=["group123...", "group456..."]
)
```

#### `get_group_ids(filters=None)`

Get list of group IDs matching filters.

**Parameters:**
- `filters` (FalconFilter | str, optional): FQL filter for groups

**Returns:** `List[str]` - List of group IDs

#### `create_group(group_name, description="", group_type="static", assignment_rule="")`

Create a new host group in Falcon.

**Parameters:**
- `group_name` (str, required): Group name
- `description` (str, optional): Group description
- `group_type` (str, optional): "static" or "dynamic" (default: "static")
- `assignment_rule` (str, optional): FQL assignment rule for dynamic groups

**Returns:** `Dict` - Group creation result with group ID

**Example:**
```python
# Create a static group
web_servers_group = client.hosts.create_group(
    group_name="Web Servers",
    description="All production web servers",
    group_type="static"
)

# Create a dynamic group
windows_servers = client.hosts.create_group(
    group_name="Windows Servers",
    description="All Windows Server OS",
    group_type="dynamic",
    assignment_rule="platform_name:'Windows'+product_type_desc:'Server'"
)
```

#### `update_group(group_ids=None, filters=None, name=None, description=None, assignment_rule=None)`

Update an existing host group's properties.

**Parameters:**
- `group_ids` (List[str] | str, optional): Group IDs to update
- `filters` (FalconFilter, optional): Filter to identify groups
- `name` (str, optional): New name
- `description` (str, optional): New description
- `assignment_rule` (str, optional): New assignment rule (dynamic groups only)

**Example:**
```python
client.hosts.update_group(
    group_ids=web_servers_group['id'],
    description="All production and staging web servers"
)
```

#### `delete_group(group_ids=None, filters=None)`

Delete a host group from Falcon.

**Parameters:**
- `group_ids` (List[str] | str, optional): Group IDs to delete
- `filters` (FalconFilter, optional): Filter to identify groups

**Example:**
```python
client.hosts.delete_group(group_ids="old_group_id")
```

### Group Membership

#### `describe_group_members(filters=None)`

Get detailed device information for group members.

**Parameters:**
- `filters` (FalconFilter, optional): Filter to identify the group

**Returns:** `Dict[str, Dict]` - Device ID → device data dictionary

**Example:**
```python
# Get all members of a group by filter
filters = client.FalconFilter(dialect="host_groups")
filters.create_new_filter("Name", "Web Servers")
members = client.hosts.describe_group_members(filters)

for device_id, device in members.items():
    print(f"{device['hostname']}")
```

#### `get_group_member_ids(group_id)`

Get device IDs for members of a specific group.

**Parameters:**
- `group_id` (str, required): Group ID

**Returns:** `List[str]` - List of device IDs in the group

**Example:**
```python
member_ids = client.hosts.get_group_member_ids("abc123...")
print(f"Group has {len(member_ids)} members")
```

#### `add_to_group()` / `group()`

Add devices to a static host group. `group()` is an alias for `add_to_group()`.

**Parameters (flexible combinations):**
- `filters` (FalconFilter | str, optional): Filter to identify group(s)
- `group_ids` (List[str] | str, optional): Specific group ID(s)
- `device_filters` (FalconFilter | str, optional): Filter to identify devices
- `device_ids` (List[str] | str, optional): Specific device ID(s)

**Returns:** `Dict` - Group update result

**You must provide:**
- Either `filters` OR `group_ids` (to identify the group)
- Either `device_filters` OR `device_ids` (to identify devices to add)

**Examples:**
```python
# Option 1: Specific group ID and device IDs
client.hosts.add_to_group(
    group_ids="abc123...",
    device_ids=["dev1...", "dev2..."]
)

# Option 2: Using filters for both
group_filters = client.FalconFilter(dialect="host_groups")
group_filters.create_new_filter("Name", "Production Servers")

device_filters = client.FalconFilter(dialect="hosts")
device_filters.create_new_filter("OS", "Windows")
device_filters.create_new_filter("ProductType", "Server")

client.hosts.add_to_group(
    filters=group_filters,
    device_filters=device_filters
)

# Option 3: Mix - group ID with device filters
device_filters = client.FalconFilter(dialect="hosts")
device_filters.create_new_filter("Hostname", "web-*")

client.hosts.add_to_group(
    group_ids="abc123...",
    device_filters=device_filters
)

# Using the alias
client.hosts.group(group_ids="abc123...", device_ids=["dev1..."])
```

#### `remove_from_group()` / `ungroup()`

Remove devices from a static host group. `ungroup()` is an alias.

**Parameters:** Same as `add_to_group()`

**Example:**
```python
# Remove specific devices from a group
client.hosts.remove_from_group(
    group_ids="abc123...",
    device_ids=["dev1...", "dev2..."]
)

# Using the alias
client.hosts.ungroup(group_ids="abc123...", device_ids=["dev1..."])
```

## Device Tagging

Tags in Falcon provide flexible, custom metadata for devices. Tags follow the format `FalconGroupingTags/Category/Value`.

**Important:** Tag methods accept `tags` as the first parameter and `filters` to identify devices.

#### `tag(tags, filters)`

Add tags to devices matching the specified filters.

**Parameters:**
- `tags` (List[str] | str, required): Tags to add (format: "FalconGroupingTags/key/value")
- `filters` (FalconFilter | str, required): Filters to identify devices

**Returns:** `Dict` - Tagging result

**Raises:** `MustProvideFilter` if filters is None

**Example:**
```python
# Tag devices by filter
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "web-server-*")

client.hosts.tag(
    tags=["FalconGroupingTags/Environment/Production", "FalconGroupingTags/Owner/WebTeam"],
    filters=filters
)

# Single tag (can pass string instead of list)
client.hosts.tag(
    tags="FalconGroupingTags/Reviewed/2024",
    filters=filters
)
```

#### `untag(tags, filters)`

Remove tags from devices matching the specified filters.

**Parameters:**
- `tags` (List[str] | str, required): Tags to remove
- `filters` (FalconFilter | str, required): Filters to identify devices

**Returns:** `Dict` - Untagging result

**Example:**
```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "web-server-*")

client.hosts.untag(
    tags=["FalconGroupingTags/Environment/Staging"],
    filters=filters
)
```

## Device Visibility

Falcon allows hiding devices from the console while keeping them protected. This is useful for decommissioned or test devices.

**Important:** Hide/unhide methods accept filters, not device IDs.

#### `hide(filters)`

Hide devices from the Falcon console (they remain protected).

**Parameters:**
- `filters` (FalconFilter | str, required): Filters to identify devices to hide

**Returns:** `Dict` - Hide operation result

**Raises:** `MustProvideFilter` if filters is None

**Example:**
```python
# Hide test/development machines
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "test-*")
client.hosts.hide(filters)

# From example code - hide stale sensors
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("LastSeen", "-30d", "LTE")
remove_result = client.hosts.hide(filters)
```

#### `unhide(filters)`

Unhide previously hidden devices.

**Parameters:**
- `filters` (FalconFilter | str, required): Filters to identify devices to unhide

**Returns:** `Dict` - Unhide operation result

**Example:**
```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "test-server-01")
client.hosts.unhide(filters)
```

#### `describe_hidden_devices(filters=None)`

Get details for hidden devices.

**Parameters:**
- `filters` (FalconFilter | str, optional): Additional filters

**Returns:** `Dict[str, Dict]` - Device ID → device data dictionary

#### `get_hidden_ids(filters=None)`

Get IDs of hidden devices.

**Parameters:**
- `filters` (FalconFilter | str, optional): Additional filters

**Returns:** `List[str]` - List of hidden device IDs

## Data History

### Login History

#### `describe_login_history(device_id)`

Get login history for a specific device.

**Parameters:**
- `device_id` (str, required): Device ID

**Returns:** `Dict` - Login history data

**Example:**
```python
login_history = client.hosts.describe_login_history("abc123...")

for login in login_history.get('resources', []):
    print(f"User: {login.get('user_name')} at {login.get('login_time')}")
```

### Network Address History

#### `describe_network_address_history(device_id)`

Get network address change history for a device.

**Parameters:**
- `device_id` (str, required): Device ID

**Returns:** `Dict` - Network history data

**Example:**
```python
network_history = client.hosts.describe_network_address_history("abc123...")

for change in network_history.get('resources', []):
    print(f"IP: {change.get('local_ip')} at {change.get('timestamp')}")
```

### Device State

#### `describe_state(device_ids=None, filters=None)`

Get detailed state information for devices.

**Parameters:**
- `device_ids` (List[str], optional): Specific device IDs
- `filters` (FalconFilter, optional): Filter for devices

**Returns:** `Dict` - State information

## Common Patterns

### Finding Stale Sensors

```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("LastSeen", "-7d", "LTE")

stale_devices = client.hosts.describe_devices(filters)
print(f"Found {len(stale_devices)} devices that haven't checked in for 7+ days")
```

### Operating System Distribution

```python
all_devices = client.hosts.describe_devices()

os_count = {}
for device_id, device in all_devices.items():
    os = device.get('platform_name', 'Unknown')
    os_count[os] = os_count.get(os, 0) + 1

for os, count in os_count.items():
    print(f"{os}: {count} devices")
```

### Organizing Devices by Group

```python
# Create groups for different environments
prod_group = client.hosts.create_group(
    group_name="Production",
    description="Production environment",
    group_type="dynamic",
    assignment_rule="tags:'FalconGroupingTags/Environment/Production'"
)

dev_group = client.hosts.create_group(
    group_name="Development",
    description="Development environment",
    group_type="dynamic",
    assignment_rule="tags:'FalconGroupingTags/Environment/Development'"
)
```

### Incident Response Workflow

```python
# 1. Find compromised devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "compromised-*")
compromised = client.hosts.describe_devices(filters)

# 2. Contain them using the same filter
client.hosts.contain(filters)

# 3. Tag for tracking
client.hosts.tag(
    tags=["FalconGroupingTags/IncidentResponse/Q1-2024-Incident"],
    filters=filters
)

# 4. Add to an incident response group
# Option A: If you have the group ID
ir_group_id = "..."
client.hosts.add_to_group(
    group_ids=ir_group_id,
    device_filters=filters
)

# Option B: If you have specific device IDs from the compromised dict
device_ids = list(compromised.keys())
id_filter = ",".join([f"device_id:'{id}'" for id in device_ids])
client.hosts.add_to_group(
    group_ids=ir_group_id,
    device_filters=id_filter
)

# Later, after remediation:
# 5. Release from containment
client.hosts.release(filters)

# 6. Remove from IR group
client.hosts.remove_from_group(
    group_ids=ir_group_id,
    device_filters=filters
)
```

### Working with Specific Device IDs

Since most methods require filters, here's how to work with specific device IDs:

```python
# You have a list of specific device IDs
specific_ids = ["abc123...", "def456...", "ghi789..."]

# Option 1: Single device - use device_id filter
if len(specific_ids) == 1:
    filters = client.FalconFilter(dialect="hosts")
    filters.create_new_filter("device_id", specific_ids[0])
    client.hosts.contain(filters)

# Option 2: Multiple devices - use raw FQL with OR logic
device_id_filter = ",".join([f"device_id:'{id}'" for id in specific_ids])
# Results in: "device_id:'abc123...',device_id:'def456...',device_id:'ghi789...'"
client.hosts.contain(device_id_filter)
```

### Conditional Actions Based on Device Data

```python
# Step 1: Get device data to inspect
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
devices = client.hosts.describe_devices(filters)

# Step 2: Decide which ones to act on based on data
devices_needing_attention = []
for device_id, device in devices.items():
    agent_version = device.get('agent_version', '')
    if agent_version.startswith('6.'):
        # Old agent version - flag for upgrade
        devices_needing_attention.append(device_id)

# Step 3: Build filter from those specific IDs and act
if devices_needing_attention:
    id_filter = ",".join([f"device_id:'{id}'" for id in devices_needing_attention])
    
    # Tag them for tracking
    client.hosts.tag(
        tags="FalconGroupingTags/NeedsUpgrade/AgentV6",
        filters=id_filter
    )
```

## Performance Considerations

### Automatic Batching

All device data retrieval methods automatically batch requests:
- Device IDs are split into batches (default: 5000 per batch)
- Batches are retrieved in parallel using thread pools
- Results are automatically aggregated

**Impact:** Retrieving 50,000 devices takes approximately the same time as 5,000 devices.

### Filtering Performance

- Always filter at the API level (using `filters` parameter) rather than retrieving all devices and filtering locally
- Use specific filters to reduce the result set size
- Consider using `get_device_ids()` if you only need IDs, not full device data

```python
# Good: Filter at API level
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
windows_devices = client.hosts.describe_devices(filters)

# Bad: Retrieve everything and filter locally
all_devices = client.hosts.describe_devices()  # Retrieves ALL devices!
windows_devices = {k: v for k, v in all_devices.items() 
                   if v.get('platform_name') == 'Windows'}
```

## Device Data Structure

Devices returned by `describe_devices()` and `get_device_data()` contain rich information:

```python
{
    "device_id": "abc123...",
    "hostname": "WORKSTATION-01",
    "platform_name": "Windows",
    "os_version": "Windows 10",
    "product_type_desc": "Workstation",
    "last_seen": "2024-05-01T12:30:00Z",
    "first_seen": "2024-01-15T08:00:00Z",
    "local_ip": "192.168.1.100",
    "external_ip": "203.0.113.50",
    "mac_address": "00:11:22:33:44:55",
    "agent_version": "7.10.12345",
    "status": "normal",
    "reduced_functionality_mode": "no",
    "tags": ["FalconGroupingTags/Environment/Production"],
    # ... many more fields
}
```

## Next Steps

- [RTR Module](rtr.md) - Remote command execution on devices
- [Prevention Policies](prevention-policies.md) - Configure security policies for groups
- [Filtering Guide](../filtering.md) - Advanced filtering techniques
