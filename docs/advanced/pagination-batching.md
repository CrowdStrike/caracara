# Pagination and Batching

Caracara automatically handles pagination and batching to efficiently retrieve large datasets from the Falcon API. This document explains how these systems work internally.

## Overview

The Falcon API uses pagination to limit the amount of data returned in a single response. Caracara abstracts this complexity, automatically:

1. **Paginating** through all pages to get complete ID lists
2. **Batching** ID lists into manageable chunks
3. **Parallelizing** batch requests using thread pools
4. **Aggregating** results into a single data structure

## Pagination Strategies

Caracara implements five different pagination strategies to handle various API response formats.

### Style 1: Numbered Offset (Parallelized)

**Used by:** Most list endpoints (hosts, groups, policies, etc.)

**How it works:**
1. First request returns total item count
2. Calculate number of pages needed: `ceil(total / limit)`
3. Request all pages in parallel using thread pool
4. Combine results from all threads

**API Response Structure:**
```json
{
    "meta": {
        "pagination": {
            "limit": 100,
            "offset": 0,
            "total": 5432
        }
    },
    "resources": ["id1", "id2", ...]
}
```

**Implementation:** `all_pages_numbered_offset_parallel()`

**Example internal flow:**
```
Total: 5432 items, Limit: 100 per page
→ 55 pages needed (5432 / 100 = 54.32, rounded up)

Thread Pool (10 threads):
  Thread 1: Request offset=0   (items 1-100)
  Thread 2: Request offset=100 (items 101-200)
  Thread 3: Request offset=200 (items 201-300)
  ...
  Thread 10: Request offset=900 (items 901-1000)

Wait for threads 1-10 to complete, spawn next batch...
```

**Performance benefit:** 
- Sequential: 55 requests × 1 second = 55 seconds
- Parallel (10 threads): ≈ 6 seconds

**Code example:**
```python
from functools import partial
from caracara.common.pagination import all_pages_numbered_offset_parallel

func = partial(
    client.hosts.hosts_api.query_devices_by_filter,
    filter="platform_name:'Windows'"
)

device_ids = all_pages_numbered_offset_parallel(
    func=func,
    logger=logger
)
```

### Style 2: Token Offset (Sequential)

**Used by:** Some APIs that require sequential pagination

**How it works:**
1. First request returns a token for the next page
2. Use token in next request to get the next page
3. Continue until no more tokens are returned
4. Cannot be parallelized (each page depends on previous)

**API Response Structure:**
```json
{
    "meta": {
        "pagination": {
            "limit": 100,
            "offset": "eyJzZWFy...",  // Token for next page
            "total": 5432
        }
    },
    "resources": ["id1", "id2", ...]
}
```

**Implementation:** `all_pages_token_offset()`

**Example internal flow:**
```
Request 1: offset=None          → Returns token "abc123"
Request 2: offset="abc123"      → Returns token "def456"
Request 3: offset="def456"      → Returns token "ghi789"
...
Request N: offset="xyz000"      → Returns None (done)
```

**Performance characteristic:**
- Must execute sequentially
- Slower than Style 1 for large datasets
- Used when API doesn't support numerical offsets

**Code example:**
```python
from functools import partial
from caracara.common.pagination import all_pages_token_offset

func = partial(
    client.hosts.hosts_api.query_devices_by_filter_scroll,
    filter="platform_name:'Linux'"
)

device_ids = all_pages_token_offset(
    func=func,
    logger=logger
)
```

### Style 3: Token After

**Used by:** Some newer APIs

**How it works:**
- Same as Style 2, but uses `after` field instead of `offset`
- Still sequential pagination

**API Response Structure:**
```json
{
    "meta": {
        "pagination": {
            "limit": 100,
            "after": "eyJzZWFy...",  // Token for next page
            "total": 5432
        }
    },
    "resources": ["id1", "id2", ...]
}
```

**Implementation:** `all_pages_token_offset(offset_key_named_after=True)`

### Style 4: Marker-based (Timestamp)

**Used by:** Intel APIs and time-series data

**How it works:**
- Uses FQL `_marker` parameter for time-based pagination
- Each page returns a timestamp marker for the next page
- Designed for datasets divided by time rather than count

**Not yet implemented in Caracara** - will be added when needed.

### Style 5: Generic Parallelized One-by-One

**Used by:** APIs that accept one ID at a time (e.g., user details)

**How it works:**
1. Have a list of IDs to query
2. Divide into batches
3. Execute each batch in parallel
4. Aggregate results

## Batching System

