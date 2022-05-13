"""
Generic Caracara API module.

This module contains the the FalconApiModule class, which represents a generic
Caracara API module. All modules, including Hosts, Prevention Policies, etc.
derive from this abstract base class.
"""
import logging

from abc import ABC, abstractmethod

from falconpy import OAuth2


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

    def __init__(self, api_authentication: OAuth2):
        """Configure a Caracara API module with a FalconPy OAuth2 module."""
        class_name = self.__class__.__name__
        self.logger = logging.getLogger(class_name)
        self.logger.debug("Initialising API module: %s", class_name)

        self.api_authentication = api_authentication
