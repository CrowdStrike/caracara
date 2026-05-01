# Caracara Architecture Overview

This document provides a detailed overview of Caracara's architecture, design principles, and internal structure.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Caracara Client                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │           FalconPy OAuth2 Object                   │     │
│  │  (Handles authentication and token management)     │     │
│  └────────────────────────────────────────────────────┘     │
│                           │                                  │
│          ┌────────────────┴────────────────┐                │
│          │    ModuleMapper (Cross-module   │                │
│          │     communication)               │                │
│          └────────────────┬────────────────┘                │
│                           │                                  │
│    ┌──────────────────────┼──────────────────────┐          │
│    │                      │                      │          │
│ ┌──▼──────┐  ┌───────────▼─┐  ┌────────────────▼────┐     │
│ │  Hosts  │  │     RTR     │  │  Prevention Policies│     │
│ │ Module  │  │   Module    │  │      Module         │     │
│ └─────────┘  └─────────────┘  └─────────────────────┘     │
│    │              │                      │                  │
│ ┌──▼──────┐  ┌───▼─────────┐  ┌────────▼─────────────┐    │
│ │Response │  │   Flight    │  │  Sensor Update      │    │
│ │Policies │  │  Control    │  │    Policies         │    │
│ └─────────┘  └─────────────┘  └─────────────────────┘    │
│    │              │                      │                  │
│ ┌──▼──────┐  ┌───▼─────────┐                              │
│ │ Users   │  │  Custom IOA │                              │
│ │ Module  │  │   Module    │                              │
│ └─────────┘  └─────────────┘                              │
│                                                              │
│  ┌──────────────────────────────────────────────────┐     │
│  │    Common Utilities                               │     │
│  │  - Pagination (5 styles)                          │     │
│  │  - Batching (parallelized data retrieval)         │     │
│  │  - Filtering (FQL generation)                     │     │
│  │  - Exception handling                             │     │
│  │  - Logging                                        │     │
│  └──────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   CrowdStrike Falcon   │
              │        API             │
              └────────────────────────┘
```

## Core Components

### 1. Client (`caracara.client.Client`)

The `Client` class is the main entry point for all Caracara operations. It handles:

- **Authentication**: Manages the FalconPy OAuth2 object
- **Module initialization**: Creates and configures all API modules
- **Context manager support**: Allows use with Python's `with` statement
- **Environment variable interpolation**: Supports `${VAR}` syntax in configuration
- **Proxy configuration**: Handles HTTP/HTTPS proxy settings

#### Initialization Flow

```python
client = Client(
    client_id="...",
    client_secret="...",
    cloud_name="us-1",  # or "auto" for automatic detection
)
```

**What happens internally:**
1. Validates that both `client_id` and `client_secret` are provided (or uses a pre-existing FalconPy OAuth2 object)
2. Interpolates any environment variables in the configuration
3. Creates the FalconPy `OAuth2` object with provided credentials
4. Requests an API token and resolves the base URL
5. Initializes all API modules with the authentication object
6. Links modules together via the `ModuleMapper` for cross-module operations

### 2. FalconApiModule Base Class

All API modules inherit from `FalconApiModule`, which provides:

- **Consistent interface**: All modules follow the same patterns
- **Logging**: Each module has its own logger (`caracara.modules.ClassName`)
- **Authentication**: Shared OAuth2 object across all modules
- **Module mapping**: Access to other modules for cross-module operations

```python
class FalconApiModule(ABC):
    """Base class for all Caracara API modules."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The module name."""
    
    @property
    @abstractmethod
    def help(self) -> str:
        """Help text describing the module."""
    
    def __init__(self, api_authentication: OAuth2, mapper: ModuleMapper):
        """Initialize with authentication and module mapper."""
```

### 3. ModuleMapper

The `ModuleMapper` is a lightweight container that enables modules to call into one another. This is essential for operations that span multiple APIs.

**Example use case:**
- The Hosts module needs to update a host's group membership
- Groups are managed by the Host Groups API
- The module mapper allows seamless access to both APIs

### 4. Filtering System

Caracara uses the external `caracara-filters` package (which provides `FQLGenerator`) to build Falcon Query Language (FQL) filter strings.

```python
# Exposed as FalconFilter for backwards compatibility
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("LastSeen", "-7d", "LTE")

