# Real Time Response (RTR) Module

The RTR module (`client.rtr`) provides a high-level interface to CrowdStrike's Real Time Response functionality, enabling remote command execution, file operations, and script management across your fleet.

## Overview

The RTR module abstracts away the complexity of RTR session management, allowing you to:
- Execute commands on multiple hosts simultaneously (supports unlimited hosts)
- Upload and download files from endpoints
- Manage RTR scripts and put-files
- Handle queued sessions for offline devices
- Automatically manage session lifecycles and refreshes

## Key Concepts

### Batch Sessions

RTR operations require establishing a "batch session" with target devices. Caracara abstracts the 10,000 host limit enforced by Falcon:

```
Your Code
    ↓
RTRBatchSession (handles unlimited hosts)
    ↓
InnerRTRBatchSession #1 (up to 10,000 hosts)
InnerRTRBatchSession #2 (up to 10,000 hosts)
InnerRTRBatchSession #N (up to 10,000 hosts)
    ↓
CrowdStrike Falcon Cloud
```

**Benefits:**
- No 10,000 host limit - Caracara handles batching automatically
- Automatic session refresh to prevent timeouts
- Parallel command execution across all batches
- Simplified error handling

### Command Types

RTR supports three command categories based on Falcon RBAC roles:

1. **Read-only commands** (`run_generic_command`): Non-destructive operations
   - Examples: `ps`, `ls`, `cat`, `netstat`
   - Required role: RTR Read

2. **Active Responder commands** (`run_active_responder_command`): Moderate-impact operations
   - Examples: `get`, `cp`, `kill`, `restart`
   - Required role: RTR Active Responder

3. **Admin commands** (`run_admin_command`): High-impact operations
   - Examples: `put`, `run`, custom scripts
   - Required role: RTR Admin

## Quick Start

### Basic Command Execution

```python
from caracara import Client

client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret",
)

# Get device IDs
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
device_ids = client.hosts.get_device_ids(filters)

# Create a batch session
session = client.rtr.batch_session()
session.connect(device_ids=device_ids)

# Run a command
result = session.run_generic_command("ps")

# Process results
for device_id, command_result in result.items():
    print(f"Device {device_id}:")
    print(command_result['stdout'])
```

## RTR Batch Session

### Creating a Session

#### `client.rtr.batch_session()`

Creates a new `RTRBatchSession` object.

**Returns:** `RTRBatchSession` - A new batch session object (not yet connected)

```python
session = client.rtr.batch_session()
```

### Connecting to Devices

#### `session.connect(device_ids, queueing=False, timeout=30)`

Establish connections to one or more devices. This must be called before any commands can be executed.

**Parameters:**
- `device_ids` (List[str], required): List of device IDs to connect to
- `queueing` (bool, optional): Queue commands for offline devices (default: False)
- `timeout` (int, optional): Connection timeout in seconds (default: 30)

**Returns:** `bool` - True if at least one device connected successfully

**Example:**
```python
# Connect to devices
device_ids = client.hosts.get_device_ids(filters)
success = session.connect(device_ids=device_ids)

if success:
    device_count = sum(len(s.devices) for s in session.batch_sessions)
    print(f"Connected to {device_count} devices")
else:
    print("Failed to establish any connections")
```

**What happens internally:**
1. Device IDs are divided into batches of 10,000 (MAX_BATCH_SESSION_HOSTS)
2. Connections are established in parallel across batches
3. Only successfully connected devices are included in the session
4. Failed connections are logged but don't cause the method to fail

## Command Execution

### Generic (Read-Only) Commands

#### `session.run_generic_command(command_string, device_ids=None, timeout=30)`

Execute a read-only command. Requires RTR Read role.

**Parameters:**
- `command_string` (str, required): Command to execute (e.g., "ps", "ls -la /tmp")
- `device_ids` (List[str], optional): Specific devices to target (defaults to all in session)
- `timeout` (int, optional): Command timeout in seconds (default: 30)

**Returns:** `Dict[str, Dict]` - Device ID → command result dictionary

