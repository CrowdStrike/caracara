"""Kits class defines the available Toolboxes."""
from enum import Enum


class Kits(Enum):
    """Enumerator for toolbox class name lookups."""

    HOSTS = "HostsToolbox"
    RTR = "RTRToolbox"
