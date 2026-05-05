# Filtering with FQL (Falcon Query Language)

Caracara provides an object-oriented interface to build Falcon Query Language (FQL) filters, making it easy to search for devices, policies, and other resources.

## Overview

The `FalconFilter` class (actually `FQLGenerator` from the `caracara-filters` package) constructs FQL filter strings for you, handling:
- Proper FQL syntax and escaping
- Field name translation (dialect-specific)
- Operator handling
- Multiple filter combination with AND logic

## Basic Usage

```python
from caracara import Client

client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)

# Create a filter object
filters = client.FalconFilter(dialect="hosts")

# Add filter conditions
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("LastSeen", "-7d", "LTE")

# Use the filter
devices = client.hosts.describe_devices(filters)
```

## Creating Filters

### The FalconFilter Class

```python
# Create a filter for hosts
filters = client.FalconFilter(dialect="hosts")

# Create a filter for another dialect
user_filters = client.FalconFilter(dialect="users")
```

The `dialect` parameter tells the filter system which field names to use. Different Falcon APIs use different field naming conventions.

### Adding Filter Conditions

#### `create_new_filter(name, value, operator="EQ")`

Add a filter condition to the filter object.

**Parameters:**
- `name` (str): Field name (dialect-specific, e.g., "OS", "Hostname", "LastSeen")
- `value` (str): Value to filter on
- `operator` (str, optional): Comparison operator (default: "EQ")

**Available Operators:**
- `EQ`: Equal to (default)
- `NEQ`: Not equal to
- `GT`: Greater than
- `GTE`: Greater than or equal to
- `LT`: Less than
- `LTE`: Less than or equal to

**Examples:**
```python
filters = client.FalconFilter(dialect="hosts")

# Equal to (default operator)
filters.create_new_filter("OS", "Windows")

# Not equal to
filters.create_new_filter("OS", "Mac", "NEQ")

# Less than or equal to (for dates)
filters.create_new_filter("LastSeen", "-7d", "LTE")

# Greater than
filters.create_new_filter("AgentVersion", "7.0.0", "GT")
```

### Getting the FQL String

#### `get_fql()`

Returns the constructed FQL string.

```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("Status", "normal")

fql_string = filters.get_fql()
print(fql_string)
# Output: platform_name:'Windows'+status:'normal'
```

## Common Filter Fields

### Hosts Dialect

Common field names when using `dialect="hosts"`:

| Filter Name | FQL Field | Description | Example Values |
|------------|-----------|-------------|----------------|
| `OS` | `platform_name` | Operating system | "Windows", "Linux", "Mac" |
| `Hostname` | `hostname` | Device hostname | "WORKSTATION-01" |
| `LastSeen` | `last_seen` | Last check-in time | "-7d", "2024-01-01" |
| `FirstSeen` | `first_seen` | First check-in time | "-30d" |
| `Status` | `status` | Device status | "normal", "contained" |
| `Role` | `device_policies.role` | Device role | "Server", "Workstation" |
| `OU` | `ou` | Organizational Unit | "Sales", "IT" |
| `SiteName` | `site_name` | Active Directory site | "HQ", "Branch1" |
| `AgentVersion` | `agent_version` | Sensor version | "7.10.12345" |
| `ProductType` | `product_type_desc` | Product type | "Workstation", "Server" |
| `LocalIP` | `local_ip` | Internal IP address | "192.168.1.100" |
| `ExternalIP` | `external_ip` | External IP address | "203.0.113.50" |
| `MACAddress` | `mac_address` | MAC address | "00:11:22:33:44:55" |

## Filter Examples

### By Operating System

```python
# Windows devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")

# Linux devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Linux")

# Not Mac devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Mac", "NEQ")
```

### By Time (Relative)

```python
# Devices not seen in 7 days
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("LastSeen", "-7d", "LTE")

# Devices first seen in the last 24 hours (new devices)
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("FirstSeen", "-24h", "GTE")

# Devices last seen more than 30 days ago
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("LastSeen", "-30d", "LTE")
```

**Time format:**
- `-7d`: 7 days ago
- `-24h`: 24 hours ago
- `-1h`: 1 hour ago
- `-30m`: 30 minutes ago

### By Time (Absolute)

```python
# Devices last seen after a specific date
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("LastSeen", "2024-01-01T00:00:00Z", "GTE")

# Devices last seen between two dates
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("LastSeen", "2024-01-01T00:00:00Z", "GTE")
filters.create_new_filter("LastSeen", "2024-02-01T00:00:00Z", "LTE")
```

### By Hostname

```python
# Exact hostname match
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Hostname", "WORKSTATION-01")

# Wildcard matching (using FQL wildcards)
# Note: Wildcards must be in the FQL itself, not handled by FalconFilter
```