**Available Commands:**
- `cat` - Display file contents
- `cd` - Change directory
- `clear` - Clear command history
- `env` - Show environment variables
- `eventlog` - View/export Windows event logs
- `filehash` - Calculate file hash
- `getsid` - Get SID for username (Windows)
- `history` - View command history
- `ipconfig` / `ifconfig` - Show network configuration
- `ls` / `dir` - List directory contents
- `mount` - Show mounted filesystems
- `netstat` - Show network connections
- `ps` - List running processes
- `reg query` - Query Windows registry

**Example:**
```python
# List running processes on all connected devices
processes = session.run_generic_command("ps")

for device_id, result in processes.items():
    if result.get('complete'):
        print(f"\n{device_id}:")
        print(result['stdout'])
    else:
        print(f"{device_id}: Command failed - {result.get('stderr')}")

# Execute on specific devices only
web_server_ids = ["abc123...", "def456..."]
result = session.run_generic_command(
    "netstat -an",
    device_ids=web_server_ids
)
```

### Active Responder Commands

#### `session.run_active_responder_command(command_string, device_ids=None, timeout=30)`

Execute an Active Responder command. Requires RTR Active Responder role.

**Parameters:** Same as `run_generic_command`

**Available Commands:**
- `cat` - Display file contents
- `cd` - Change directory
- `cp` - Copy files
- `encrypt` - Encrypt files
- `get` - Download file (use dedicated `get()` method instead - see below)
- `kill` - Terminate process
- `ls` - List directory
- `map` - Map network drive
- `memdump` - Dump process memory
- `mkdir` - Create directory
- `mount` - Mount drive
- `mv` - Move files
- `ps` - List processes
- `reg query`, `reg set`, `reg delete` - Registry operations
- `restart` - Restart device
- `rm` - Remove files
- `runscript` - Execute a script
- `shutdown` - Shutdown device
- `unmap` - Unmap network drive
- `xmemdump` - Extended memory dump
- `zip` - Compress files

**Example:**
```python
# Kill a malicious process
result = session.run_active_responder_command("kill 1234")

# Create a directory for evidence collection
result = session.run_active_responder_command("mkdir C:\\incident_response")
```

### Admin Commands

#### `session.run_admin_command(command_string, device_ids=None, timeout=30)`

Execute an admin-level command. Requires RTR Admin role.

**Parameters:** Same as `run_generic_command`

**Admin Commands:**
- `put` - Upload file to device (must be pre-uploaded to Falcon as a put-file)
- `run` - Execute arbitrary command
- `runscript` - Execute custom script (must be pre-uploaded to Falcon)

**Example:**
```python
# Run a custom PowerShell command (requires RTR Admin role)
result = session.run_admin_command(
    "run powershell.exe Get-EventLog -LogName Security -Newest 10"
)

# Deploy a remediation script
result = session.run_admin_command("put remediation_tool.exe")
```

## File Operations

### Downloading Files from Endpoints

File download in Falcon RTR is a three-step asynchronous process:

1. **Execute GET command** - Tells endpoints to upload files to Falcon cloud
2. **Check status** - Wait for uploads to complete
3. **Download files** - Pull files from Falcon cloud to your system

This reflects how Falcon RTR works: files must first be uploaded from endpoints to the Falcon cloud (which takes time for large files or slow connections), then downloaded to your local system.

#### Step 1: Execute GET Command

#### `session.get(file_path, device_ids=None, timeout=30)`

Tell endpoints to upload a file to the Falcon cloud.

**Parameters:**
- `file_path` (str, required): Full path to file on remote devices
- `device_ids` (List[str], optional): Specific devices to target
- `timeout` (int, optional): Command timeout in seconds

**Returns:** `List[BatchGetCmdRequest]` - List of batch request objects for tracking

**What's a BatchGetCmdRequest?**
```python
from dataclasses import dataclass

@dataclass
class BatchGetCmdRequest:
    """Represents a batch GET command request."""
    batch_get_cmd_req_id: str  # Unique ID for tracking this batch request
    devices: Dict              # Devices that received the GET command
```

Each `BatchGetCmdRequest` represents one batch of up to 10,000 devices that received the GET command.

