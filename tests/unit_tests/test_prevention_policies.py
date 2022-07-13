"""Unit tests for PreventionPoliciesApiModule"""
from unittest.mock import patch
import falconpy
from caracara import Client
from caracara.common.sorting import SORT_ASC

# A lot of mock methods need a certain function signature, and since they only mock functionality
# they do not always use all the arguments. So we disable the unused-argument warning.
# We also disable the redefined-builtin warning, as falconpy uses builtin identifiers like 'filter'
# so we must use it also in order to mock it.
# pylint: disable=unused-argument, redefined-builtin


def prevpol_test():
    """Decorator that contains common functionality between all prevention policy tests."""
    def decorator(func):
        @patch(
            "caracara.modules.prevention_policies.prevention_policies.PreventionPolicies",
            autospec=falconpy.PreventionPolicies,
        )
        @patch("caracara.client.OAuth2")
        def test_new_func(mock_oauth2, mock_prevpol):
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
                mock_prevpol=mock_prevpol,
            )
        return test_new_func
    return decorator


# @prevpol_test()
# def test_describe_devices(auth: Client, **_):
#     """Unit test for HostsApiModule.describe_devices"""
#     # Mock falconpy methods
#     auth.hosts.hosts_api.configure_mock(**{
#         "query_devices_by_filter_scroll.side_effect": mock_query_devices_by_filter_scroll,
#         "get_device_details.side_effect": mock_get_device_details,
#     })

#     visible_devices = dict(
#         (id_, dev) for id_, dev in mock_devices.items() if dev.get("host_hidden_status") != "hidd
#     )
#     assert auth.hosts.describe_devices() == visible_devices


@prevpol_test()
def test_describe_policies_raw(auth: Client, **_):
    """Unit test for PreventionPoliciesApiModule.describe_policies_raw"""
    test_filters = None
    test_sort = SORT_ASC

    # NOTE: This is not structured like an real result from the API
    resources = [
        "Not",
        "Real",
        "Test",
        "Response"
    ]

    def mock_query_combined_policies(filters, sort, offset, limit):
        assert filters == test_filters
        assert sort == test_sort

        return {
            "body": {
                "resources": resources[offset:offset+limit],
                "meta": {
                    "pagination": {
                        "total": len(resources)
                    }
                }
            }
        }
        pass

    auth.prevention_policies.prevention_policies_api.configure_mock(**{
        "query_combined_policies.side_effect": mock_query_combined_policies
    })

    assert auth.prevention_policies.describe_policies_raw() == resources


@prevpol_test()
def test_describe_policies(auth, **_):
    """Unit test for PreventionPoliciesApiModule.describe_policies"""
    assert False


@prevpol_test()
def test_new_policy(auth, **_):
    """Unit test for PreventionPoliciesApiModule.new_policy"""
    assert False


@prevpol_test()
def test_push_policy(auth, **_):
    """Unit test for PreventionPoliciesApiModule.push_policy"""
    assert False
