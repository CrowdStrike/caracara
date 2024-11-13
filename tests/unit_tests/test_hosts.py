"""Unit tests for HostsApiModule"""

from unittest.mock import patch

import falconpy
import pytest

from caracara import Client
from caracara.common.constants import OnlineState
from caracara.common.exceptions import InvalidOnlineState, MustProvideFilter

# A lot of mock methods need a certain function signature, and since they only mock functionality
# they do not always use all the arguments. Therefore, we disable the unused-argument warning.
# We also disable the redefined-builtin warning, as FalconPy uses builtin identifiers like 'filter'
# so we must use it also in order to mock it.
# pylint: disable=unused-argument, redefined-builtin

mock_devices = {
    "00000000000000000000000000000000": {
        "device_id": "00000000000000000000000000000000",
        "hostname": "TESTTEST0",
    },
    "00000000000000000000000000000001": {
        "device_id": "00000000000000000000000000000001",
        "hostname": "TESTTEST1",
    },
    "00000000000000000000000000000002": {
        "device_id": "00000000000000000000000000000002",
        "host_hidden_status": "hidden",
        "hostname": "TESTTEST2",
    },
    "00000000000000000000000000000003": {
        "device_id": "00000000000000000000000000000003",
        "host_hidden_status": "hidden",
        "hostname": "TESTTEST3",
    },
}
visible_ids = [i for i, dev in mock_devices.items() if dev.get("host_hidden_status") != "hidden"]
hidden_ids = [i for i, dev in mock_devices.items() if dev.get("host_hidden_status") == "hidden"]

mock_device_online_states = {
    "00000000000000000000000000000000": {
        "id": "00000000000000000000000000000000",
        "state": "online",
    },
    "00000000000000000000000000000001": {
        "id": "00000000000000000000000000000001",
        "state": "offline",
    },
    "00000000000000000000000000000002": {
        "id": "00000000000000000000000000000002",
        "state": "unknown",
    },
    "00000000000000000000000000000003": {
        "id": "00000000000000000000000000000003",
        "state": "online",
    },
}
online_ids = [i for i, data in mock_device_online_states.items() if data.get("state") == "online"]
offline_ids = [i for i, data in mock_device_online_states.items() if data.get("state") == "offline"]
unknown_ids = [i for i, data in mock_device_online_states.items() if data.get("state") == "unknown"]


def mock_query_devices_by_filter_scroll(*, filter, limit, offset):
    """Mock method for falconpy.Hosts.query_devices_by_filter_scroll.

    Although we use filters (pluralised) in Caracara to avoid overwriting the native Python
    filter keyword, we have to use filter here so that we match with the Falcon API spec we
    are mocking.
    """
    if offset is None:
        offset = 0

    return {
        "body": {
            "resources": visible_ids[offset : offset + limit],
            "meta": {
                "pagination": {
                    "total": len(visible_ids),
                },
            },
        },
    }


def mock_query_hidden_devices(*, filter, limit, offset):
    """Mock method for falconpy.Hosts.query_hidden_devices.

    Although we use filters (pluralised) in Caracara to avoid overwriting the native Python
    filter keyword, we have to use filter here so that we match with the Falcon API spec we
    are mocking.
    """
    if offset is None:
        offset = 0

    return {
        "body": {
            "resources": hidden_ids[offset : offset + limit],
            "meta": {
                "pagination": {
                    "total": len(hidden_ids),
                },
            },
        },
    }


def mock_get_device_details(ids, *, parameters=None):
    """Mock method for falconpy.Hosts.get_device_details"""
    return {
        "body": {"resources": [mock_devices[id_] for id_ in ids]},
    }


def mock_query_online_state(ids, *, parameters=None):
    """Mock method for falconpy.Hosts.get_device_details"""
    return {
        "body": {"resources": [mock_device_online_states[id_] for id_ in ids]},
    }


def hosts_test():
    """Decorator that contains common functionality between all hosts tests."""

    def decorator(func):
        @patch("caracara.modules.hosts.hosts.HostGroup", autospec=falconpy.HostGroup)
        @patch("caracara.modules.hosts.hosts.Hosts", autospec=falconpy.Hosts)
        @patch("caracara.client.OAuth2", autospec=True)
        def new_func(mock_oauth2, mock_hosts, mock_hostgroup):
            # B106 is a bandit warning for hardcoded passwords.
            # This is a testing context and the credentials passed to this constructor
            # are not valid, so we can legitimately disable this warning.
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
    """Unit test for HostsApiModule.describe_devices"""
    # Mock FalconPy methods
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "get_device_details.side_effect": mock_get_device_details,
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    visible_devices = dict(
        (id_, dev) for id_, dev in mock_devices.items() if dev.get("host_hidden_status") != "hidden"
    )

    assert auth.hosts.describe_devices() == visible_devices


@hosts_test()
def test_describe_devices__online_only(auth: Client, **_):
    """Unit test for HostsApiModule.describe_devices"""
    # Mock FalconPy methods
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "get_device_details.side_effect": mock_get_device_details,
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    online_visible_devices = dict(
        filter(
            lambda item: item[0] in list(set(visible_ids) & set(online_ids)),
            mock_devices.items(),
        )
    )

    assert auth.hosts.describe_devices(online_state="online") == online_visible_devices


