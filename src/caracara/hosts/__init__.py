"""Hosts toolbox"""
from ._api import FalconAPI
from ._host import Host
from .._toolbox import Toolbox


class HostsToolbox(Toolbox):
    """Hosts Toolbox"""
    def __init__(self: object, key: str = None, secret: str = None, auth_object: object = None, verbose: bool = True):
        """Opens the toolbox"""
        super().__init__(api=FalconAPI(key=key, secret=secret, auth_object=auth_object), verbose=verbose)

        self.host = Host(api=self.api)


__all__ = ["HostsToolbox"]