### By Product Type

```python
# Servers only
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("ProductType", "Server")

# Workstations only
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("ProductType", "Workstation")
```

### By Agent Version

```python
# Specific version
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("AgentVersion", "7.10.12345")

# Older than a version
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("AgentVersion", "7.0.0", "LT")
```

### By Network

```python
# Specific local IP
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("LocalIP", "192.168.1.100")

# Specific subnet (requires raw FQL)
fql_string = "local_ip:>'192.168.1.0'+local_ip:<'192.168.1.255'"
devices = client.hosts.describe_devices(fql_string)
```

### By Status

```python
# Normal devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Status", "normal")

# Contained devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("Status", "contained")
```

### Multiple Filters (AND Logic)

```python
# Windows servers not seen in 7 days
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("ProductType", "Server")
filters.create_new_filter("LastSeen", "-7d", "LTE")

# Translates to:
# platform_name:'Windows'+product_type_desc:'Server'+last_seen:<='-7d'
```

## Advanced Usage

### Using Raw FQL Strings

If `FalconFilter` doesn't support your use case, you can pass raw FQL strings directly:

```python
# Raw FQL string
fql_string = "platform_name:'Windows'+hostname:*'DC-'*"
devices = client.hosts.describe_devices(fql_string)
```

### Combining FalconFilter with Raw FQL

You can build part of the filter with `FalconFilter` and extend it:

```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")

base_fql = filters.get_fql()
# base_fql = "platform_name:'Windows'"

# Add custom FQL
extended_fql = f"{base_fql}+hostname:*'DC-'*"
devices = client.hosts.describe_devices(extended_fql)
```

### Wildcard Patterns

FQL supports wildcards, but they must be included in raw FQL strings:

**Wildcard operators:**
- `*`: Matches any characters
- `?`: Matches a single character

**Examples:**
```python
# Hostnames starting with "WEB-"
fql = "hostname:*'WEB-'*"

# Hostnames ending with "-PROD"
fql = "hostname:*'-PROD'*"

# Hostnames containing "DATABASE"
fql = "hostname:*'DATABASE'*"

# Complex pattern
fql = "hostname:*'WEB-??-PROD'*"  # WEB-01-PROD, WEB-02-PROD, etc.
```

### OR Logic

FQL supports OR logic using commas. This must be done with raw FQL:

```python
# Windows OR Linux (using raw FQL)
fql = "platform_name:'Windows',platform_name:'Linux'"
devices = client.hosts.describe_devices(fql)

# Multiple values for same field
fql = "hostname:'SERVER01',hostname:'SERVER02',hostname:'SERVER03'"
devices = client.hosts.describe_devices(fql)
```

### NOT Logic

```python
# Not Windows (using FalconFilter)
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows", "NEQ")

# Not in a specific subnet (using raw FQL with ! operator)
fql = "!local_ip:>'192.168.1.0'+!local_ip:<'192.168.1.255'"
devices = client.hosts.describe_devices(fql)
```

### Nested Fields

Some fields are nested in the API response. Use dot notation:

```python
# Raw FQL for nested fields
fql = "device_policies.prevention.policy_id:'abc123...'"
devices = client.hosts.describe_devices(fql)
```

## Common Filter Patterns

### Stale Sensors Report

```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("LastSeen", "-30d", "LTE")
filters.create_new_filter("Status", "normal")  # Exclude contained devices

stale = client.hosts.describe_devices(filters)
print(f"Found {len(stale)} stale sensors")
```

### New Devices in Last 24 Hours

```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("FirstSeen", "-24h", "GTE")

new_devices = client.hosts.describe_devices(filters)
print(f"New devices: {len(new_devices)}")

for device_id, device in new_devices.items():
    print(f"  {device['hostname']} - {device['platform_name']}")
```

### Production Windows Servers

```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("ProductType", "Server")
# Add a tag filter (raw FQL)
base_fql = filters.get_fql()
fql = f"{base_fql}+tags:'FalconGroupingTags/Environment/Production'"

prod_servers = client.hosts.describe_devices(fql)
```

### Devices by Version Range

```python
# Sensors older than version 7.0
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("AgentVersion", "7.0", "LT")

old_sensors = client.hosts.describe_devices(filters)
```

### Devices by IP Range

For IP ranges, raw FQL is more practical:

```python
# Devices in 192.168.1.0/24
fql = "local_ip:>'192.168.1.0'+local_ip:<'192.168.1.255'"
devices = client.hosts.describe_devices(fql)

# Specific IPs
fql = "local_ip:'192.168.1.10',local_ip:'192.168.1.20'"
devices = client.hosts.describe_devices(fql)
```

