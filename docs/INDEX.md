# Caracara Documentation Index

Welcome! This directory contains comprehensive developer documentation for the Caracara toolkit.

## 📚 Documentation Structure

```
docs/
├── README.md                          ← You are here
├── quick-start.md                     ← Start here if you're new!
├── architecture.md                    ← Understanding Caracara's design
├── filtering.md                       ← Master the FQL filter system
├── modules/
│   ├── README.md                      ← All modules overview
│   ├── hosts.md                       ← Device management (most used)
│   ├── sensor_download.md             ← Sensor installer downloads and CCID
│   └── rtr.md                         ← Remote command execution
└── advanced/
    └── pagination-batching.md         ← How Caracara handles large datasets
```

## 🚀 Getting Started

### Complete Beginner?
1. **[Quick Start Guide](quick-start.md)** - Get running in 5 minutes
2. **[Filtering Guide](filtering.md)** - Learn to search effectively  
3. **[Hosts Module](modules/hosts.md)** - Work with devices

### Already Know FalconPy?
1. **[Architecture Overview](architecture.md)** - See how Caracara wraps FalconPy
2. **[Modules Overview](modules/README.md)** - Jump to your needed module
3. **[Advanced Topics](advanced/pagination-batching.md)** - Optimize performance

## 📖 Core Documentation

### Essential Guides

| Document | Description | Audience |
|----------|-------------|----------|
| **[Quick Start](quick-start.md)** | Installation, authentication, first script | Beginners |
| **[Architecture](architecture.md)** | Design principles, component overview | All developers |
| **[Filtering](filtering.md)** | FQL filter construction, examples | All developers |

### API Modules

| Module | Document | Key Features |
|--------|----------|--------------|
| **Hosts** | [Documentation](modules/hosts.md) | Device search, groups, containment, tagging |
| **RTR** | [Documentation](modules/rtr.md) | Remote commands, file operations, scripts |
| **Sensor Download** | [Documentation](modules/sensor_download.md) | Installer search, download, CCID retrieval |
| **All Modules** | [Overview](modules/README.md) | Complete module reference |

### Advanced Topics

| Topic | Document | Description |
|-------|----------|-------------|
| **Pagination & Batching** | [Documentation](advanced/pagination-batching.md) | How Caracara handles large datasets efficiently |

## 🎯 Common Tasks

### I want to...

