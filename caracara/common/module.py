"""Generic Caracara API module.

This module contains the the FalconApiModule class, which represents a generic
Caracara API module. All modules, including Hosts, Prevention Policies, etc.
derive from this abstract base class.
"""

import logging
from abc import ABC, abstractmethod

from falconpy import OAuth2


# pylint: disable=R0903
class ModuleMapper:
    """Empty container class to allow modules to map into other modules.

    This is deliberately empty to start with as the modules are loaded into
    the class dynamically when the Client is set up. This allows modules to
    call into one another post-initialisation.
    """


class FalconApiModule(ABC):
    """
    Meta class for a generic Caracara API Module.

    Each module provides API Methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Store the name for the developer to use when instantiating the API module."""

    @property
    @abstractmethod
    def help(self) -> str:
        """Store the help string to be made available for each API module."""

    def __init__(self, api_authentication: OAuth2, mapper: ModuleMapper):
        """Configure a Caracara API module with a FalconPy OAuth2 module."""
        class_name = self.__class__.__name__
        self.logger = logging.getLogger(f"caracara.modules.{class_name}")
        self.logger.debug("Initialising API module: %s", class_name)

        self.api_authentication = api_authentication
        self.mapper = mapper
