"""Host interactions"""
from .._toolbox import Toolbox


class Host(Toolbox):
    """Class to represent host interactions"""

    def __init__(self, key: str = None, secret: str = None, api: object = None, verbose: bool = True):
        super().__init__(key=key, secret=secret, api=api, verbose=verbose)

    def find_host_aid(self: object, hostname: str):
        """Retrieves a list of hosts that match the specified hostname."""
        self.display(f"  Searching for hosts starting with {hostname}")
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
        self.display("  Retrieving host detail")
        result = self.api.hosts.get_device_details(ids=aid)
        if not result["body"]["resources"]:
            resources = []
        else:
            resources = result["body"]["resources"]

        return resources
