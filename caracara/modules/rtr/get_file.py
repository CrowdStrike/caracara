"""RTR Batch GET abstraction module."""
from __future__ import annotations

import os

from dataclasses import dataclass
from typing import TYPE_CHECKING

import py7zr


if TYPE_CHECKING:
    # This trick will avoid us from causing a cyclical reference within the class
    # Credit: https://stackoverflow.com/a/39757388
    from caracara.modules.rtr.batch_session import RTRBatchSession


@dataclass
class GetFile:
    """
    Represents a file uploaded to Falcon via a GET command.

    This class may be instantiated many times, with each object stored in a common list,
    in order to represent many files retrieved from a GET comamnd executed against a
    batch session.
    """

    device_id: str = None
    filename: str = None
    session_id: str = None
    sha256: str = None
    size: int = None
    batch_session: RTRBatchSession = None

    def download(
        self,
        output_path: str,
        extract: bool = True,
        preserve_7z: bool = False,
    ):
        """
        Download a file to a specified path.

        If the path is a folder, the filename will be auto generated.
        If the path is a file, it'll be downloaded to that path and name.
        """
        if self.filename.startswith("/"):
            # macOS or *nix path
            filename = self.filename.rsplit("/", maxsplit=1)[-1]
        else:
            # Windows filename
            filename = self.filename.rsplit("\\", maxsplit=1)[-1]

        filename_noext, ext = os.path.splitext(filename)

        if os.path.isdir(output_path):
            # Output path is a folder, so we should compute the filename
            full_output_path = os.path.join(
                output_path,
                f"{filename_noext}_{self.sha256}_{self.device_id}{ext}",
            )
            full_output_path_7z = full_output_path + ".7z"
        else:
            full_output_path = output_path
            if extract:
                full_output_path_7z = full_output_path + ".7z"
            else:
                # We should ensure that the user's path ends in .7z if they are not extracting
                if not full_output_path.endswith(".7z"):
                    full_output_path_7z = full_output_path + ".7z"

        file_contents = self.batch_session.api.get_extracted_file_contents(
            session_id=self.session_id,
            sha256=self.sha256,
            filename=self.filename,
        )

        with open(full_output_path_7z, 'wb') as output_7z_file:
            output_7z_file.write(file_contents)

        if not extract:
            # Downloaded, so we're done now!
            return

        with py7zr.SevenZipFile(  # nosec - The password 'infected' is generic and always the same
            file=full_output_path_7z,
            mode='r',
            password='infected',
        ) as archive:
            inner_filename = archive.getnames()[0]
            target_dir = os.path.dirname(full_output_path_7z)

            archive.extract(target_dir, inner_filename)
            os.rename(
                os.path.join(target_dir, inner_filename),
                full_output_path,
            )

            if not preserve_7z:
                os.unlink(full_output_path_7z)

    def __str__(self):
        """Return a loggable string representing the contents of the object."""
        return f"Filename {self.filename} | Session ID: {self.session_id} | SHA256: {self.sha256}"
