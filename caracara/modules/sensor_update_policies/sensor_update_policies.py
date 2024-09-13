"""Sensor Update Policy APIs.

This module allows for interaction with the Sensor Update policies, and facilitates
the retrieval of maintenance tokens.
"""

import datetime
from typing import Optional

from falconpy import OAuth2, SensorUpdatePolicies

from caracara.common.exceptions import BaseCaracaraError
from caracara.common.module import FalconApiModule, ModuleMapper


class SensorUpdatePoliciesApiModule(FalconApiModule):
    """This module facilitates interactions with the Sensor Update Policies API."""

    name = "CrowdStrike Sensor Update Policies API Module"
    help = "Interact with the Sensor Update Policies API, and get maintenance tokens"

    def __init__(self, api_authentication: OAuth2, mapper: ModuleMapper):
        """Construct an instance of the SensorUpdatePoliciesApiModule."""
        super().__init__(api_authentication, mapper)

        self.logger.debug("Configuring the FalconPy Sensor Update Policies module")
        self.sensor_update_policies_api = SensorUpdatePolicies(auth_object=self.api_authentication)

    def get_maintenance_token(
        self,
        device_id: str,
        audit_message: Optional[str] = None,
    ) -> str:
        """Get the maintenance token for a device.

        Arguments
        ---------
        device_id: str, required
            A Falcon Device ID (AID) to get the maintenance token for.

        audit_message: str or None
            A text string containing an audit message for the retrieval of the maintenance token.
            If left blank / None, Caracara will generate one for you.

        Returns
        -------
        str: The maintenance token.
        """
        if audit_message is None:
            timestamp = datetime.datetime.now(
                tz=datetime.timezone.utc,
            ).strftime("%Y-%m-%d %H:%M:%S")

            audit_message = f"Generated via Caracara at {timestamp} UTC"

        response = self.sensor_update_policies_api.reveal_uninstall_token(
            audit_message=audit_message,
            device_id=device_id,
        )

        if response["status_code"] == 200:
            body = response["body"]
            return body["resources"][0]["uninstall_token"]

        raise BaseCaracaraError(
            "The API operation failed to generate a maintenance token."
            "Check that you have the Sensor Update Policies - Write permission "
            "enabled on your API token."
        )

    def get_bulk_maintenance_token(self, audit_message: Optional[str] = None) -> str:
        """Get the bulk maintenance token for a Falcon tenant.

        Arguments
        ---------
        audit_message: str or None
            A text string containing an audit message for the retrieval of the maintenance token.
            If left blank / None, Caracara will generate one for you.

        Returns
        -------
        str: The bulk maintenance token.
        """
        return self.get_maintenance_token(device_id="MAINTENANCE", audit_message=audit_message)
