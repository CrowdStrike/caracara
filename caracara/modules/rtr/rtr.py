"""Caracara Real Time Response (RTR) module."""
import os

from datetime import datetime
from functools import partial
from typing import Dict, List

from falconpy import (
    OAuth2,
    RealTimeResponse,
    RealTimeResponseAdmin,
)

from caracara.common.batching import batch_get_data
from caracara.common.module import FalconApiModule
from caracara.common.pagination import all_pages_numbered_offset_parallel
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string
from caracara.modules.rtr.batch_session import RTRBatchSession


class RTRApiModule(FalconApiModule):
    """Real Time Response (RTR) API Module."""

    name = "RTR API Module"
    help = "Interface with hosts via the Real Time Response (RTR) API"

    default_timeout = 30

    def __init__(self, api_authentication: OAuth2):
        """Create an RTR module object and configure it with a FalconPy OAuth2 object."""
        super().__init__(api_authentication)
        self.rtr_api = RealTimeResponse(auth_object=self.api_authentication)
        self.rtr_admin_api = RealTimeResponseAdmin(auth_object=self.api_authentication)

    def batch_session(self) -> RTRBatchSession:
        """
        Create a new RTR batch session abstraction object.

        Once created, use the connect() function to establish a connection to a list
        of Falcon device IDs.

        Returns
        -------
        RTRBatchSession: a batch RTR session object that can connect to many systems at once
        """
        rtr_batch_session = RTRBatchSession(
            rtr_api=self.rtr_api,
            rtr_admin_api=self.rtr_admin_api,
        )
        return rtr_batch_session

    @filter_string
    def _search_sessions(self, filters: str or FalconFilter = None):
        """
        Get RTR Session IDs based on filters.

        Arguments
        ---------
        filters: FalconFilter or str, optional
            Filters to apply to the RTR session search.

        Returns
        -------
        List[str]: A list of all session IDs discovered.
        """
        self.logger.info("Searching for RTR sessions based on filter string: %s", filters)
        func = partial(self.rtr_api.list_all_sessions, filter=filters)
        session_ids = all_pages_numbered_offset_parallel(func=func, logger=self.logger)
        return session_ids

    def _get_queued_session_ids(self) -> List[str]:
        """
        Get a list of queued RTR Session IDs.

        Returns
        -------
        List[str]: A list of IDs of all queued RTR sessions discovered.
        """
        self.logger.info("Searching for queued RTR sessions")
        filter_str = "offline_queued: 1+deleted_at: null"
        session_ids = self._search_sessions(filters=filter_str)
        return session_ids

    def describe_queued_sessions(self) -> Dict:
        """
        Show the contents of all queued RTR sessions.

        Returns
        -------
        Dict: A dictionary containing all queued RTR sessions discoverd.
        """
        self.logger.info("Describing all queued RTR sessions")
        session_ids = self._get_queued_session_ids()
        session_data = batch_get_data(session_ids, self.rtr_api.list_sessions)
        return session_data

    def delete_queued_session(self, session_id: str):
        """
        Delete a queued session by ID.

        Arguments
        ---------
        session_id: str
            ID of the queued RTR session to delete.

        Returns
        -------
        None
        """
        self.logger.info("Deleting queued session with ID %s", session_id)
        self.rtr_api.delete_session(session_id)

    def delete_queued_session_command(self, session_id: str, cloud_request_id: str):
        """Delete a specific command within a queued session."""
        self.logger.info(
            "Deleting command with ID %s from queued session %s",
            cloud_request_id, session_id,
        )
        self.rtr_api.delete_queued_session(
            session_id=session_id,
            cloud_request_id=cloud_request_id
        )

    def clear_queued_sessions(self):
        """
        Clear all sessions from the RTR queue.

        This is a shortcut function provided for a common operation, and can be done
        manually without this function.

        Returns
        -------
        None
        """
        self.logger.info("Clearing all queued RTR sessions")
        session_ids = self._get_queued_session_ids()
        for session_id in session_ids:
            self.delete_queued_session(session_id)

    @filter_string
    def describe_put_files(self, filters: str or FalconFilter = None) -> Dict:
        """
        Query RTR PUT files and return a list. Falcon (FQL) filters are supported.

        Arguments
        ---------
        filters: FalconFilter or str, optional
            Filters to apply to the PUT file search.

        Returns
        -------
        Dict: a dictionary containing information about all the PUT files discovered.
        """
        self.logger.info("Querying RTR put files using the filter string %s", filters)
        func_ids = partial(self.rtr_admin_api.list_put_files, filter=filters)
        put_file_ids = all_pages_numbered_offset_parallel(
            func=func_ids,
            logger=self.logger,
        )
        self.logger.info("Retreived %d PUT file IDs", len(put_file_ids))
        self.logger.debug(put_file_ids)

        put_file_data = batch_get_data(put_file_ids, self.rtr_admin_api.get_put_files)
        return put_file_data

    def create_put_file(self, file_path: str, name: str = None, description: str = None):
        """
        Create a PUT file within the Falcon cloud for later use.

        Arguments
        ---------
        file_path: str
            Path to the file on disk to be uploaded to the Falcon Cloud
        name: str, optional
            Rename the file when uploaded to the Falcon Cloud
        description: str, optional
            Description text to add to the file.
            Defaults to "File uploaded via Caracara at <current UTC timestamp>"

        Returns
        -------
        None
        """
        if not os.path.isfile(file_path):
            self.logger.info("%s is not a valid file", file_path)
            raise Exception("You must provide the path to a valid file on disk")

        # Default to using the original filename in the case that the user doesn't
        # specify an alternative
        if name is None:
            name = os.path.basename(file_path)

        if description is None:
            timestamp_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            description = f"File uploaded via Caracara at {timestamp_str}"

        self.logger.info(
            "Uploading %s to Falcon with name %s and description %s",
            file_path, name, description,
        )

        with open(file_path, 'rb') as put_file:
            file_contents = put_file.read()

        self.rtr_admin_api.create_put_files(
            name=name,
            description=description,
            files=[(name, (name, file_contents, 'application/script'))]
        )

    def delete_put_file(self, put_file_id: str):
        """
        Delete a PUT file.

        Arguments
        ---------
        put_file_id: str
            ID of the PUT file to delete from the Falcon Cloud

        Returns
        -------
        None
        """
        self.logger.info("Deleting PUT file with ID %s", put_file_id)
        self.rtr_admin_api.delete_put_files(put_file_id)

    @filter_string
    def describe_scripts(self, filters: str or FalconFilter = None) -> Dict:
        """
        Query RTR scripts and return a list. Falcon (FQL) filters are supported.

        Arguments
        ---------
        filters: str or FalconFilter, optional
            Filters to apply to the script search

        Returns
        -------
        Dict: a dictionary containing a list of every script uploaded to the Falcon Cloud,
            including its contents
        """
        self.logger.info("Querying RTR scripts using the filter string %s", filters)
        func_ids = partial(self.rtr_admin_api.list_scripts, filter=filters)
        script_ids = all_pages_numbered_offset_parallel(
            func=func_ids,
            logger=self.logger,
        )
        self.logger.info("Retreived %d script file IDs", len(script_ids))
        self.logger.debug(script_ids)

        script_data = batch_get_data(script_ids, self.rtr_admin_api.get_scripts)
        return script_data