#### Find devices
→ [Hosts Module - Querying Devices](modules/hosts.md#querying-devices)

#### Search with filters
→ [Filtering Guide](filtering.md)

#### Run remote commands
→ [RTR Module](modules/rtr.md)

#### Manage host groups
→ [Hosts Module - Host Groups](modules/hosts.md#host-groups)

#### Understand performance
→ [Pagination and Batching](advanced/pagination-batching.md)

#### Contain compromised devices
→ [Hosts Module - Device Containment](modules/hosts.md#device-containment)

#### Download files from devices
→ [RTR Module - File Operations](modules/rtr.md#file-operations)

## 📋 Quick Reference

### Installation
```bash
# Poetry (recommended)
poetry add caracara

# Pip
pip install caracara
```

### Basic Usage
```python
from caracara import Client

# Authenticate
client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)

# Search for devices
filters = client.FalconFilter(dialect="hosts")
filters.create_new_filter("OS", "Windows")
devices = client.hosts.describe_devices(filters)

# Run remote commands
session = client.rtr.batch_session()
session.connect(device_ids=list(devices.keys()))
results = session.run_generic_command("ps")
```

### Common Filters
```python
# Stale sensors (not seen in 7 days)
filters.create_new_filter("LastSeen", "-7d", "LTE")

# Specific OS
filters.create_new_filter("OS", "Windows")  # or "Linux", "Mac"

# Servers only
filters.create_new_filter("ProductType", "Server")

# Multiple conditions (AND logic)
filters.create_new_filter("OS", "Windows")
filters.create_new_filter("ProductType", "Server")
filters.create_new_filter("LastSeen", "-30d", "LTE")
```

## 🏗️ Architecture Quick Look

```
┌─────────────────────────────────────────────────────────┐
│                    Caracara Client                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │        FalconPy OAuth2 (Authentication)          │   │
│  └──────────────────────────────────────────────────┘   │
│                           │                             │
│  ┌────────────────────────┴────────────────────┐       │
│  │                                              │       │
│  ▼                                              ▼       │
│  Hosts Module                                RTR Module │
│  - Device search                             - Commands │
│  - Group management                          - Files    │
│  - Containment                               - Scripts  │
│                                                          │
│  Prevention Policies    Response Policies    Users      │
│  Sensor Update          Flight Control       Custom IOA │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Common Utilities                       │   │
│  │  • Pagination (5 styles, auto-parallel)          │   │
│  │  • Batching (multi-threaded data retrieval)      │   │
│  │  • Filtering (FQL generation)                    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
              CrowdStrike Falcon API
```

[→ Full Architecture Documentation](architecture.md)

## 🎓 Learning Path

### Day 1: Foundation
1. ✅ Complete [Quick Start Guide](quick-start.md)
2. ✅ Read [Filtering Guide](filtering.md)  
3. ✅ Try examples from [Hosts Module](modules/hosts.md)

### Day 2: Core Features
1. ✅ Master [Host Groups](modules/hosts.md#host-groups)
2. ✅ Learn [RTR basics](modules/rtr.md)
3. ✅ Practice with real use cases

### Day 3: Advanced
1. ✅ Understand [Architecture](architecture.md)
2. ✅ Learn [Pagination & Batching](advanced/pagination-batching.md)
3. ✅ Optimize your scripts

## 📚 Additional Resources

### Official Resources
- **GitHub Repository**: [CrowdStrike/caracara](https://github.com/CrowdStrike/caracara)
- **PyPI Package**: [caracara](https://pypi.org/project/caracara/)
- **FalconPy Docs**: [falconpy.io](https://falconpy.io)

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/CrowdStrike/caracara/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CrowdStrike/caracara/discussions)
- **Examples**: [examples/](../examples/) directory in repository

### Contributing
- **Contributing Guide**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- **Security**: [SECURITY.md](../SECURITY.md)

## 🔧 Tools and Utilities

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
# Now all Caracara operations will log
```

### Environment Variables
```python
# Use ${VAR} syntax for automatic expansion
client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
)
```

### Context Managers
```python
# Automatic token cleanup
with Client(...) as client:
    devices = client.hosts.describe_devices(filters)
# Token automatically revoked here
```

## 💡 Pro Tips

1. **Always filter at the API level** - Don't retrieve all data and filter locally
2. **Reuse client instances** - Create once, use many times
3. **Use type hints** - Your IDE will provide excellent autocomplete
4. **Enable logging during development** - See exactly what's happening
5. **Test filters in Falcon UI first** - Verify FQL before using in code

## 📊 Feature Matrix

| Feature | Hosts | RTR | Policies | Flight Control | Users |
|---------|:-----:|:---:|:--------:|:--------------:|:-----:|
| Search/List | ✅ | ✅ | ✅ | ✅ | ✅ |
| Details | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create | ✅ | ❌ | ✅ | ❌ | ❌ |
| Update | ✅ | ❌ | ✅ | ❌ | ❌ |
| Delete | ✅ | ✅ | ✅ | ❌ | ❌ |
| Filtering | ✅ | ✅ | ✅ | ✅ | ✅ |
| Batching | ✅ | ✅ | ✅ | ✅ | ✅ |

✅ = Supported | ❌ = Not applicable/needed

## 🗺️ Documentation Roadmap

### Current Status
- ✅ Core documentation complete
- ✅ Most-used modules documented (Hosts, RTR)
- ✅ Architecture and design principles
- ✅ Advanced topics started

### Future Additions
- 📝 Additional module documentation (Prevention Policies, Response Policies, etc.)
- 📝 More advanced topics (concurrency, logging, debugging)
- 📝 Cookbook with real-world recipes
- 📝 API migration guides
- 📝 Video tutorials

## 📝 Documentation Conventions

Throughout this documentation:

- **Code blocks** show working examples
- **💡 Pro tips** highlight best practices
- **⚠️ Warnings** indicate important gotchas
- **Links** connect related topics
- **Examples** use realistic scenarios

## 🤝 Contributing to Documentation

Found an error? Want to add examples? Documentation improvements are welcome!

1. Fork the repository
2. Edit the Markdown files in `docs/`
3. Submit a Pull Request
4. See [CONTRIBUTING.md](../CONTRIBUTING.md) for details

## 📄 License

Caracara is released under the MIT License. See [LICENSE](../LICENSE) for details.

---

**Ready to get started?** → [Quick Start Guide](quick-start.md)

**Need help?** → [GitHub Discussions](https://github.com/CrowdStrike/caracara/discussions)

**Found a bug?** → [GitHub Issues](https://github.com/CrowdStrike/caracara/issues)