**Example:**
```python
# Tell all connected devices to upload a file
file_path = "C:\\Windows\\System32\\drivers\\etc\\hosts"
batch_get_cmd_reqs = session.get(file_path)

print(f"Executed GET on {len(batch_get_cmd_reqs)} batches")
for req in batch_get_cmd_reqs:
    print(f"  Batch {req.batch_get_cmd_req_id}: {len(req.devices)} devices")
```

#### Step 2: Check Upload Status

#### `session.get_status(batch_get_cmd_reqs, timeout=30)`

Check which files have finished uploading to the Falcon cloud.

**Parameters:**
- `batch_get_cmd_reqs` (List[BatchGetCmdRequest], required): Requests from `session.get()`
- `timeout` (int, optional): Status check timeout in seconds

**Returns:** `List[GetFile]` - List of files ready to download

**What's a GetFile?**
```python
from dataclasses import dataclass

@dataclass
class GetFile:
    """Represents a file that has been uploaded to Falcon and is ready to download."""
    device_id: str          # Device that uploaded the file
    filename: str           # Full path on the origin device
    session_id: str         # RTR session ID
    sha256: str             # SHA256 hash of the file
    size: int               # File size in bytes
    batch_session: RTRBatchSession  # Reference to the batch session
    
    def download(...):
        """Download and extract the file."""
```

**Example - Wait for uploads to complete:**
```python
import time

batch_get_cmd_reqs = session.get("C:\\Windows\\System32\\drivers\\etc\\hosts")

# Wait for uploads (usually done in a loop)
max_attempts = 10
attempt_delay = 30  # seconds
expected_count = len(device_ids)

get_files = []
for attempt in range(max_attempts):
    get_files = session.get_status(batch_get_cmd_reqs)
    
    print(f"Attempt {attempt + 1}: {len(get_files)}/{expected_count} files uploaded")
    
    if len(get_files) >= expected_count:
        break
    
    if attempt < max_attempts - 1:
        time.sleep(attempt_delay)

print(f"Ready to download {len(get_files)} files")
```

#### Step 3: Download Files

#### `GetFile.download(output_path, extract=True, preserve_7z=False, show_download_progress=False)`

Download and optionally extract a file from the Falcon cloud.

**Parameters:**
- `output_path` (str, required): Local folder or file path
- `extract` (bool, optional): Extract from .7z archive (default: True)
- `preserve_7z` (bool, optional): Keep .7z archive after extraction (default: False)
- `show_download_progress` (bool, optional): Show progress bar (default: False)

**Returns:** None (file is written to disk)

**Important:** Files are uploaded to Falcon as `.7z` archives encrypted with password `"infected"`. The `download()` method automatically handles decryption and extraction.

**Example:**
```python
output_folder = "/tmp/collected_files"

for get_file in get_files:
    print(f"Downloading from {get_file.device_id}: {get_file.filename}")
    get_file.download(
        output_path=output_folder,
        extract=True,              # Extract from .7z
        preserve_7z=False,         # Delete .7z after extraction
        show_download_progress=True  # Show progress bar
    )

print(f"Downloaded {len(get_files)} files to {output_folder}")
```

**File naming:**
When `output_path` is a directory, files are automatically named:
```
{original_filename}_{sha256}_{device_id}.{ext}
```

Example: `hosts_a1b2c3d4..._{device_id}.txt`

### Complete File Download Example

```python
from caracara import Client
from caracara.modules.rtr.batch_session import BatchGetCmdRequest
from caracara.modules.rtr.get_file import GetFile
import time
from typing import List

client = Client(client_id="...", client_secret="...")

# Get target devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
device_ids = client.hosts.get_device_ids(filters)

# Connect RTR session
session = client.rtr.batch_session()
session.connect(device_ids=device_ids)

# Step 1: Execute GET command
file_path = "C:\\Windows\\System32\\drivers\\etc\\hosts"
batch_get_cmd_reqs: List[BatchGetCmdRequest] = session.get(file_path)

# Step 2: Wait for uploads to complete
max_attempts = 10
attempt_delay = 30
get_files: List[GetFile] = []

for attempt in range(max_attempts):
    get_files = session.get_status(batch_get_cmd_reqs)
    print(f"Attempt {attempt + 1}: {len(get_files)} files uploaded")
    
    if len(get_files) >= len(device_ids):
        break
    
    if attempt < max_attempts - 1:
        print(f"Waiting {attempt_delay}s before next check...")
        time.sleep(attempt_delay)

# Step 3: Download all files
output_folder = "/tmp/hosts_files"
for get_file in get_files:
    get_file.download(
        output_path=output_folder,
        extract=True,
        preserve_7z=False,
        show_download_progress=True
    )

print(f"Downloaded {len(get_files)} files to {output_folder}")
```

