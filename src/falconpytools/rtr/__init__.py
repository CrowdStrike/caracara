"""RTR Toolbox"""
from ._api import FalconAPI
from ._single_target import SingleTarget
from .._toolbox import Toolbox
# from toolbox import inform


class RTRToolbox(Toolbox):
    """RTR Toolbox"""
    def __init__(self: object, key: str = None, secret: str = None, auth_object: object = None, verbose: bool = True):
        """Opens the toolbox"""
        super().__init__(api=FalconAPI(key=key, secret=secret, auth_object=auth_object), verbose=verbose)


__all__ = ["RTRToolbox", "SingleTarget"]
