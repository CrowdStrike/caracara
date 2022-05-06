"""
Caracara meta class.

Returns information about Caracara itself, such as its package version and
a custom user agent string based on Caracara's version.
"""

import pkg_resources

_pkg_version = pkg_resources.get_distribution("caracara").version


def user_agent_string():
    """
    Returns a user agent to be sent to CrowdStrike with API
    requests including Caracara's version.
    """
    return f"crowdstrike-caracara/{_pkg_version}"
