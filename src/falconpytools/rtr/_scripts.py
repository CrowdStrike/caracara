"""Script interactions"""
from .._tool import Tool


class Scripts(Tool):
    """Class to represent Script interactions"""

    def upload(self: object, script: str, script_name: str):
        """
        Uploads a script
        """
        self.display(f"  Uploading script {script_name}")
        upload = self.api.rtr_admin.create_scripts(
                data={
                    "name": script_name,
                    "content": script,
                    "platform": "linux",            # need params for these
                    "permission_type": "private",   # need params for these
                    "description": f"RTR script {script_name}"
                }, files=[(script_name, (script_name, 'application/script'))]
            )
        self.display(f"  Script {script_name} uploaded")

        return bool(upload["status_code"] in [200, 409])

    def remove(self: object, script_name: str):
        """
        Deletes a script
        """
        self.display(f"  Removing script {script_name}")
        delete = self.api.rtr_admin.delete_scripts(ids=self.api.rtr_admin.list_scripts(
            filter=f"name:'{script_name}'"
            )["body"]["resources"][0]
        )
        self.display(f"  Script {script_name} removed")

        return bool(delete["status_code"] == 200)
