# Sensor Download Module

The Sensor Download module (`client.sensor_download`) provides functionality to search available
sensor installer versions, retrieve installer metadata, download installers to disk, and fetch the
Checksummed Customer ID (CCID) required for sensor deployment.

## Overview

The Sensor Download module exposes:
- Tenant CCID retrieval (for use in deployment scripts)
- Sensor installer search and filtering
- Installer metadata retrieval
- Installer file download

## Quick Start

```python
from caracara import Client

client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret",
)

# Find all Linux sensor installers for RHEL
filters = client.FalconFilter(dialect="sensor_download")
filters.create_new_filter("platform", "Linux")
filters.create_new_filter("os", "RHEL")

installers = client.sensor_download.describe_installers(filters, sort="version|desc")
for installer in installers:
    print(f"{installer['name']} ({installer['version']}) — {installer['sha256']}")
```

## Installer Operations

### Searching for Installers

#### `describe_installers(filters=None, sort=None)`

Return full metadata for all sensor installers matching the provided filters.

This method uses the V3 combined endpoint, which includes the complete set of installer
properties: name, version, platform, os, os_version, sha256, release_date, file_size,
file_type, description, architectures (V2+), is_lts and lts_expiry_date (V3+).

**Parameters:**
- `filters` (FalconFilter | str, optional): FQL filter to apply. Use `dialect="sensor_download"`
  when constructing a `FalconFilter` to get sensor-installer-specific filter suggestions.
- `sort` (str, optional): Sort field and direction, e.g. `'version|desc'` or `'release_date|asc'`.

**Returns:** `List[Dict]` — Installer metadata dictionaries ordered by the chosen sort.

**Example:**

```python
# All Windows sensor installers, newest first
filters = client.FalconFilter(dialect="sensor_download")
filters.create_new_filter("platform", "Windows")

installers = client.sensor_download.describe_installers(filters, sort="release_date|desc")
for installer in installers:
    print(f"{installer['version']} released {installer['release_date']}")
```

#### `get_installer_ids(filters=None, sort=None)`

Return the SHA256 hashes of all sensor installers matching the provided filters.
Useful when you only need the identifiers, for example to pass to `download_installer()`.

**Parameters:**
- `filters` (FalconFilter | str, optional): FQL filter to apply.
- `sort` (str, optional): Sort field and direction.

**Returns:** `List[str]` — SHA256 hashes of matching installers.

**Example:**

```python
# Get the SHA256 of every LTS sensor build
filters = client.FalconFilter(dialect="sensor_download")
filters.create_new_filter("is_lts", True)

sha256_list = client.sensor_download.get_installer_ids(filters)
print(f"Found {len(sha256_list)} LTS build(s)")
```

### Downloading Installers

#### `download_installer(sha256, destination_path, filename=None, include_version=False, if_exists="error", show_progress=True)`

Download a sensor installer to disk by its SHA256 hash, verifying integrity via SHA256.

The file is downloaded in 1 MiB chunks (streaming) to avoid loading the full installer into
memory. The SHA256 of the downloaded bytes is verified against the expected hash; a mismatch
raises `ValueError` and removes the partial file.

The destination directory is created automatically if it does not exist. When no `filename`
is provided, the canonical installer name from the Falcon cloud is used (e.g.
`falcon-sensor-7.15.0-17206.x86_64.rpm` or `WindowsSensor.exe`).

**Parameters:**
- `sha256` (str): SHA256 hash of the installer to download. Also used as the API lookup key.
- `destination_path` (str): Directory where the installer file will be saved.
- `filename` (str, optional): Override the saved filename. When provided, `include_version` is ignored.
- `include_version` (bool, optional): Embed the sensor version before the extension (e.g. `FalconSensor_Windows-7.32.20406.exe`). Useful when downloading multiple versions to the same directory. Default `False`.
- `if_exists` (`"error"` | `"skip"` | `"overwrite"`, optional): Behaviour when the destination file already exists. `"error"` raises `FileExistsError` (default), `"skip"` returns the existing path, `"overwrite"` replaces the file.
- `show_progress` (bool, optional): Display a tqdm progress bar while downloading. Default `True`.

**Returns:** `str` — Full path to the downloaded file.

**Raises:** `FileExistsError` if the file exists and `if_exists="error"`. `GenericAPIError` on API error. `ValueError` on SHA256 mismatch.

**Example:**

```python
# Download the latest Linux sensor for RHEL 8
filters = client.FalconFilter(dialect="sensor_download")
filters.create_new_filter("platform", "Linux")
filters.create_new_filter("os", "RHEL")
filters.create_new_filter("os_version", "8")

installers = client.sensor_download.describe_installers(filters, sort="release_date|desc")
if installers:
    latest = installers[0]
    path = client.sensor_download.download_installer(
        sha256=latest["sha256"],
        destination_path="/tmp/falcon-sensors",
    )
    print(f"Downloaded to: {path}")
```

### Retrieving the CCID

#### `get_cid(include_checksum=False)`

