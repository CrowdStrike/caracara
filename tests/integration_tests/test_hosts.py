"""test_hosts.py - HostsApiModule unit testing.

REQUIRED API SCOPES
    Hosts: READ, WRITE
    Host Group: READ, WRITE
"""
from .test_general import AUTH

HOST_TARGET_FILTER = "falconpy"


def test_describe_devices():
    """Test whether Caracara can return valid device data"""
    assert bool(AUTH.hosts.describe_devices()) is True


def test_describe_hidden_devices():
    """Test whether Caracara can retrieve a list of devices hidden in the Falcon UI"""
    assert bool(AUTH.hosts.describe_hidden_devices()) is True


def test_describe_login_history():
    """Retrieves the login history of hosts in Falcon"""
    assert bool(AUTH.hosts.describe_login_history()) is True


def test_describe_network_address_history():
    """Retrieves the network address history of hosts in Falcon"""
    assert bool(AUTH.hosts.describe_network_address_history()) is True


# def test_get_device_id():
#     assert bool(AUTH.hosts.get_device_ids(filters="hostname:'falconpy'"))

def test_contain_host():
    """Attempts to network contain hosts based on a hostname filter"""
    assert bool(AUTH.hosts.contain(filters=f"hostname:'{HOST_TARGET_FILTER}'")[0]["id"])


def test_release_host():
    """Attempts to release the same hosts from network containment"""
    assert bool(AUTH.hosts.release(filters=f"hostname:'{HOST_TARGET_FILTER}'")[0]["id"])


def test_hide_host():
    """Tests whether hosts can be hidden from the Falcon UI based on a hostname filter"""
    assert bool(AUTH.hosts.hide(filters=f"hostname:'{HOST_TARGET_FILTER}'")[0]["id"])


# def test_get_hidden_ids():
#     assert bool(AUTH.hosts.get_hidden_ids(filters=f"hostname:'{HOST_TARGET_FILTER}'"))


def test_unhide_host():
    """Attempts to unhide the same hosts"""
    assert bool(AUTH.hosts.unhide(filters=f"hostname:'{HOST_TARGET_FILTER}'")[0]["id"])


# def test_hide_host_the_hard_way():
#     assert bool(AUTH.hosts.hide(
#         ids_to_hide=AUTH.hosts.get_device_ids(filters=f"hostname:'{HOST_TARGET_FILTER}'")
#         )[0]["id"])

# def test_unhide_host_the_hard_way():
#     assert bool(AUTH.hosts.unhide(
#         ids_to_show=AUTH.hosts.get_hidden_ids(filters=f"hostname:'{HOST_TARGET_FILTER}'")
#         )[0]["id"])


def test_tag_host():
    """Attempts to tag hosts with a Falcon Grouping Tag based on a hostname filter"""
    assert bool(
        AUTH.hosts.tag(
            filters=f"hostname:'{HOST_TARGET_FILTER}'",
            tags="FalconGroupingTags/unittesttag"
        )[0]["updated"]
    )


def test_tag_host_list():
    """Attempts to remove the Falcon Grouping Tag from the same hosts"""
    assert bool(
        AUTH.hosts.tag(
            filters=f"hostname:'{HOST_TARGET_FILTER}'",
            tags=["FalconGroupingTags/unittesttaglist"]
        )[0]["updated"]
    )


def test_tag_host_delimit():
    """Attempts to add multiple Falcon Grouping Tags to hosts based on a hostname filter"""
    assert bool(
        AUTH.hosts.tag(
            filters=f"hostname:'{HOST_TARGET_FILTER}'",
            tags="FalconGroupingTags/unittesttagdelimit,FalconGroupingTags/unittesttagdelimit2"
        )[0]["updated"]
    )


def test_untag_host():
    """Attempts to remove the multiple listed tags from the same hosts"""
    assert bool(
        AUTH.hosts.untag(
            filters=f"hostname:'{HOST_TARGET_FILTER}'",
            tags=[
                "FalconGroupingTags/unittesttag",
                "FalconGroupingTags/unittesttaglist",
                "FalconGroupingTags/unittesttagdelimit",
                "FalconGroupingTags/unittesttagdelimit2"
            ]
        )[0]["updated"]
    )