After pagination retrieves IDs, the batching system retrieves detailed data for those IDs.

### How Batching Works

**Located in:** `caracara/common/batching.py`

**Main function:** `batch_get_data(lookup_ids, func, data_batch_size)`

**Process:**
1. **Divide IDs into batches**
   ```python
   # Example: 50,000 device IDs, batch size 5,000
   # Results in 10 batches of 5,000 IDs each
   batches = [
       lookup_ids[0:5000],      # Batch 0
       lookup_ids[5000:10000],  # Batch 1
       ...
       lookup_ids[45000:50000]  # Batch 9
   ]
   ```

2. **Create thread pool**
   ```python
   threads = min(cpu_count * 2, 20)
   # On 8-core system: min(16, 20) = 16 threads
   ```

3. **Execute requests in parallel**
   ```python
   with ThreadPoolExecutor(max_workers=threads) as executor:
       results = executor.map(worker_function, batches)
   ```

4. **Aggregate results**
   ```python
   all_resources = []
   for batch_resources, batch_errors in results:
       all_resources.extend(batch_resources)
   ```

### Thread Pool Sizing

**Formula:** `min(cpu_count * 2, 20)`

**Rationale:**
- **2× CPU count**: Good balance for I/O-bound operations
- **Max 20 threads**: Respects API rate limits and prevents excessive parallelism

**Examples:**
- 4-core system: 8 threads
- 8-core system: 16 threads
- 16-core system: 20 threads (capped)
- 32-core system: 20 threads (capped)

### Batch Sizes

**Default batch sizes** (defined in `caracara/common/constants.py`):

```python
DEFAULT_DATA_BATCH_SIZE = 5000  # For data retrieval
MAX_BATCH_SESSION_HOSTS = 10000  # For RTR sessions
```

**Why these sizes:**
- **5,000**: Balances API limits with memory efficiency
- **10,000**: Maximum enforced by Falcon API for RTR

### Performance Impact

**Example: Retrieving 50,000 device details**

**Without batching/parallelization:**
```
50,000 IDs ÷ 500 per request = 100 requests
100 requests × 1 second = 100 seconds
```

**With batching and parallelization:**
```
50,000 IDs ÷ 5,000 per batch = 10 batches
10 batches ÷ 16 threads ≈ 1 batch per thread (rounded up)
Execution time ≈ 2-3 seconds
```

**Speedup: ~40-50× faster**

## Combined Flow Example

Let's trace a complete operation: `client.hosts.describe_devices(filters)`

### Step 1: Paginate to Get IDs

```python
# User code
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
devices = client.hosts.describe_devices(filters)
```

**Internal execution:**
```python
# caracara/modules/hosts/hosts.py::describe_devices()

# 1. Get device IDs using pagination
device_ids = self.get_device_ids(filters)
    # Calls: all_pages_numbered_offset_parallel()
    # API requests:
    #   Request 1: Get total count (e.g., 50,000)
    #   Calculate pages: 50,000 / 500 = 100 pages
    #   Parallel requests: Pages 1-100 (using thread pool)
    # Returns: ['id1', 'id2', ..., 'id50000']

# 2. Get device data using batching
device_data = self.get_device_data(device_ids)
    # Calls: batch_get_data(device_ids, ...)
    # Batching:
    #   50,000 IDs → 10 batches of 5,000
    #   Thread pool executes 10 requests in parallel
    # Returns: {'id1': {...}, 'id2': {...}, ...}
```

### Step 2: Batch Data Retrieval

```python
# caracara/modules/hosts/hosts.py::get_device_data()
device_data = batch_get_data(
    device_ids,
    self.hosts_api.get_device_details
)

# caracara/common/batching.py::batch_get_data()
# 1. Split into batches
batches = [
    device_ids[0:5000],
    device_ids[5000:10000],
    ...
]

# 2. Create worker function
def worker(batch_func, worker_lookup_ids):
    response = batch_func(ids=worker_lookup_ids)
    return response['body']['resources'], response['body']['errors']

# 3. Execute in parallel
with ThreadPoolExecutor(max_workers=16) as executor:
    partial_worker = partial(worker, self.hosts_api.get_device_details)
    completed = executor.map(partial_worker, batches)

# 4. Aggregate
for resources, errors in completed:
    all_resources.extend(resources)
```

## Tuning Performance

### Custom Batch Sizes

You can override default batch sizes:

```python
from caracara.common.batching import batch_get_data

# Use smaller batches (better for memory-constrained environments)
device_data = batch_get_data(
    device_ids,
    client.hosts.hosts_api.get_device_details,
    data_batch_size=1000  # Instead of default 5000
)
```