fql_string = filters.get_fql()
# Result: "platform_name:'Windows'+last_seen:<='-7d'"
```

**Key features:**
- Type-safe filter construction
- Automatic FQL syntax generation
- Support for all FQL operators (EQ, NEQ, LTE, GTE, etc.)
- Dialect-specific field name translation

## Pagination Strategies

Caracara implements five different pagination strategies to handle various API response formats:

### Style 1: Numbered Offset (Parallelized)

Used by most APIs. Requests can be parallelized because page numbers are known upfront.

```python
{
    "meta": {
        "pagination": {
            "limit": 100,
            "offset": 200,
            "total": 1500
        }
    }
}
```

**Implementation:** `all_pages_numbered_offset_parallel()`

### Style 2: Token Offset (Sequential)

Each response includes a token for the next page. Must be retrieved sequentially.

```python
{
    "meta": {
        "pagination": {
            "limit": 100,
            "offset": "next_page_token_here",
            "total": 1500
        }
    }
}
```

**Implementation:** `all_pages_token_offset()`

### Style 3: Token After (Sequential)

Similar to Style 2, but uses an `after` field instead of `offset`.

**Implementation:** `all_pages_token_offset(offset_key_named_after=True)`

### Style 4: Marker-based (Timestamp)

Used by Intel APIs. Uses FQL `_marker` for time-based pagination.

### Style 5: Generic Parallelized

For APIs that accept one ID at a time but can be parallelized across multiple IDs.

## Batching and Concurrency

### Data Batching

The `batch_get_data()` function in `caracara.common.batching` handles parallelized data retrieval:

1. **Split IDs into batches**: Default batch size is defined in `constants.py`
2. **Create thread pool**: Size is `min(cpu_count * 2, 20)`
3. **Execute requests in parallel**: Each thread requests one batch
4. **Aggregate results**: Combine all responses into a single dictionary

```python
# Example: Getting details for 50,000 device IDs
device_ids = [...]  # 50,000 IDs
device_data = batch_get_data(
    lookup_ids=device_ids,
    func=client.hosts.hosts_api.get_device_details,
    data_batch_size=5000  # Default from constants
)
# Results in 10 parallel API calls, dramatically faster than sequential
```

### Thread Pool Configuration

- **Maximum threads**: `min(cpu_count * 2, 20)`
- **Rationale**: Balance between parallelism and API rate limits
- Each thread gets its own batch and makes independent API calls

## RTR Architecture

The Real Time Response (RTR) module has a unique architecture to handle large-scale operations:

### RTR Batch Sessions

```
RTRBatchSession (Unlimited hosts)
    │
    ├─ InnerRTRBatchSession #1 (up to 10k hosts)
    ├─ InnerRTRBatchSession #2 (up to 10k hosts)
    └─ InnerRTRBatchSession #N (up to 10k hosts)
```

**Key components:**

1. **RTRBatchSession**: High-level abstraction for connecting to any number of hosts
2. **InnerRTRBatchSession**: Represents a single cloud-side batch (max 10,000 hosts)
3. **Automatic session refresh**: Prevents timeouts during long operations
4. **Thread pool execution**: Commands execute across all batches in parallel

**Example:**
```python
# Connect to 25,000 hosts
session = client.rtr.batch_session()
session.connect(device_ids=list_of_25000_ids)

# Behind the scenes: Creates 3 InnerRTRBatchSession objects
# Commands are automatically distributed across all sessions
result = session.run_generic_command("ps")
```

## Exception Hierarchy

```
BaseCaracaraError
    ├─ GenericAPIError
    │   ├─ MustProvideFilter
    │   ├─ MustProvideFilterOrID
    │   ├─ DeviceNotFound
    │   ├─ HostGroupNotFound
    │   ├─ MissingArgument
    │   ├─ MissingArguments
    │   └─ InvalidOnlineState
    └─ (Future custom exceptions)
```

All exceptions inherit from `BaseCaracaraError`, making it easy to catch all Caracara-specific errors:

```python
from caracara.common.exceptions import BaseCaracaraError

try:
    devices = client.hosts.describe_devices(filters)
except BaseCaracaraError as e:
    print(f"Caracara error: {e}")
```

## Design Principles

### 1. Fail-Safe Defaults

- SSL verification enabled by default
- Reasonable timeouts
- Safe batch sizes to avoid rate limiting

### 2. Explicit Over Implicit

- All required parameters must be provided
- No silent failures or assumptions
- Clear error messages when operations fail

### 3. IDE-Friendly

- Full type hints on all public methods
- Descriptive docstrings
- Consistent naming conventions

### 4. Performance-Oriented

- Automatic parallelization where possible
- Efficient batching strategies
- Minimal API calls through smart caching

### 5. Logging Throughout

Every significant operation logs at appropriate levels:
- `DEBUG`: Verbose details, API responses
- `INFO`: High-level operation progress
- `ERROR`: Failures and exceptions

### 6. Backward Compatibility

- `FalconFilter` maintained for legacy code (wraps `FQLGenerator`)
- Stable public APIs
- Deprecation warnings before removal

## File Organization

```
caracara/
├── __init__.py               # Package entry point
├── client.py                 # Client class
├── common/                   # Shared utilities
│   ├── batching.py          # Parallel batch data retrieval
│   ├── pagination.py        # All pagination styles
│   ├── constants.py         # Shared constants
│   ├── decorators.py        # Utility decorators
│   ├── exceptions.py        # Exception classes
│   ├── interpolation.py     # Environment variable interpolation
│   ├── module.py            # Base module classes
│   ├── meta.py              # Version and metadata
│   ├── policy_wrapper.py    # Policy object abstraction
│   ├── sorting.py           # Sorting utilities
│   └── csdialog.py          # CLI dialog utilities
├── filters/                  # FQL filter system
│   ├── __init__.py          # FalconFilter (wraps FQLGenerator)
│   └── decorators.py        # Filter decorators
└── modules/                  # API modules
    ├── __init__.py
    ├── hosts/               # Hosts and host groups
    │   ├── hosts.py
    │   ├── _containment.py
    │   ├── _groups.py
    │   ├── _hiding.py
    │   ├── _online_state.py
    │   ├── _tagging.py
    │   └── _data_history.py
    ├── rtr/                 # Real Time Response
    │   ├── rtr.py
    │   ├── batch_session.py
    │   ├── get_file.py
    │   └── constants.py
    ├── prevention_policies/
    ├── response_policies/
    ├── sensor_update_policies/
    ├── flight_control/
    ├── users/
    └── custom_ioa/
```

## Next Steps

- [Client Configuration](client-configuration.md) - Configure authentication and options
- [Filtering with FQL](filtering.md) - Master the filter system
- [Hosts Module](modules/hosts.md) - Work with devices
- [Advanced Topics](advanced/pagination-batching.md) - Deep dive into internals
