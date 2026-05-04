"""Falcon Sensor Download API."""

import hashlib
import os
from functools import partial
from typing import Dict, List, Literal, Optional, Union

from tqdm import tqdm

from falconpy import OAuth2, SensorDownload

from caracara.common.exceptions import GenericAPIError
from caracara.common.module import FalconApiModule, ModuleMapper
from caracara.common.pagination import all_pages_numbered_offset_parallel
from caracara.filters import FalconFilter
from caracara.filters.decorators import filter_string

# Default chunk size for streaming downloads. Matches the RTR get-file default.
# Benchmarking across multiple sessions showed no consistent throughput difference
# between 1 MiB and larger sizes (e.g. 16 MiB) — server-side variance dominates.
# 1 MiB gives ~16x more progress bar updates for a typical 100+ MiB installer.
DOWNLOAD_CHUNK_SIZE = 1 * 1024 * 1024  # 1 MiB


class SensorDownloadApiModule(FalconApiModule):
    """
    Sensor Download API Module.

    This module exposes sensor installer search, metadata retrieval, and download
    functionality, as well as the ability to retrieve the (C)CID for the authenticated tenant.
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

    @filter_string
    def describe_installers(
        self,
        filters: Union[FalconFilter, str] = None,
        sort: str = None,
    ) -> List[Dict]:
        """Return full metadata for all sensor installers matching the provided filters.

        Uses the V3 combined endpoint, which includes LTS flags and architecture data in
        addition to the base V1 fields (name, version, platform, os, sha256, release_date,
        file_size, file_type, description).

        Arguments
        ---------
        filters: Union[FalconFilter, str], optional
            FQL filter string or FalconFilter object. Use dialect='sensor_download' when
            constructing a FalconFilter to get sensor installer-specific filter suggestions.
        sort: str, optional
            Sort field and direction, e.g. 'version|desc' or 'release_date|asc'.

        Returns
        -------
        List[Dict]: A list of installer metadata dictionaries ordered by the chosen sort.
        """
        self.logger.info(
            "Describing sensor installers with filter '%s', sort '%s'", filters, sort
        )
        func = partial(
            self.sensor_download_api.get_combined_sensor_installers_by_query_v3,
            filter=filters,
            sort=sort,
        )
        installers = all_pages_numbered_offset_parallel(
            func=func,
            logger=self.logger,
            limit=500,
        )
        self.logger.info("Retrieved %d sensor installer(s)", len(installers))
        return installers

    @filter_string
    def get_installer_ids(
        self,
        filters: Union[FalconFilter, str] = None,
        sort: str = None,
    ) -> List[str]:
        """Return the SHA256 hashes of all sensor installers matching the provided filters.

        Arguments
        ---------
        filters: Union[FalconFilter, str], optional
            FQL filter string or FalconFilter object. Use dialect='sensor_download' when
            constructing a FalconFilter to get sensor installer-specific filter suggestions.
        sort: str, optional
            Sort field and direction, e.g. 'version|desc' or 'release_date|asc'.

        Returns
        -------
        List[str]: A list of SHA256 hashes for each matching sensor installer. These can
            be passed directly to download_installer().
        """
        self.logger.info(
            "Fetching sensor installer IDs with filter '%s', sort '%s'", filters, sort
        )
        func = partial(
            self.sensor_download_api.get_sensor_installers_by_query_v3,
            filter=filters,
            sort=sort,
        )
        installer_ids = all_pages_numbered_offset_parallel(
            func=func,
            logger=self.logger,
            limit=500,
        )
        self.logger.info("Retrieved %d sensor installer ID(s)", len(installer_ids))
        return installer_ids

    def _get_installer_metadata(self, sha256: str) -> Dict:
        """Retrieve V3 metadata for a single installer by its SHA256 hash."""
        self.logger.info("Fetching installer metadata for SHA256: %s", sha256)
        response = self.sensor_download_api.get_sensor_installer_entities_v3(ids=sha256)
        self.logger.debug(response)
        try:
            resources = response["body"]["resources"]
            if not resources:
                raise GenericAPIError(response["body"].get("errors", []))
            return resources[0]
        except (KeyError, IndexError) as exc:
            raise GenericAPIError(response["body"].get("errors", [])) from exc

    def download_installer(
        self,
        sha256: str,
        destination_path: str,
        filename: Optional[str] = None,
        include_version: bool = False,
        if_exists: Literal["error", "skip", "overwrite"] = "error",
        show_progress: bool = True,
        download_chunk_size: int = DOWNLOAD_CHUNK_SIZE,
    ) -> str:
        """Download a sensor installer to disk by its SHA256 hash, verifying integrity.

        The file is downloaded in chunks (streaming) to avoid loading the full installer
        into memory. After writing, the SHA256 of the downloaded bytes is verified against
        the expected hash; a mismatch raises ValueError and removes the partial file.

        Note: the underlying download uses DownloadSensorInstallerByIdV2 rather than V3.
        FalconPy's V3 wrapper does not expose stream=True to process_service_request, so
        streaming is unavailable via that method. All other endpoints in this module use V3.

        Arguments
        ---------
        sha256: str
            SHA256 hash of the installer to download. Also used as the API lookup key.
        destination_path: str
            Directory path where the installer file will be saved (created if absent).
        filename: str, optional
            Override the saved filename. Defaults to the canonical installer name from
            the Falcon cloud (e.g. FalconSensor_Windows.exe). When provided,
            include_version is ignored.
        include_version: bool, optional
            When True and filename is not set, the sensor version is embedded before the
            file extension (e.g. FalconSensor_Windows-7.32.20406.exe). Useful when
            downloading multiple versions of the same platform to the same directory.
            Default False.
        if_exists: "error" | "skip" | "overwrite", optional
            Behaviour when the destination file already exists.
            "error"     — raise FileExistsError (default).
            "skip"      — return the existing path without re-downloading.
            "overwrite" — replace the existing file.
        show_progress: bool, optional
            Display a tqdm progress bar while downloading. Default True.
        download_chunk_size: int, optional
            HTTP streaming chunk size in bytes. Default 1 MiB.

        Returns
        -------
        str: Full path to the downloaded installer file.

        Raises
        ------
        FileExistsError: Destination file already exists and if_exists="error".
        GenericAPIError: API returned an error status.
        ValueError: Downloaded file SHA256 does not match the expected hash.
        """
        self.logger.info("Downloading sensor installer with SHA256: %s", sha256)

        file_size = None
        if filename is None:
            metadata = self._get_installer_metadata(sha256)
            base_name = metadata["name"]
            file_size = metadata.get("file_size")
            if include_version:
                version = metadata.get("version", "")
                if version:
                    stem, ext = os.path.splitext(base_name)
                    filename = f"{stem}-{version}{ext}"
                else:
                    filename = base_name
            else:
                filename = base_name
            self.logger.info("Using installer filename: %s", filename)

        os.makedirs(destination_path, exist_ok=True)
        full_path = os.path.join(destination_path, filename)

        if os.path.exists(full_path):
            if if_exists == "error":
                raise FileExistsError(
                    f"{full_path} already exists. Use include_version=True to embed the "
                    "sensor version in the filename, or if_exists='overwrite' to replace it."
                )
            if if_exists == "skip":
                self.logger.info("Skipping download; file already exists: %s", full_path)
                return full_path
            # if_exists == "overwrite" — fall through to download

        self.logger.info("Streaming %s to %s", filename, destination_path)

        response = self.sensor_download_api.download_sensor_installer_v2(
            id=sha256,
            stream=True,
        )

        if isinstance(response, dict):
            raise GenericAPIError(response.get("body", {}).get("errors", []))

        full_path = os.path.join(destination_path, filename)
        hasher = hashlib.sha256()

        try:
            if show_progress:
                with tqdm.wrapattr(
                    stream=open(full_path, "wb"),  # noqa: WPS515
                    method="write",
                    total=file_size or 0,
                    miniters=1,
                    bytes=True,
                    desc=filename,
                ) as output_file:
                    for chunk in response.iter_content(chunk_size=download_chunk_size):
                        if chunk:
                            hasher.update(chunk)
                            output_file.write(chunk)
                    # Explicitly flush buffered data before the context manager closes.
                    # See: https://github.com/tqdm/tqdm/issues/1247
                    output_file.close()
            else:
                with open(full_path, "wb") as output_file:
                    for chunk in response.iter_content(chunk_size=download_chunk_size):
                        if chunk:
                            hasher.update(chunk)
                            output_file.write(chunk)
        except Exception:
            if os.path.exists(full_path):
                os.remove(full_path)
            raise

        actual_sha256 = hasher.hexdigest()
        if actual_sha256.lower() != sha256.lower():
            os.remove(full_path)
            raise ValueError(
                f"SHA256 mismatch for {filename}: expected {sha256}, got {actual_sha256}"
            )

        self.logger.info("Installer downloaded and verified successfully: %s", full_path)
        return full_path
