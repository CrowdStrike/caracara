"""Tool class"""
from ._toolbox import Toolbox


class Tool(Toolbox):
    """Individual tool base class, inherits from the toolbox"""
    def __init__(self, api: object = None, verbose: bool = True):
        super().__init__(api=api, verbose=verbose)
        self.api = api
        self.verbose = verbose
