# Caracara Developer Documentation

Welcome to the Caracara Developer Documentation! This guide provides comprehensive information for developers working with or contributing to the Caracara toolkit.

## What is Caracara?

Caracara is a friendly Python wrapper for the CrowdStrike Falcon API, built on top of [FalconPy](https://github.com/CrowdStrike/falconpy/). It provides a developer-friendly interface with automatic pagination, concurrency, rich filtering, and comprehensive type hints for IDE autocomplete support.

## Documentation Structure

### Getting Started
- **[Quick Start Guide](quick-start.md)** - Get up and running with Caracara in minutes
- **[Installation](installation.md)** - Detailed installation instructions and requirements

### Core Concepts
- **[Architecture Overview](architecture.md)** - Understand how Caracara is structured
- **[Client Configuration](client-configuration.md)** - Learn how to configure the Caracara client
- **[Filtering with FQL](filtering.md)** - Master the Falcon Query Language filter system
- **[Error Handling](error-handling.md)** - Handle exceptions and errors effectively

### API Modules
- **[Hosts Module](modules/hosts.md)** - Manage devices and host groups
- **[RTR Module](modules/rtr.md)** - Real Time Response for remote execution
- **[Prevention Policies Module](modules/prevention-policies.md)** - Manage prevention policies
- **[Response Policies Module](modules/response-policies.md)** - Manage response policies
- **[Sensor Update Policies Module](modules/sensor-update-policies.md)** - Control sensor updates
- **[Flight Control Module](modules/flight-control.md)** - Multi-tenant (MSSP) operations
- **[Users Module](modules/users.md)** - User and role management
- **[Custom IOA Module](modules/custom-ioa.md)** - Custom Indicators of Attack

### Advanced Topics
- **[Pagination and Batching](advanced/pagination-batching.md)** - How Caracara handles large datasets
- **[Concurrency and Performance](advanced/concurrency.md)** - Multithreading and optimization
- **[Logging and Debugging](advanced/logging.md)** - Troubleshooting and monitoring
- **[FalconPy Integration](advanced/falconpy-integration.md)** - Using Caracara with FalconPy

### Contributing
- **[Development Setup](contributing/setup.md)** - Set up your development environment
- **[Code Style Guide](contributing/style-guide.md)** - Coding standards and conventions
- **[Testing Guide](contributing/testing.md)** - Writing and running tests
- **[Module Development](contributing/module-development.md)** - Creating new API modules

## Key Features

### 🚀 Automatic Pagination with Concurrency
Caracara automatically handles pagination and parallelizes data retrieval where possible, dramatically reducing data fetch times for large datasets.

```python
# This single call will handle all pagination automatically
devices = client.hosts.describe_devices(filters)
```

### 🎯 IDE-Friendly with Type Hints
Full type hint support means your IDE can provide accurate autocomplete suggestions and catch type errors before runtime.

### 🔍 Simple Filter Syntax
Object-oriented Falcon Query Language (FQL) generation makes filtering intuitive:

```python
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("LastSeen", "-7d", "LTE")
```

### 🔌 100% FalconPy Compatible
Built on FalconPy and fully interoperable - use both libraries together seamlessly.

### 📝 Rich Logging Support
Built-in Python logging integration for debugging and monitoring.

### 🎭 RTR Batch Abstraction
High-level interface to Real Time Response that handles session management, batching (10k+ hosts), and file extraction automatically.

## Quick Example

```python
from caracara import Client

# Authenticate once
client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret",
)

# Create a filter
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("LastSeen", "-7d", "LTE")

# Get all matching devices (automatically paginated)
stale_devices = client.hosts.describe_devices(filters)

# Work with the results
for device_id, device_data in stale_devices.items():
    print(f"{device_data['hostname']} hasn't checked in recently")
```

## Version Information

- **Current Version**: 1.0.3
- **Minimum Python Version**: 3.10+
- **FalconPy Version**: 1.5.0+

## Support and Resources

- **GitHub Repository**: [CrowdStrike/caracara](https://github.com/CrowdStrike/caracara)
- **Issue Tracker**: [GitHub Issues](https://github.com/CrowdStrike/caracara/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CrowdStrike/caracara/discussions)
- **FalconPy Documentation**: [falconpy.io](https://falconpy.io)

## License

Caracara is released under the MIT License. See [LICENSE](../LICENSE) for details.
