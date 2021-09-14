"""File interactions"""
import os
from .._tool import Tool


class Files(Tool):
    """Class to represent File interactions"""

    def upload(self: object, raw_file: str, file_name: str):
        """
        Uploads a put file
        """
        self.display(f"  Uploading put file {file_name}")
        upload = self.api.rtr_admin.create_put_files(
                data={
                    "name": file_name,
                    "content": raw_file,
                    "description": f"RTR put file {file_name}"
                }, files=[(file_name, (file_name, raw_file, 'application/octet-stream'))]
            )
        success = bool(upload["status_code"] in [200, 409])
        if success:
            if upload["status_code"] == 200:
                self.display(f"Put file {file_name} uploaded")
                returned = upload["body"]["resources"][0]["sha256"]
            if upload["status_code"] == 409:
                self.display(f"Put file {file_name} already exists")
                returned = True  # File pre-exists, tell them so
        else:
            returned = False

        return returned

    def remove(self: object, file_name: str):
        """
        Deletes a put file
        """
        self.display(f"Removing put file {file_name}")
        delete = self.api.rtr_admin.delete_put_files(ids=self.api.rtr_admin.list_put_files(
            filter=f"name:'{file_name}'"
            )["body"]["resources"][0]
        )
        success = bool(delete["status_code"] == 200)
        if success:
            self.display(f"Put file {file_name} removed")
        else:
            self.display(f"Unable to remove put file {file_name}")

        return success

    def download(self: object, session_id: str, file_name: str = None):
        """Downloads a file that has been uploaded to CrowdStrike cloud with the GET command"""
        returned = False
        self.display("Retrieving file list")
        file_list = self.api.rtr.list_files(session_id=session_id)
        if file_list["body"]["resources"]:
            self.display("Reviewing file list")
            for file_item in file_list["body"]["resources"]:
                retrieve_id = file_item["sha256"]
                self.display("Initiating download")
                clean_name = file_name.replace("/", "_")
                if clean_name[:1] == "_":
                    clean_name = clean_name[1:]
                download = self.api.rtr.get_extracted_file_contents(
                    sha256=retrieve_id,
                    session_id=session_id,
                    file_name=f"{clean_name}_download.zip"
                )
                if not isinstance(download, dict):
                    self.display("Saving to local file")
                    if not os.path.isdir("download"):
                        os.mkdir("download")
                    with open(f"download/{clean_name}_download.zip", "wb+") as download_file:
                        download_file.write(download)
                        returned = True

        return returned
