"""Hosts toolbox."""
from ._api import FalconAPI
from ._host import Host
from .._toolbox import Toolbox


class HostsToolbox(Toolbox):
    """Hosts Toolbox."""

    def __init__(self: object, verbose: bool = True, **kwargs):
        """Open the toolbox."""
        super().__init__(api=FalconAPI(**kwargs), verbose=verbose)

        self.host = Host(api=self.api)


__all__ = ["HostsToolbox"]