**From the example code** (`examples/rtr/download_event_log.py`):
This pattern is used in production code to collect Windows Event Logs or other files from fleets of devices.

### Uploading Files to Endpoints (Put-Files)

Put-files must first be uploaded to Falcon, then can be deployed to devices.

#### `client.rtr.describe_put_files(filters=None)`

List available put-files in your Falcon tenant.

**Parameters:**
- `filters` (FalconFilter | str, optional): Filter put-files

**Returns:** `Dict` - Put-file information

**Example:**
```python
# List all put-files
put_files = client.rtr.describe_put_files()

for put_file in put_files.get('resources', []):
    print(f"{put_file['name']}: {put_file['description']}")
```

To deploy a put-file to devices:
```python
# Use the admin 'put' command
session.run_admin_command("put your_file_name.exe")
```

## Script Management

### Listing Scripts

#### `client.rtr.describe_scripts(filters=None)`

List RTR scripts available in your tenant.

**Parameters:**
- `filters` (FalconFilter | str, optional): Filter scripts

**Returns:** `Dict` - Script information

**Example:**
```python
scripts = client.rtr.describe_scripts()

for script in scripts.get('resources', []):
    print(f"{script['name']} - Platform: {script['platform']}")
```

### Executing Scripts

Use the `runscript` command via Active Responder or Admin:

```python
# Execute a pre-uploaded script
result = session.run_active_responder_command(
    "runscript -CloudFile='MyScript' -CommandLine='param1 param2'"
)
```

## Queued Sessions

Queued sessions allow commands to be sent to offline devices that will execute when the device comes online.

### Managing Queued Sessions

#### `client.rtr.describe_queued_sessions()`

Get all queued RTR sessions.

**Returns:** `Dict` - Queued session data

**Example:**
```python
queued = client.rtr.describe_queued_sessions()

for session_id, session_data in queued.items():
    print(f"Session {session_id}:")
    print(f"  Device: {session_data.get('device_id')}")
    print(f"  Commands: {len(session_data.get('queued_commands', []))}")
```

#### `client.rtr.delete_queued_session(session_id)`

Delete a specific queued session.

**Parameters:**
- `session_id` (str, required): Session ID to delete

#### `client.rtr.delete_queued_session_command(session_id, cloud_request_id)`

Delete a specific command from a queued session.

**Parameters:**
- `session_id` (str, required): Session ID
- `cloud_request_id` (str, required): Command ID to delete

#### `client.rtr.clear_queued_sessions()`

Clear ALL queued sessions (convenience method).

**Example:**
```python
# Clear all queued sessions
client.rtr.clear_queued_sessions()
print("All queued sessions cleared")
```

## Advanced Patterns

### Incident Response Collection

```python
# Connect to compromised device
compromised_id = "abc123..."
session = client.rtr.batch_session()
session.connect(device_ids=[compromised_id])

# Collect artifacts
artifacts = [
    "C:\\Windows\\System32\\drivers\\etc\\hosts",
    "C:\\Windows\\System32\\Tasks\\SuspiciousTask.xml",
]

output_dir = "/incident_response/case_123"
all_get_files = []

for artifact_path in artifacts:
    print(f"Collecting {artifact_path}...")
    batch_reqs = session.get(artifact_path)
    
    # Wait for upload
    import time
    time.sleep(30)
    
    # Get status
    get_files = session.get_status(batch_reqs)
    all_get_files.extend(get_files)

# Download all collected files
for get_file in all_get_files:
    get_file.download(output_path=output_dir, extract=True)

# Also get process list
processes = session.run_generic_command("ps")
network = session.run_generic_command("netstat -anob")

print(f"Collected {len(all_get_files)} files and command outputs")
```