### Monitoring Performance

Enable logging to see pagination and batching in action:

```python
import logging

logging.basicConfig(level=logging.INFO)
# Or for very verbose output:
# logging.basicConfig(level=logging.DEBUG)

client = Client(...)
devices = client.hosts.describe_devices(filters)
```

**Log output:**
```
caracara.modules.HostsApiModule: Searching for device IDs...
caracara.common.pagination: Retrieved 50000 IDs across 100 pages
caracara.modules.HostsApiModule: Obtaining data for 50000 devices
caracara.common.batching: Batch data retrieval for get_device_details (50000 items)
caracara.common.batching: Divided the item IDs into 10 batches
caracara.common.batching: ThreadPoolExecutor-0_0 | Batch worker started with a list of 5000 items
caracara.common.batching: ThreadPoolExecutor-0_1 | Batch worker started with a list of 5000 items
...
caracara.common.batching: Retrieved 50000 resources
```

## Memory Considerations

### Memory Usage Patterns

**During pagination:**
- Minimal memory - only storing IDs (strings)
- Example: 50,000 IDs × ~40 bytes = ~2 MB

**During batching:**
- Peak memory = batch_size × average_item_size
- Example: 5,000 devices × ~10 KB each = ~50 MB per batch
- Multiple batches in flight: 50 MB × threads

**For very large datasets (>100k devices):**

Consider using streaming or processing in chunks:

```python
# Process devices in chunks to reduce memory usage
def process_devices_in_chunks(client, filters, chunk_size=10000):
    # Get all IDs first (minimal memory)
    all_device_ids = client.hosts.get_device_ids(filters)
    
    # Process in chunks
    for i in range(0, len(all_device_ids), chunk_size):
        chunk_ids = all_device_ids[i:i+chunk_size]
        chunk_data = client.hosts.get_device_data(chunk_ids)
        
        # Process this chunk
        for device_id, device in chunk_data.items():
            # Do something with device
            process_device(device)
        
        # chunk_data goes out of scope, memory is freed
```

## Rate Limiting

### Falcon API Rate Limits

CrowdStrike Falcon APIs have rate limits. Caracara's design helps you stay within limits:

1. **Thread pool caps** prevent excessive parallelism (max 20 threads)
2. **Batch sizes** are chosen to balance speed with limits
3. **Sequential pagination** where required by API design

### Best Practices

- **Don't create multiple clients unnecessarily** - reuse a single client instance
- **Use filters effectively** - reduce the dataset size at the API level
- **Consider timing** - space out large operations if running frequently
- **Monitor for 429 errors** - these indicate you've hit rate limits

## Debugging Pagination Issues

### Enable Debug Logging

```python
import logging

# Very verbose - shows all API responses
logging.basicConfig(level=logging.DEBUG)

client = Client(...)
devices = client.hosts.describe_devices(filters)
```

### Common Issues

**Issue: "Getting fewer results than expected"**
- Check your filter syntax
- Verify the FQL is correct: `print(filters.get_fql())`
- Test filter in Falcon UI first

**Issue: "Operation is slow"**
- Check network latency to Falcon API
- Verify CPU count: `import multiprocessing; multiprocessing.cpu_count()`
- Consider if batch size needs adjustment

**Issue: "Running out of memory"**
- Process in chunks (see Memory Considerations above)
- Reduce batch size
- Use `get_device_ids()` instead of `describe_devices()` if you only need IDs

## Implementation Details

### File Locations

- **Pagination implementations**: [`caracara/common/pagination.py`](../../caracara/common/pagination.py)
- **Batching implementation**: [`caracara/common/batching.py`](../../caracara/common/batching.py)
- **Constants**: [`caracara/common/constants.py`](../../caracara/common/constants.py)

### Key Functions

```python
# Pagination
from caracara.common.pagination import (
    all_pages_numbered_offset_parallel,  # Style 1
    all_pages_token_offset,              # Styles 2 & 3
)

# Batching
from caracara.common.batching import (
    batch_get_data,
    batch_data_pull_threads,
)

# Constants
from caracara.common.constants import (
    DEFAULT_DATA_BATCH_SIZE,
    MAX_BATCH_SESSION_HOSTS,
)
```

## Next Steps

- [Concurrency and Performance](concurrency.md) - Optimize your Caracara usage
- [Architecture Overview](../architecture.md) - Understand the overall design
- [Hosts Module](../modules/hosts.md) - See pagination in action
