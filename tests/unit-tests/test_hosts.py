from unittest.mock import patch
from caracara import Client
import falconpy


mock_devices = {
    "00000000000000000000000000000000": {
        "device_id": "00000000000000000000000000000000",
    },
    "00000000000000000000000000000001": {
        "device_id": "00000000000000000000000000000001",
    },
    "00000000000000000000000000000002": {
        "device_id": "00000000000000000000000000000002",
        "host_hidden_status": "hidden",
    },
    "00000000000000000000000000000003": {
        "device_id": "00000000000000000000000000000003",
        "host_hidden_status": "hidden",
    },
}
visible_ids = [i for i, dev in mock_devices.items() if dev.get("host_hidden_status") != "hidden"]
hidden_ids = [i for i, dev in mock_devices.items() if dev.get("host_hidden_status") == "hidden"]


def mock_query_devices_by_filter_scroll(*, filter, limit, offset):
    assert filter is None

    if offset is None:
        offset = 0

    return {
        "body": {
            "resources": visible_ids[offset:offset+limit],
            "meta": {
                "pagination": {
                    "total": len(visible_ids),
                },
            },
        },
    }


def mock_query_hidden_devices(*, filter, limit, offset):
    assert filter is None

    if offset is None:
        offset = 0

    return {
        "body": {
            "resources": hidden_ids[offset:offset+limit],
            "meta": {
                "pagination": {
                    "total": len(hidden_ids),
                },
            },
        },
    }


def mock_get_device_details(ids, *, parameters=None):
    return {
        "body": {
            "resources": [mock_devices[id_] for id_ in ids]
        },
    }


def hosts_test():
    """Decorator that contains common functionality between all hosts tests."""
    def decorator(func):
        @patch("caracara.modules.hosts.hosts.HostGroup", autospec=falconpy.HostGroup)
        @patch("caracara.modules.hosts.hosts.Hosts", autospec=falconpy.Hosts)
        @patch("caracara.client.OAuth2")
        def new_func(mock_oauth2, mock_hosts, mock_hostgroup):
            # B106 is a bandit warning for hardcoded passwords, this is a testing context and
            # the credentials passed to this constructor aren't valid and aren't used.
            auth = Client(  # nosec B106:hardcoded_password_funcarg
                client_id="testing id",
                client_secret="testing secret",
                cloud_name="auto",
            )

            return func(
                auth=auth,
                mock_oauth2=mock_oauth2,
                mock_hosts=mock_hosts,
                mock_hostgroup=mock_hostgroup,
            )
        return new_func
    return decorator


@hosts_test()
def test_describe_devices(auth: Client, **_):
    # Mock falconpy methods
    auth.hosts.hosts_api.configure_mock(**{
        "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
        "get_device_details.side_effect": mock_get_device_details,
    })

    visible_devices = dict(
        (id_, dev) for id_, dev in mock_devices.items() if dev.get("host_hidden_status") != "hidden"
    )
    assert auth.hosts.describe_devices() == visible_devices


@hosts_test()
def test_describe_hidden_devices(auth: Client, **_):
    # Mock falconpy methods
    auth.hosts.hosts_api.configure_mock(**{
        "query_hidden_devices.side_effect": mock_query_hidden_devices,
        "get_device_details.side_effect": mock_get_device_details,
    })

    hidden_devices = dict(
        (i, dev) for i, dev in mock_devices.items() if dev.get("host_hidden_status") == "hidden"
    )
    assert auth.hosts.describe_hidden_devices() == hidden_devices


@hosts_test()
def test_describe_login_history(auth: Client, **_):
    mock_login_history = {
        "00000000000000000000000000000000": {
            "device_id": "00000000000000000000000000000000",
            "recent_logins": [
                {
                    "login_time": "2022-01-01T10:00:00Z",
                    "user_name": "MockUser1",
                },
                {
                    "login_time": "2022-01-01T12:00:00Z",
                    "user_name": "MockUser2",
                },
            ],
        },
        "00000000000000000000000000000001": {
            "device_id": "00000000000000000000000000000001",
            "recent_logins": [
                {
                    "login_time": "2022-01-01T10:00:00Z",
                    "user_name": "MockUser1",
                },
            ],
        },
    }

    def mock_query_device_login_history(ids):
        return {
            "body": {
                "resources": [mock_login_history[id_] for id_ in ids],
            },
        }

    # Mock falconpy methods
    auth.hosts.hosts_api.configure_mock(
        query_devices_by_filter_scroll=mock_query_devices_by_filter_scroll,
        query_device_login_history=mock_query_device_login_history,
    )

    assert auth.hosts.describe_login_history() == mock_login_history


