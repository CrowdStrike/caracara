"""Host interactions"""
from .._toolbox import Toolbox


class Host(Toolbox):
    """Class to represent host interactions"""

    def __init__(self, key: str = None, secret: str = None, api: object = None, verbose: bool = True):
        super().__init__(key=key, secret=secret, api=api, verbose=verbose)

    def find_host_aid(self: object, hostname: str):
        """Retrieves a list of hosts that match the specified hostname."""
        self.display(f"Searching for hosts starting with {hostname}")
        result = self.api.hosts.query_devices_by_filter(
                                filter=f"hostname:'{hostname}*'"
                                )
        if not result["body"]["resources"]:
            resources = []
        else:
            resources = result["body"]["resources"]

        return resources

    def get_host(self: object, aid: str):
        """Retrieve details for a host"""
        self.display("Retrieving host detail")
        result = self.api.hosts.get_device_details(ids=aid)
        if not result["body"]["resources"]:
            resources = []
        else:
            resources = result["body"]["resources"]

        return resources

    def get_cid(self: object):
        """Retrieves the CID by looking at the first host"""
        self.display("Retrieving CID")
        result = self.api.hosts.query_devices_by_filter()
        if not result["body"]["resources"]:
            returned = False
        else:
            print(result)
            returned = result["body"]["resources"][0]["cid"]

        return returned
