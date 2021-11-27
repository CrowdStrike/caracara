"""CrowdStrike Caracara.

 _______
|   _   .---.-.----.---.-.----.---.-.----.---.-.
|.  1___|  _  |   _|  _  |  __|  _  |   _|  _  |
|.  |___|___._|__| |___._|____|___._|__| |___._|
|:  1   |
|::.. . |  Powered by FalconPy
`-------'     The CrowdStrike Falcon SDK for Python
"""
from enum import Enum
from importlib import import_module
from ._version import _VERSION, _MAINTAINER, _AUTHOR, _AUTHOR_EMAIL
from ._version import _CREDITS, _DESCRIPTION, _TITLE, _PROJECT_URL, _KEYWORDS

__version__ = _VERSION
__maintainer__ = _MAINTAINER
__author__ = _AUTHOR
__author_email__ = _AUTHOR_EMAIL
__credits__ = _CREDITS
__description__ = _DESCRIPTION
__title__ = _TITLE
__project_url__ = _PROJECT_URL
__keywords__ = _KEYWORDS

__available_kits__ = ["hosts", "rtr"]

__all__ = ["toolbox"]


class KitType(Enum):
    """Enumerator for toolbox class name lookups."""
    HOSTS = "HostsToolbox"
    RTR = "RTRToolbox"


def toolbox(kit: str = None, **kwargs):
    """Return an instance of the specified client."""
    if not kit:
        # Implement a generic-only kit here
        raise SystemError("No toolbox specified.")

    if not kit.lower() in __available_kits__:
        raise SystemError("Invalid toolbox specified.")

    try:
        opened = getattr(import_module(f".{kit}", package=__title__), KitType[kit.upper()].value)
    except (ImportError, TypeError, KeyError) as import_failure:
        raise SystemError("Unable to load specified toolbox.") from import_failure

    return opened(**kwargs)
