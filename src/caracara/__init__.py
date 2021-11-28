"""CrowdStrike Caracara.

 _______
|   _   .---.-.----.---.-.----.---.-.----.---.-.
|.  1___|  _  |   _|  _  |  __|  _  |   _|  _  |
|.  |___|___._|__| |___._|____|___._|__| |___._|
|:  1   |
|::.. . |  Powered by FalconPy
`-------'     The CrowdStrike Falcon SDK for Python
"""
from importlib import import_module
from ._kits import Kits
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

__all__ = ["toolbox"]


class Session():
    """Class to represent the current session."""
    def __init__(self):
        """Initialize the session."""
        self.connections = []
        self.total = lambda: len(self.connections)
        self.latest = lambda: len(self.connections) - 1

    def append(self, cid: object = None):
        """Append a new CID to the list of connections."""
        self.connections.append(cid)

        return self.total


__session__ = Session()


class CID():
    """Class to represent a single CID connection."""
    def __init__(self, **kwargs):
        self.creds = {
            "client_id": kwargs.get("key", None),
            "client_secret": kwargs.get("secret", None)
        }
        if kwargs.get("member_cid", None):
            self.creds["member_cid"] = kwargs.get("member_cid", None)
        self.base = kwargs.get("base", "us1")
        self.use_ssl = kwargs.get("use_ssl", True)
        self.proxy = kwargs.get("proxy", None)
        self.timeout = kwargs.get("timeout", None)
        self.auth = None


def toolbox(kit: str = None, **kwargs):
    """Return an instance of the specified client."""
    if not kit:
        # Implement a generic-only kit here
        raise SystemError("No toolbox specified.")

    if not kit.upper() in [defined.name for defined in Kits]:
        raise SystemError("Invalid toolbox specified.")

    try:
        opened = getattr(import_module(f".{kit}", package=__title__), Kits[kit.upper()].value)
    except (ImportError, TypeError, KeyError) as import_failure:
        raise SystemError("Unable to load specified toolbox.") from import_failure

    if __session__.total() <= 0:
        __session__.append(CID(**kwargs))

    new = opened(session=__session__.connections[__session__.latest()])
    __session__.connections[__session__.latest()].auth = new.api.auth

    return new