@hosts_test()
def test_describe_devices__enum_online_state(auth: Client, **_):
    """Unit test for HostsApiModule.describe_devices"""
    # Mock FalconPy methods
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "get_device_details.side_effect": mock_get_device_details,
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    offline_visible_devices = dict(
        filter(
            lambda item: item[0] in list(set(visible_ids) & set(offline_ids)),
            mock_devices.items(),
        )
    )

    assert auth.hosts.describe_devices(online_state=OnlineState.OFFLINE) == offline_visible_devices


@hosts_test()
def test_describe_devices__invalid_online_state(auth: Client, **_):
    """Unit test for HostsApiModule.describe_devices"""
    # Mock FalconPy methods
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "get_device_details.side_effect": mock_get_device_details,
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    with pytest.raises(InvalidOnlineState):
        auth.hosts.describe_devices(online_state="notastate")


@hosts_test()
def test_describe_hidden_devices(auth: Client, **_):
    """Unit test for HostsApiModule.describe_hidden_devices"""
    # Mock FalconPy methods
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_hidden_devices.side_effect": mock_query_hidden_devices,
            "get_device_details.side_effect": mock_get_device_details,
        }
    )

    hidden_devices = dict(
        (i, dev) for i, dev in mock_devices.items() if dev.get("host_hidden_status") == "hidden"
    )
    assert auth.hosts.describe_hidden_devices() == hidden_devices


@hosts_test()
def test_describe_login_history(auth: Client, **_):
    """Unit test for HostsApiModule.describe_login_history"""
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

    # Mock FalconPy methods
    auth.hosts.hosts_api.configure_mock(
        query_devices_by_filter_scroll=mock_query_devices_by_filter_scroll,
        query_device_login_history=mock_query_device_login_history,
    )

    assert auth.hosts.describe_login_history() == mock_login_history


@hosts_test()
def test_describe_network_address_history(auth: Client, **_):
    """Unit test for HostsApiModule.describe_network_address_history"""
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

    # Mock FalconPy methods
    auth.hosts.hosts_api.configure_mock(
        query_devices_by_filter_scroll=mock_query_devices_by_filter_scroll,
        query_network_address_history=mock_query_network_address_history,
    )

    assert auth.hosts.describe_network_address_history() == mock_network_history


@hosts_test()
def test_contain_no_filter(auth: Client, **_):
    """Unit test for HostsApiModule.contain with no filter provider."""
    with pytest.raises(MustProvideFilter):
        auth.hosts.contain()


@hosts_test()
def test_contain(auth: Client, **_):
    """Unit test for HostsApiModule.contain"""
    resources = [
        "00000000000000000000000000000000",
        "00000000000000000000000000000001",
        "00000000000000000000000000000002",
        "00000000000000000000000000000003",
    ]

    def mock_perform_action(*, ids, action_name):
        return {
            "body": {
                "errors": None,
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "perform_action.side_effect": mock_perform_action,
        }
    )

    filters = auth.FalconFilter(dialect="hosts")
    filters.create_new_filter("Hostname", "TESTTEST*")

    assert auth.hosts.contain(filters=filters) == resources
    auth.hosts.hosts_api.perform_action.assert_called_once_with(
        ids=visible_ids,
        action_name="contain",
    )


@hosts_test()
def test_release(auth: Client, **_):
    """Unit test for HostsApiModule.release"""
    resources = [
        "00000000000000000000000000000000",
        "00000000000000000000000000000001",
        "00000000000000000000000000000002",
        "00000000000000000000000000000003",
    ]

    def mock_perform_action(*, ids, action_name):
        return {
            "body": {
                "errors": None,
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "perform_action.side_effect": mock_perform_action,
        }
    )

    filters = auth.FalconFilter(dialect="hosts")
    filters.create_new_filter("Hostname", "TESTTEST*")

    assert auth.hosts.release(filters=filters) == resources
    auth.hosts.hosts_api.perform_action.assert_called_once_with(
        ids=visible_ids,
        action_name="lift_containment",
    )


@hosts_test()
def test_hide(auth: Client, **_):
    """Unit test for HostsApiModule.hide"""
    resources = [
        "00000000000000000000000000000000",
        "00000000000000000000000000000001",
        "00000000000000000000000000000002",
        "00000000000000000000000000000003",
    ]

    def mock_perform_action(*, ids, action_name):
        return {
            "body": {
                "errors": None,
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "perform_action.side_effect": mock_perform_action,
        }
    )

    filters = auth.FalconFilter(dialect="hosts")
    filters.create_new_filter("Hostname", "TESTTEST*")

    assert auth.hosts.hide(filters=filters) == resources
    auth.hosts.hosts_api.perform_action.assert_called_once_with(
        ids=visible_ids,
        action_name="hide_host",
    )


