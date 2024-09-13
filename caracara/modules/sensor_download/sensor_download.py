"""Falcon Sensor Download API."""

from falconpy import OAuth2, SensorDownload

from caracara.common.exceptions import GenericAPIError
from caracara.common.module import FalconApiModule, ModuleMapper


class SensorDownloadApiModule(FalconApiModule):
    """
    Sensor Download API Module.

    Whilst this module will eventually contain the logic required to inspect the available
    versions of the Falcon sensor available for download, its primary purpose is to allow
    other modules to retrieve the (C)CID.
    """

    name = "CrowdStrike Sensor Download API Module"
    help = "Download the Falcon sensor installer and fetch the installation CCID"

    def __init__(self, api_authentication: OAuth2, mapper: ModuleMapper):
        """Construct an instance of the SensorDownloadApiModule class."""
        super().__init__(api_authentication, mapper)
        self.logger.debug("Configuring the FalconPy Sensor Download API")
        self.sensor_download_api = SensorDownload(auth_object=self.api_authentication)

    def get_cid(self, include_checksum: bool = False) -> str:
        """Obtain the Customer ID (CID) associated with the currently authenticated API token.

        If include_checksum=True, Checksummed CID (CCID) will be returned, which includes a hyphen
        and a two character checksum appended to the CID. The CCID is required for installing the
        sensor.
        If include_checksum=False, the resultant CID will be lower-cased for broad compatibility
        outside of sensor installers.
        """
        self.logger.info("Obtaining the CCID from the cloud using the Sensor Download API")

        response = self.sensor_download_api.get_sensor_installer_ccid()
        self.logger.debug(response)

        try:
            ccid = response["body"]["resources"][0]
        except (KeyError, IndexError) as exc:
            self.logger.info(
                "Failed to retrieve the CCID from the cloud. Check your API credentials."
            )
            raise GenericAPIError(response["body"]["errors"]) from exc

        if include_checksum:
            return ccid

        # Strip the hyphen and two character checksum if we just need the CID, then send to
        # lower case.
        cid = ccid[:-3].lower()
        return cid
