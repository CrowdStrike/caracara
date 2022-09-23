"""Falcon Flight Control (MSSP) APIs.

This module handles interaction with Parent CIDs, which have beneath them children (members) that
can be interfaced with directly.

This module handles interactions with the Parent CID's management APIs. To authenticate to
a child/member CID, use the member_cid kwarg when initialising a Caracara Client object.
"""
from typing import (
    Dict,
    List,
    Union,
)

from falconpy import (
    FlightControl,
    OAuth2,
)

from caracara.common.batching import batch_get_data
from caracara.common.module import FalconApiModule
from caracara.common.pagination import all_pages_numbered_offset_parallel


class FlightControlApiModule(FalconApiModule):
    """The FlightControlApiModule facilitates interactions with the Flight Control (MSSP) API."""

    name = "CrowdStrike Falcon Flight Control API Module"
    help = "Interact with the management API calls in a Falcon Flight Control (MSSP) Parent CID"

    def __init__(self, api_authentication: OAuth2):
        """Construct an instance of the FlightControlApiModule class."""
        super().__init__(api_authentication)

        self.logger.debug("Configuring the FalconPy Flight Control API")
        self.flight_control_api = FlightControl(auth_object=self.api_authentication)

    def get_child_cids(self) -> List[str]:
        """Retreives a list of every Child/Member CID within a Parent instance.

        This function will return a list of CID strings without additional data. To get the names
        of the CIDs, either pass the results of this function into get_child_cid_data(), or use the
        describe_child_cids() function to obtain all this data in one function call.

        Returns
        -------
        list: A list of all Child CIDs owned by the Parent CID associated with this Caracara Client
              instance
        """
        self.logger.info("Obtaining a list of all Child CIDs")
        child_cids: List[str] = all_pages_numbered_offset_parallel(
            self.flight_control_api.query_children,
            self.logger,
            10,
        )
        return child_cids

    def get_child_cid_data(self, cids: List[str]) -> Dict[str, Dict[str, Union[List[str], str]]]:
        """Return a dictionary containing details for every Child CID specified by ID.

        You should use this endpoint if you have a list of Child CIDs associated with the Parent
        CID you are authenticated to within this Caracara Client instance. If you do not yet have
        a list of Child CIDs, either use the get_child_cids() function to obtain these first,
        or alternatively use the describe_child_cids() function to obtain all this data in one
        function call.

        Arguments
        ---------
        cids: [str], required
            A list of Falcon Customer IDs (CIDs) associated with this Parent Falcon tenant

        Returns
        -------
        dict: A dictionary containing details for every Child CID listed.
        """
        self.logger.info("Obtaining data for %d child CIDs", len(cids))
        child_cid_data: Dict[str, Dict[str, Union[List[str], str]]] = batch_get_data(
            cids,
            self.flight_control_api.get_children,
        )
        return child_cid_data

    def describe_child_cids(self) -> Dict[str, Dict[str, Union[List[str], str]]]:
        """Return a dictionary containing details for each Child CID associated with this tenant.

        Returns
        -------
        dict: A dictionary containing details for every Child CID associated with this
              Parent Falcon tenant (CID)
        """
        self.logger.info("Describing this Parent CID's Child CIDs")
        child_cids = self.get_child_cids()
        child_cid_data = self.get_child_cid_data(cids=child_cids)
        return child_cid_data