### Health Check Across Fleet

```python
# Connect to all devices
all_devices = client.hosts.get_device_ids()
session = client.rtr.batch_session()
session.connect(device_ids=all_devices)

# Run health checks
services = session.run_generic_command("ps")

# Analyze results
critical_service = "CrowdStrike Falcon Sensor Service"
devices_missing_service = []

for device_id, result in services.items():
    if result.get('complete'):
        if critical_service not in result['stdout']:
            devices_missing_service.append(device_id)

if devices_missing_service:
    print(f"ALERT: {len(devices_missing_service)} devices missing critical service")
    for device_id in devices_missing_service:
        print(f"  {device_id}")
```

## Session Management

### Automatic Session Refresh

RTR sessions expire after a period of inactivity. Caracara automatically refreshes sessions before they expire when you execute commands through the `@_batch_session_required` decorator.

### Manual Session Refresh

#### `session.refresh_sessions(timeout=30)`

Manually refresh all batch sessions.

**Parameters:**
- `timeout` (int, optional): Refresh timeout in seconds

### Disconnecting

#### `session.disconnect()`

Disconnect and clean up all batch RTR sessions.

**Example:**
```python
session.disconnect()
```

### Context Manager Support

```python
# Automatic cleanup (not yet implemented in current version)
# Use manual disconnect for now
session = client.rtr.batch_session()
try:
    session.connect(device_ids=device_ids)
    result = session.run_generic_command("ps")
finally:
    session.disconnect()
```

## Performance Considerations

### Batching

- Caracara automatically divides large device lists into batches of 10,000
- Commands execute in parallel across all batches
- Thread pool size: `min(cpu_count * 2, MAX_BATCH_SESSION_THREADS)`

### Timeouts

- Default command timeout: 30 seconds
- Adjust based on expected command execution time
- Long-running commands should use higher timeouts

```python
# For slow commands, increase timeout
result = session.run_generic_command("dir C:\\ /s", timeout=120)
```

### Memory Considerations

- Large file downloads are streamed in chunks
- Multiple files can be downloaded simultaneously
- Monitor memory usage when downloading from thousands of devices

## Error Handling

```python
from caracara.common.exceptions import GenericAPIError

session = client.rtr.batch_session()

try:
    success = session.connect(device_ids=device_ids)
    if not success:
        print("Failed to connect to any devices")
        return
    
    result = session.run_generic_command("ps")
    
    for device_id, cmd_result in result.items():
        if not cmd_result.get('complete'):
            print(f"Command failed on {device_id}: {cmd_result.get('stderr')}")
            
except GenericAPIError as e:
    print(f"RTR API error: {e}")
except ValueError as e:
    print(f"Session error: {e}")
```

## Best Practices

1. **Always connect before executing commands**: The `connect()` method must be called before any command execution

2. **Handle offline devices**: Check command results for completion status

3. **Use appropriate command types**: 
   - Read-only for information gathering
   - Active Responder for file operations and process management
   - Admin for uploads and arbitrary execution

4. **Manage timeouts**: Adjust based on expected command execution time

5. **Process results carefully**: Always check the `complete` flag and handle errors

6. **Clean up sessions**: Call `disconnect()` when done, especially for long-running scripts

7. **Respect rate limits**: Don't create excessive parallel sessions

8. **File downloads require patience**: Large files or slow connections take time to upload to Falcon cloud

9. **Check upload status regularly**: Use appropriate delay between status checks (typically 30-60 seconds)

10. **Use batch operations**: Caracara handles batching automatically - you don't need to split device lists

## Next Steps

- [Hosts Module](hosts.md) - Identify devices for RTR operations
- [Prevention Policies](prevention-policies.md) - Configure RTR permissions
- [Advanced Topics](../advanced/concurrency.md) - Optimize RTR performance