### Devices Missing from a Group

This requires multiple API calls:

```python
# Get all device IDs
all_devices = set(client.hosts.get_device_ids())

# Get group member IDs
group_members = set(client.hosts.get_group_member_ids(group_id="group_id"))

# Find devices not in the group
not_in_group = all_devices - group_members
```

## Testing Filters

### In Caracara

```python
# Create filter
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")

# Print the FQL to verify
print(f"FQL: {filters.get_fql()}")

# Test it
devices = client.hosts.describe_devices(filters)
print(f"Found {len(devices)} devices")
```

### In Falcon UI

You can test FQL filters in the Falcon console:

1. Navigate to **Host Management** → **Devices**
2. Click the filter bar
3. Paste your FQL string
4. Verify results

This is useful for debugging complex filters before using them in code.

## FQL Reference

### Operators

| Operator | FQL Syntax | Description |
|----------|------------|-------------|
| Equal | `:` | Exact match |
| Not Equal | `:!` | Does not match |
| Greater Than | `:>` | Greater than |
| Greater Than or Equal | `:>=` | Greater than or equal to |
| Less Than | `:<` | Less than |
| Less Than or Equal | `:<=` | Less than or equal to |
| Contains | `:*` | Wildcard match |

### Logical Operators

| Operator | FQL Syntax | Description |
|----------|------------|-------------|
| AND | `+` | All conditions must match |
| OR | `,` | Any condition can match |
| NOT | `!` | Negates a condition |

### Examples in Raw FQL

```python
# AND: Windows servers
fql = "platform_name:'Windows'+product_type_desc:'Server'"

# OR: Windows or Linux
fql = "platform_name:'Windows',platform_name:'Linux'"

# NOT: Not Windows
fql = "!platform_name:'Windows'"

# Complex: (Windows OR Linux) AND Server
fql = "(platform_name:'Windows',platform_name:'Linux')+product_type_desc:'Server'"

# Wildcard: Hostname contains "WEB"
fql = "hostname:*'WEB'*"

# Date range
fql = "last_seen:>='-30d'+last_seen:<='-7d'"
```

## Best Practices

### 1. Filter at the API Level

Always filter at the API level rather than retrieving all data and filtering locally:

```python
# Good: Filter at API level
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
devices = client.hosts.describe_devices(filters)

# Bad: Retrieve everything and filter locally
all_devices = client.hosts.describe_devices()
windows = {k: v for k, v in all_devices.items() if v['platform_name'] == 'Windows'}
```

### 2. Use Specific Filters

The more specific your filter, the faster the API response:

```python
# Better: Specific filter
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("ProductType", "Server")
filters.create_new_filter("LastSeen", "-7d", "LTE")

# Worse: Broad filter
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
# Then filtering the results in code
```

### 3. Test Complex Filters

For complex filters, test them in the Falcon UI first to ensure they work as expected.

### 4. Use Raw FQL When Needed

Don't force complex logic into `FalconFilter` - use raw FQL strings when appropriate:

```python
# Complex OR logic - use raw FQL
fql = "(hostname:'SERVER01',hostname:'SERVER02')+platform_name:'Windows'"
devices = client.hosts.describe_devices(fql)
```

### 5. Document Your Filters

```python
# Clearly document what your filter does
# Filter: Production Windows servers not seen in 7+ days
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("ProductType", "Server")
filters.create_new_filter("LastSeen", "-7d", "LTE")
base_fql = filters.get_fql()
fql = f"{base_fql}+tags:'FalconGroupingTags/Environment/Production'"
```

## Troubleshooting

### "No results returned"

1. **Print the FQL**: `print(filters.get_fql())`
2. **Test in Falcon UI**: Verify the filter works there
3. **Check field names**: Ensure you're using the correct field names for the dialect
4. **Verify data exists**: Confirm devices matching your criteria exist

### "Unexpected results"

1. **AND vs OR**: Remember that `FalconFilter` uses AND logic between filters
2. **Operator precedence**: Be careful with complex logic - use parentheses in raw FQL
3. **Date formats**: Ensure dates are in the correct format

### "Filter syntax error"

1. **Escaping**: FQL values should be quoted (`'value'`)
2. **Special characters**: Some characters may need escaping
3. **Use raw FQL**: For complex patterns, write the FQL directly

## Next Steps

- [Hosts Module](../modules/hosts.md) - Apply filters to device queries
- [Pagination and Batching](../advanced/pagination-batching.md) - Understand how filtered results are retrieved
- [FalconPy FQL Documentation](https://falconpy.io/Service-Collections/Hosts.html#querydevicesbyfil) - Official FQL reference
