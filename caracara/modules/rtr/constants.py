"""Real Time Response (RTR) Constants."""
RTR_COMMANDS = {
    "cat": "read_only",
    "cd": "read_only",
    "clear": "read_only",
    "cp": "active_responder",
    "csrutil": "read_only",
    "encrypt": "active_responder",
    "env": "read_only",
    "eventlog": "read_only",
    "filehash": "read_only",
    "get": "active_responder",
    "getsid": "read_only",
    "history": "read_only",
    "ifconfig": "read_only",
    "ipconfig": "read_only",
    "kill": "active_responder",
    "ls": "read_only",
    "map": "active_responder",
    "memdump": "active_responder",
    "mkdir": "active_responder",
    "mount": "read_only",
    "mv": "active_responder",
    "netstat": "read_only",
    "ps": "read_only",
    "put": "admin",
    "put-and-run": "admin",
    "reg": {
        "_default": "active_responder",
        "query": "read_only",
    },
    "restart": "active_responder",
    "rm": "active_responder",
    "run": "admin",
    "runscript": {
        "_default": "admin",
        "-Raw": "admin",
        "-CloudFile": "active_responder",
        "-HostPath": "admin",
    },
    "shutdown": "active_responder",
    "umount": "active_responder",
    "unmap": "active_responder",
    "update": "active_responder",
    "users": "read_only",
    "xmemdump": "active_responder",
    "zip": "active_responder",
}

# Maximum number of devices within an RTR batch session
# There is a 10,000 limit enforced in EU-1 and US-2, so we use this as our limit
MAX_BATCH_SESSION_HOSTS = 10000

# Most number of threads permitted when running RTR batch commands
MAX_BATCH_SESSION_THREADS = 3

# RTR sessions last for 10 minutes
SESSION_EXPIRY = 60 * 10

# Refresh RTR sessions if there are < 3 minutes left
SESSION_REFRESH_TIMEOUT = 60 * 3
