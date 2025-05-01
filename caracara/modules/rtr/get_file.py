"""RTR Batch GET abstraction module."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Tuple

import py7zr
import py7zr.callbacks
from tqdm import tqdm

if TYPE_CHECKING:
    # This trick will avoid us from causing a cyclical reference within the class
    # Credit: https://stackoverflow.com/a/39757388
    from falconpy import RealTimeResponse

    from caracara import Client
    from caracara.modules.rtr.batch_session import RTRBatchSession


class SevenZipExtractProgressBar(py7zr.callbacks.ExtractCallback, tqdm):
    """A progress bar extractor for py7zr.

    This code is heavily based on an example published on GitHub here:
        https://github.com/miurahr/py7zr/pull/558
    """

    def __init__(self, *args, total_bytes: int, **kwargs):
        """Initialise the progress bar."""
        super().__init__(self, *args, total=total_bytes, **kwargs)

    def report_start_preparation(self):
        """No start preparation callback needed."""

    def report_start(self, processing_file_path, processing_bytes):
        """No start callback needed."""

    def report_end(self, processing_file_path, wrote_bytes):
        """No end callback needed."""

    def report_update(self, decompressed_bytes):
        """Update the progress bar."""
        self.update(int(decompressed_bytes))

    def report_postprocess(self):
        """No post-process callback needed."""

    def report_warning(self, message):
        """No warning callback needed."""


@dataclass
class GetFile:
    """Represent a file uploaded to Falcon via a GET command.

    This class may be instantiated many times, with each object stored in a common list,
    in order to represent many files retrieved from a GET comamnd executed against a
    batch session.

    Only one of batch_session, client, or rtr_api need to be set. When the rtr_api property
    is called, a RealTimeResponse object will be returned according to this priority list:
    - _rtr_api (i.e., rtr_api is set via the GetFile object's property setter)
    - client.rtr.rtr_api
    - batch_session.api
    """

    device_id: str = None
    filename: str = None
    session_id: str = None
    sha256: str = None
    size: int = None
    batch_session: RTRBatchSession = None
    client: Client = None
    _rtr_api: RealTimeResponse = None

    @property
    def rtr_api(self) -> RealTimeResponse:
        """Property that returns an authenticated RealTimeResponse FalconPy object."""
        if self._rtr_api:
            return self._rtr_api
        if self.client:
            return self.client.rtr.rtr_api
        if self.batch_session:
            return self.batch_session.api
        raise AttributeError(
            "You must set at least one of batch_session, client, or rtr_api, so that this object "
            "can access the FalconPy Real Time Response API wrapper."
        )

    @rtr_api.setter
    def rtr_api(self, v: RealTimeResponse) -> None:
        self._rtr_api = v

    def _download_derive_output_paths(self, output_path: str, extract: bool) -> Tuple[str, str]:
        """Derive the output filename of a GET file downloaded from the CrowdStrike cloud."""
        # Get the name of the uploaded file from the filename value, which actually contains the
        # full path to the file on the origin system's disk.
        if self.filename.startswith("/"):
            # macOS or *nix path
            filename = self.filename.rsplit("/", maxsplit=1)[-1]
        else:
            # Windows filename
            filename = self.filename.rsplit("\\", maxsplit=1)[-1]

        filename_noext, ext = os.path.splitext(filename)

        # Figure out what the file should be named.
        # If a directory is provided as an output, we rename the file according to its name,
        # hash and origin device AID.
        # Otherwise, we use the exact filename provided as a parameter.
        if os.path.isdir(output_path):
            # Output path is a folder, so we should compute the filename
            if self.device_id:
                output_filename = f"{filename_noext}_{self.sha256}_{self.device_id}{ext}"
            else:
                output_filename = f"{filename_noext}_{self.sha256}{ext}"

            full_output_path = os.path.join(
                output_path,
                output_filename,
            )
            full_output_path_7z = full_output_path + ".7z"
        else:
            full_output_path = output_path
            if extract:
                full_output_path_7z = full_output_path + ".7z"
            else:
                # We should ensure that the user's path ends in .7z if they are not extracting
                if full_output_path.endswith(".7z"):
                    full_output_path_7z = full_output_path
                else:
                    full_output_path_7z = full_output_path + ".7z"

        return full_output_path, full_output_path_7z

    def _extract_downloaded_7z(
        self, archive_path: str, output_path: str, show_extraction_progress: bool
    ) -> None:
        """Extract the downloaded 7-Zip archive if requested."""
        target_dir = os.path.dirname(archive_path)

        with py7zr.SevenZipFile(  # nosec - The password "infected" is generic and always the same
            file=archive_path,
            mode="r",
            password="infected",
        ) as archive:
            archive_filenames = archive.getnames()
            if show_extraction_progress:
                archive_info = archive.archiveinfo()
                with SevenZipExtractProgressBar(
                    unit="B",
                    unit_scale=True,
                    miniters=1,
                    total_bytes=archive_info.uncompressed,
                    desc="Extracting...",
                    ascii=True,
                ) as progress:
                    # archive.extract() does not provide a callback parameter, but behaviour should
                    # not differ since RTR 7-Zip archives should always contain exactly one inner
                    # file.
                    archive.extractall(path=target_dir, callback=progress)
            else:
                archive.extract(path=target_dir)

        # Check that we truly only received exactly one output file in the 7-Zip archive.
        # If all is well, we rename the first (and hopefully only) output file to match the name
        # derived at the beginning of this function.
        if archive_filenames and len(archive_filenames) == 1:
            orig_filename = archive_filenames[0]
            orig_path = os.path.join(target_dir, orig_filename)
            os.rename(orig_path, output_path)
        else:
            raise ValueError(
                "The downloaded 7-Zip archive contains the wrong number of files. "
                f"Contents: {str(archive_filenames)}"
            )

    def download(
        self,
        output_path: str,
        extract: bool = True,
        preserve_7z: bool = False,
        show_download_progress: bool = False,
        download_chunk_size: int = 1048576,  # 1MiB
    ):
        """Download a file to a specified path.

        If the path is a folder, the filename will be auto generated.
        If the path is a file, it'll be downloaded to that path and name.

        All downloads require that the following three attributes be set in the GetFile object:
        - session_id (RTR Session ID)
        - sha256 (SHA256 hash of the extracted file)
        - filename (name of the extracted file)
        These three values are all returned when the status of a GET command is queried.

        Additionally, this function requires that a Device ID (AID) be stored within the GetFile
        object to include the Device ID in the eventual filename. If this is not provided, and
        output_path is set to a directory, the AID will be excluded from the calculated eventual
        file name. Note that this is irrelevant if output_path is NOT a path to a directory, as
        the filename provided to this parameter will be used instead of one derived by the library.

        Other parameters:
        - show_download_progress: Whether or not to draw the download progress via TQDM.
        - download_chunk_size: Size of each chunk to stream via requests. Defaults to 1MiB.
                               If this is set to 0, chunking will not be used.
        """
        if not self.session_id or not self.sha256 or not self.filename:
            raise ValueError(
                "A session ID, SHA256 hash, and filename are all required to download a GET file. "
                "Ensure these values are set in the object before calling the download function."
            )

        full_output_path, full_output_path_7z = self._download_derive_output_paths(
            output_path,
            extract,
        )

        # Chunked downloads can be disabled by providing a 0 as the chunk size.
        # This is rarely advantageous, but is provided for compatability.
        # Non-chunked downloads do not support progress bars, so we just skip the tqdm invocation
        # if download_chunk_size = 0, and instead write the file straight to disk from memory.
        if download_chunk_size == 0:
            file_contents = self.rtr_api.get_extracted_file_contents(
                session_id=self.session_id,
                sha256=self.sha256,
                filename=self.filename,
            )
            with open(full_output_path_7z, "wb") as output_7z_file:
                output_7z_file.write(file_contents)
        else:
            get_file_response = self.rtr_api.get_extracted_file_contents(
                session_id=self.session_id,
                sha256=self.sha256,
                filename=self.filename,
                stream=True,
            )

            if show_download_progress:
                with tqdm.wrapattr(
                    stream=open(full_output_path_7z, "wb"),
                    method="write",
                    total=0,  # Content-Length header is not sent by RTR, so tqdm will count upwards
                    miniters=1,
                    bytes=True,
                    desc=os.path.basename(full_output_path_7z),
                ) as output_7z_file:
                    for chunk in get_file_response.iter_content(chunk_size=download_chunk_size):
                        output_7z_file.write(chunk)

                    # We have to manually close the file once the download is complete, or chunk
                    # data will not be flushed to disk and the 7-Zip archive will be unreadable by
                    # py7zr. See: https://github.com/tqdm/tqdm/issues/1247
                    output_7z_file.close()
            else:
                # If no progress bar is requested, we still use chunking to avoid storing the whole
                # 7-Zip archive into memory before writing it to disk.
                with open(full_output_path_7z, "wb") as output_7z_file:
                    for chunk in get_file_response.iter_content(chunk_size=download_chunk_size):
                        output_7z_file.write(chunk)

        if not extract:
            # Downloaded, so we're done now!
            return

        self._extract_downloaded_7z(
            archive_path=full_output_path_7z,
            output_path=full_output_path,
            show_extraction_progress=show_download_progress,
        )

        # Delete the 7-Zip archive after extracting its contents if the developer told us it
        # does not need to be preserved.
        if not preserve_7z:
            os.unlink(full_output_path_7z)

    def __str__(self):
        """Return a loggable string representing the contents of the object."""
        return f"Filename {self.filename} | Session ID: {self.session_id} | SHA256: {self.sha256}"