Return the Customer ID (CID) for the authenticated tenant.

When `include_checksum=True`, the full Checksummed CID (CCID) is returned — this is the
value required when installing the Falcon sensor. When `include_checksum=False` (the default),
the plain CID is returned in lower case.

**Parameters:**
- `include_checksum` (bool): Return the CCID with its two-character checksum appended.

**Returns:** `str` — CID or CCID string.

**Example:**

```python
ccid = client.sensor_download.get_cid(include_checksum=True)
print(f"Install with: CS_FALCON_CUSTOMER_ID={ccid}")
```

## Filtering with FalconFilter

The `sensor_download` dialect provides the following filter names:

| Filter Name | FQL Field | Description |
|---|---|---|
| `platform` | `platform` | Installer platform: `Android`, `Linux`, `Mac`, `VMware`, or `Windows` |
| `os` | `os` | OS name, e.g. `RHEL`, `Ubuntu`, `Windows` |
| `os_version` | `os_version` | OS version string, e.g. `8`, `20.04` |
| `version` | `version` | Sensor version; supports `GT`, `GTE`, `LT`, `LTE` operators |
| `release_date` | `release_date` | Release date; accepts ISO 8601 or relative timestamps (e.g. `-30d`) |
| `architectures` | `architectures` | Supported architecture, e.g. `x86_64`, `arm64` (V2+ only) |
| `is_lts` / `lts` | `is_lts` | Whether the build is LTS; accepts `True`/`False` or `yes`/`no` (V3 only) |

> **Note:** `description`, `file_type`, `name`, and `sha256` appear as fields in the installer
> metadata returned by `describe_installers()` but are **not** valid FQL filter properties — the
> API rejects them with a 400 error. Filter by `platform`, `os`, `version`, or `release_date`
> instead, then inspect the full metadata dict to match on those fields in Python if needed.

All filter names support both camelCase (`releaseDate`) and snake_case (`release_date`) variants.

**Examples:**

```python
# Installers released in the last 90 days
filters = client.FalconFilter(dialect="sensor_download")
filters.create_new_filter("release_date", "-90d", "GTE")

# All sensor builds at or above version 7.10
filters = client.FalconFilter(dialect="sensor_download")
filters.create_new_filter("version", "7.10.0", "GTE")

# Only LTS builds for Windows
filters = client.FalconFilter(dialect="sensor_download")
filters.create_new_filter("platform", "Windows")
filters.create_new_filter("lts", True)
```

> **Note on version comparison:** FQL uses lexicographic string comparison for the `version`
> field. This means `7.9` sorts after `7.10`. When comparing version numbers with differing
> digit counts, sort by `release_date` instead of `version` to get the intended ordering.

## Common Patterns

### Download the latest sensor for a platform

```python
def download_latest(client, platform: str, destination: str) -> str:
    filters = client.FalconFilter(dialect="sensor_download")
    filters.create_new_filter("platform", platform)

    installers = client.sensor_download.describe_installers(
        filters, sort="release_date|desc"
    )
    if not installers:
        raise RuntimeError(f"No installers found for platform: {platform}")

    latest = installers[0]
    return client.sensor_download.download_installer(
        sha256=latest["sha256"],
        destination_path=destination,
    )
```

### Build a deployment script with the CCID

```python
ccid = client.sensor_download.get_cid(include_checksum=True)
path = download_latest(client, "Linux", "/tmp/sensors")

print(f"# Run on target host:")
print(f"sudo rpm -ivh {path}")
print(f"sudo /opt/CrowdStrike/falconctl -s --cid={ccid}")
```

### Audit available LTS builds

```python
filters = client.FalconFilter(dialect="sensor_download")
filters.create_new_filter("lts", True)

lts_builds = client.sensor_download.describe_installers(filters, sort="release_date|desc")
for build in lts_builds:
    expiry = build.get("lts_expiry_date", "N/A")
    print(f"  {build['platform']:8s}  {build['version']:10s}  expires {expiry}")
```

## Data Structure Reference

`describe_installers()` returns a list of dictionaries. The fields present depend on the
API version used internally (always V3 in this module):

```python
{
    # V1 fields — always present
    "description": "Falcon sensor for Linux",
    "file_size": 45000000,
    "file_type": "rpm",
    "name": "falcon-sensor-7.15.0-17206.x86_64.rpm",
    "os": "RHEL",
    "os_version": "8",
    "platform": "Linux",
    "release_date": "2024-01-15T00:00:00Z",
    "sha256": "aabbcc...",
    "version": "7.15.0",

    # V2 fields
    "architectures": ["x86_64"],
    "ltv_expiry_date": None,
    "ltv_promoted_date": None,

    # V3 fields
    "is_lts": False,
    "lts_expiry_date": None,
}
```

## Next Steps

- [Hosts Module](hosts.md) — Enumerate enrolled devices and look up sensor version per host
- [Sensor Update Policies](README.md#sensor-update-policies) — Manage automated sensor update policies
