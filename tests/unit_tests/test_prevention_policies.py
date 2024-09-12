"""Unit tests for PreventionPoliciesApiModule"""

import copy
from unittest.mock import patch

import falconpy

from caracara import Client, Policy
from caracara.common.sorting import SORT_ASC


def prevpol_test():
    """Decorator that contains common functionality between all prevention policy tests."""

    def decorator(func):
        @patch(
            "caracara.modules.prevention_policies.prevention_policies.PreventionPolicies",
            autospec=falconpy.PreventionPolicies,
        )
        @patch("caracara.client.OAuth2")
        def test_new_func(mock_oauth2, mock_prevpol):
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
                mock_prevpol=mock_prevpol,
            )

        return test_new_func

    return decorator


# Disabling this warning because these are not publicly shared constants; they're just locally
# shared test variables. The reused mock function also does not need a docstring, as its purpose
# is conveyed by the function it's mocking.
# pylint: disable=invalid-name,missing-function-docstring
test_filters = None
test_sort = SORT_ASC

mock_policies = [
    {
        "id": "00000000000000000000000000000000",
        "cid": "00000000000000000000000000000001",
        "name": "Test Policy",
        "description": "Test desc",
        "platform_name": "Mac",
        "groups": [],
        "enabled": True,
        "created_by": "test.person@crowdstrike.test",
        "created_timestamp": "2019-02-14T19:57:16.315431783Z",
        "modified_by": "test.person@crowdstrike.test",
        "modified_timestamp": "2019-02-14T19:57:16.315431783Z",
        "prevention_settings": [],
        "ioa_rule_groups": [],
    },
]


def mock_query_combined_policies(filter, sort, offset, limit):  # pylint: disable=redefined-builtin
    assert filter == test_filters
    assert sort == test_sort

    return {
        "body": {
            "resources": mock_policies[offset : offset + limit],
            "meta": {
                "pagination": {
                    "total": len(mock_policies),
                },
            },
        },
    }


@prevpol_test()
def test_describe_policies_raw(auth: Client, **_):
    """Unit test for PreventionPoliciesApiModule.describe_policies_raw."""

    auth.prevention_policies.prevention_policies_api.configure_mock(
        **{
            "query_combined_policies.side_effect": mock_query_combined_policies,
        }
    )

    assert (
        auth.prevention_policies.describe_policies_raw(
            filters=test_filters,
            sort=test_sort,
        )
        == mock_policies
    )


@prevpol_test()
def test_describe_policies(auth, **_):
    """Unit test for PreventionPoliciesApiModule.describe_policies"""

    auth.prevention_policies.prevention_policies_api.configure_mock(
        **{
            "query_combined_policies.side_effect": mock_query_combined_policies,
        }
    )

    results = auth.prevention_policies.describe_policies(
        filters=test_filters,
        sort=test_sort,
    )

    result_dumps = [pol.dump() for pol in results]

    assert result_dumps == mock_policies


@prevpol_test()
def test_push_policy(auth: Client, **_):
    """Unit test for PreventionPoliciesApiModule.push_policy"""

    mock_policy = {
        "name": "Test policy",
        "platform_name": "Windows",
        "description": "Test policy description",
        "prevention_settings": [],
    }
    mock_cid = "00000000000000000000000000000001"

    def mock_create_policies(body):
        # We must deep copy for assert_called_once_with to work correctly
        body = copy.deepcopy(body)
        body["resources"][0]["cid"] = mock_cid
        return {"body": body}

    auth.prevention_policies.prevention_policies_api.configure_mock(
        **{
            "create_policies.side_effect": mock_create_policies,
        }
    )

    res = auth.prevention_policies.push_policy(
        Policy(
            data_dict=mock_policy,
            style="prevention",
        )
    )

    assert res.cid == mock_cid

    auth.prevention_policies.prevention_policies_api.create_policies.assert_called_once_with(
        body={
            "resources": [mock_policy],
        },
    )