@hosts_test()
def test_unhide(auth: Client, **_):
    """Unit test for HostsApiModule.unhide"""
    resources = [
        "00000000000000000000000000000000",
        "00000000000000000000000000000001",
        "00000000000000000000000000000002",
        "00000000000000000000000000000003",
    ]

    def mock_perform_action(*, ids, action_name):
        return {
            "body": {
                "errors": None,
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(
        **{
            "query_hidden_devices.side_effect": mock_query_hidden_devices,
            "perform_action.side_effect": mock_perform_action,
        }
    )

    filters = auth.FalconFilter(dialect="hosts")
    filters.create_new_filter("Hostname", "TESTTEST*")

    assert auth.hosts.unhide(filters=filters) == resources
    auth.hosts.hosts_api.perform_action.assert_called_once_with(
        ids=hidden_ids,
        action_name="unhide_host",
    )


@hosts_test()
def test_tag(auth: Client, **_):
    """Unit test for HostsApiModule.tag"""
    resources = [
        "00000000000000000000000000000000",
        "00000000000000000000000000000001",
        "00000000000000000000000000000002",
        "00000000000000000000000000000003",
    ]
    tags = ["tag1", "tag2"]

    def mock_update_device_tags(*, action_name, ids, tags):
        return {
            "body": {
                "errors": None,
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "update_device_tags.side_effect": mock_update_device_tags,
        }
    )

    filters = auth.FalconFilter(dialect="hosts")
    filters.create_new_filter("Hostname", "TESTTEST*")

    assert auth.hosts.tag(filters=filters, tags=tags) == resources
    auth.hosts.hosts_api.update_device_tags.assert_called_once_with(
        action_name="add",
        ids=visible_ids,
        tags=tags,
    )


@hosts_test()
def test_untag(auth: Client, **_):
    """Unit test for HostsApiModule.untag"""
    resources = [
        "00000000000000000000000000000000",
        "00000000000000000000000000000001",
        "00000000000000000000000000000002",
        "00000000000000000000000000000003",
    ]
    tags = ["tag1", "tag2"]

    def mock_update_device_tags(*, action_name, ids, tags):
        return {
            "body": {
                "errors": None,
                "resources": resources,
            }
        }

    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "update_device_tags.side_effect": mock_update_device_tags,
        }
    )

    filters = auth.FalconFilter(dialect="hosts")
    filters.create_new_filter("Hostname", "TESTTEST*")

    assert auth.hosts.untag(filters=filters, tags=tags) == resources
    auth.hosts.hosts_api.update_device_tags.assert_called_once_with(
        action_name="remove",
        ids=visible_ids,
        tags=tags,
    )


@hosts_test()
def test_get_device_ids(auth: Client, **_):
    """Unit test for HostsApiModule.get_device_ids"""
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
        }
    )

    assert auth.hosts.get_device_ids() == visible_ids


@hosts_test()
def test_get_device_ids__online_only(auth: Client, **_):
    """Unit test for HostsApiModule.get_device_ids"""
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    assert set(auth.hosts.get_device_ids(online_state="online")) == set(online_ids) & set(
        visible_ids
    )


@hosts_test()
def test_get_device_ids__enum_online_state(auth: Client, **_):
    """Unit test for HostsApiModule.get_device_ids"""
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    assert set(auth.hosts.get_device_ids(online_state=OnlineState.UNKNOWN)) == set(
        unknown_ids
    ) & set(visible_ids)


@hosts_test()
def test_get_device_ids__invalid_online_state(auth: Client, **_):
    """Unit test for HostsApiModule.get_device_ids"""
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    with pytest.raises(InvalidOnlineState):
        auth.hosts.get_device_ids(online_state="notastate")


@hosts_test()
def test_get_hidden_ids(auth: Client, **_):
    """Unit test for HostsApiModule.get_hidden_ids"""
    auth.hosts.hosts_api.configure_mock(
        **{
            "query_hidden_devices.side_effect": mock_query_hidden_devices,
        }
    )

    assert auth.hosts.get_hidden_ids() == hidden_ids


@hosts_test()
def test_filter_device_ids__online_only(auth: Client, **_):
    """Unit test for HostsApiModule.filter_device_ids_by_online_state"""
    auth.hosts.hosts_api.configure_mock(
        **{
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    assert (
        auth.hosts.filter_device_ids_by_online_state(
            list(mock_device_online_states.keys()),
            "online",
        )
        == online_ids
    )


@hosts_test()
def test_filter_device_ids__enum_online_state(auth: Client, **_):
    """Unit test for HostsApiModule.filter_device_ids_by_online_state"""
    auth.hosts.hosts_api.configure_mock(
        **{
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    assert (
        auth.hosts.filter_device_ids_by_online_state(
            list(mock_device_online_states.keys()),
            OnlineState.ONLINE,
        )
        == online_ids
    )


@hosts_test()
def test_filter_device_ids__invalid_online_state(auth: Client, **_):
    """Unit test for HostsApiModule.filter_device_ids_by_online_state"""
    auth.hosts.hosts_api.configure_mock(
        **{
            "get_online_state.side_effect": mock_query_online_state,
        }
    )

    with pytest.raises(InvalidOnlineState):
        auth.hosts.filter_device_ids_by_online_state(
            list(mock_device_online_states.keys()),
            "notastate",
        )
