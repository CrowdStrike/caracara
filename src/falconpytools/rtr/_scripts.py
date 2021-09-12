"""Script interactions"""
from .._toolbox import Toolbox


class Scripts(Toolbox):
    """Class to represent Script interactions"""
    def __init__(self, key: str = None, secret: str = None, api: object = None, verbose: bool = True):
        super().__init__(key=key, secret=secret, api=api, verbose=verbose)

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