@hosts_test()
def test_describe_network_address_history(auth: Client, **_):
    # There are only entries for the visible devices
    mock_network_history = {
        "00000000000000000000000000000000": {
            "device_id": "00000000000000000000000000000000",
            "history": [
                {
                    "ip_address": "123.34.56.78",
                    "mac_address": "00:00:00:00:00:00",
                    "timestamp": "2022-01-01T10:00:00Z",
                },
                {
                    "ip_address": "87.65.43.21",
                    "mac_address": "00:00:00:00:00:01",
                    "login_time": "2022-01-01T12:00:00Z",
                },
            ],
        },
        "00000000000000000000000000000001": {
            "device_id": "00000000000000000000000000000001",
            "history": [
                {
                    "ip_address": "111.111.111.111",
                    "mac_address": "00:00:00:00:00:02",
                    "timestamp": "2022-01-01T10:00:00Z",
                },
            ],
        },
    }

    def mock_query_network_address_history(ids):
        return {
            "body": {
                "resources": [mock_network_history[id_] for id_ in ids],
            },
        }

    # Mock falconpy methods
    auth.hosts.hosts_api.configure_mock(
        query_devices_by_filter_scroll=mock_query_devices_by_filter_scroll,
        query_network_address_history=mock_query_network_address_history,
    )

    assert auth.hosts.describe_network_address_history() == mock_network_history


@hosts_test()
def test_contain(auth: Client, **_):
    resources = []

    def mock_perform_action(*, ids, action_name):
        return {
            "body": {
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(**{
        "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
        "perform_action.side_effect": mock_perform_action,
    })

    assert auth.hosts.contain() == resources
    auth.hosts.hosts_api.perform_action.assert_called_once_with(
        ids=visible_ids, action_name="contain",
    )


@hosts_test()
def test_release(auth: Client, **_):
    resources = []

    def mock_perform_action(*, ids, action_name):
        return {
            "body": {
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(**{
        "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
        "perform_action.side_effect": mock_perform_action,
    })

    assert auth.hosts.release() == resources
    auth.hosts.hosts_api.perform_action.assert_called_once_with(
        ids=visible_ids, action_name="lift_containment",
    )


@hosts_test()
def test_hide(auth: Client, **_):
    resources = []

    def mock_perform_action(*, ids, action_name):
        return {
            "body": {
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(**{
        "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
        "perform_action.side_effect": mock_perform_action,
    })

    assert auth.hosts.hide() == resources
    auth.hosts.hosts_api.perform_action.assert_called_once_with(
        ids=visible_ids, action_name="hide_host",
    )


@hosts_test()
def test_unhide(auth: Client, **_):
    resources = []

    def mock_perform_action(*, ids, action_name):
        return {
            "body": {
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(**{
        "query_hidden_devices.side_effect": mock_query_hidden_devices,
        "perform_action.side_effect": mock_perform_action,
    })

    assert auth.hosts.unhide() == resources
    auth.hosts.hosts_api.perform_action.assert_called_once_with(
        ids=hidden_ids, action_name="unhide_host",
    )


@hosts_test()
def test_tag(auth: Client, **_):
    resources = []
    tags = ["tag1", "tag2"]

    def mock_update_device_tags(*, action_name, ids, tags):
        return {
            "body": {
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(**{
        "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
        "update_device_tags.side_effect": mock_update_device_tags,
    })

    assert auth.hosts.tag(tags) == resources
    auth.hosts.hosts_api.update_device_tags.assert_called_once_with(
        action_name="add", ids=visible_ids, tags=tags
    )


@hosts_test()
def test_untag(auth: Client, **_):
    resources = []
    tags = ["tag1", "tag2"]

    def mock_update_device_tags(*, action_name, ids, tags):
        return {
            "body": {
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(**{
        "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
        "update_device_tags.side_effect": mock_update_device_tags,
    })

    assert auth.hosts.untag(tags) == resources
    auth.hosts.hosts_api.update_device_tags.assert_called_once_with(
        action_name="remove", ids=visible_ids, tags=tags
    )


@hosts_test()
def test_get_device_ids(auth: Client, **_):
    auth.hosts.hosts_api.configure_mock(**{
        "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
    })

    assert auth.hosts.get_device_ids() == visible_ids


@hosts_test()
def test_get_hidden_ids(auth: Client, **_):
    auth.hosts.hosts_api.configure_mock(**{
        "query_hidden_devices.side_effect": mock_query_hidden_devices,
    })

    assert auth.hosts.get_hidden_ids() == hidden_ids
