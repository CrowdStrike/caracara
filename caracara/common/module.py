"""
Module containing the definition of a generic Caracara FQL filter module
"""
import logging

from abc import ABC, abstractmethod

from falconpy import OAuth2


class FalconApiModule(ABC):
    """
    Meta class for API Module.
    Each module provides API Methods.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Name for the developer to use when instantiating the filter"""

    @property
    @abstractmethod
    def help(self) -> str:
        """A bespoke help string to be made available for each filter"""

    def __init__(self, api_authentication: OAuth2):
        class_name = self.__class__.__name__
        self.logger = logging.getLogger(class_name)
        self.logger.debug("Initialising API module: %s", class_name)

        self.api_authentication = api_authentication
