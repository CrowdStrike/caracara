"""Unit tests for ResponsePoliciesApiModule"""
import copy
from unittest.mock import patch
import falconpy
from caracara import Client, Policy
from caracara.common.sorting import SORT_ASC


def respol_test():
    """Decorator that contains common functionality between all prevention policy tests."""
    def decorator(func):
        @patch(
            "caracara.modules.response_policies.response_policies.ResponsePolicies",
            autospec=falconpy.ResponsePolicies,
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


test_filters = None  # pylint: disable=invalid-name
test_sort = SORT_ASC  # pylint: disable=invalid-name


# Note that in the swagger documentation, `responses.RTResponsePolicyV1` doesn't actually
# make any mention of a cid, although the API still returns one. So we still use it.
mock_policies = [
    {
        "cid": "00000000000000000000000000000001",
        "created_by": "test.person@crowdstrike.test",
        "created_timestamp": "2019-02-14T19:57:16.315431783Z",
        "description": "Test description",
        "enabled": True,
        "groups": [],
        "id": "00000000000000000000000000000000",
        "modified_by": "test.person@crowdstrike.test",
        "modified_timestamp": "2019-02-14T19:57:16.315431783Z",
        "name": "Test Response Policy",
        "platform_name": "Mac",
        "settings": [],
    },
]


def mock_query_combined_policies(filter, sort, offset, limit):  # pylint: disable=redefined-builtin
    # pylint: disable=missing-function-docstring
    assert filter == test_filters
    assert sort == test_sort

    return {
        "body": {
            "resources": mock_policies[offset:offset+limit],
            "meta": {
                "pagination": {
                    "total": len(mock_policies)
                }
            }
        }
    }


@respol_test()
def test_describe_policies_raw(auth, **_):
    """Unit test for ResponsePoliciesApiModule.describe_policies_raw"""

    auth.response_policies.response_policies_api.configure_mock(**{
        "query_combined_policies.side_effect": mock_query_combined_policies
    })

    assert auth.response_policies.describe_policies_raw(
        filters=test_filters, sort=test_sort
    ) == mock_policies


@respol_test()
def test_describe_policies(auth, **_):
    """Unit test for ResponsePoliciesApiModule.describe_policies"""

    auth.response_policies.response_policies_api.configure_mock(**{
        "query_combined_policies.side_effect": mock_query_combined_policies
    })

    results = auth.response_policies.describe_policies(
        filters=test_filters, sort=test_sort
    )

    result_dumps = [pol.dump() for pol in results]

    assert result_dumps == mock_policies


@respol_test()
def test_push_policy(auth, **_):
    """Unit test for ResponsePoliciesApiModule.push_policy"""

    mock_policy = {
        "name": "Test policy",
        "platform_name": "Windows",
        "description": "Test policy description",
        "settings": [],
    }
    mock_cid = "00000000000000000000000000000001"

    def mock_create_policies(body):
        body = copy.deepcopy(body)  # must deep copy for assert_called_once_with to work correctly
        body["resources"][0]["cid"] = mock_cid
        return {"body": body}

    auth.response_policies.response_policies_api.configure_mock(**{
        "create_policies.side_effect": mock_create_policies
    })

    res = auth.response_policies.push_policy(Policy(data_dict=mock_policy, style="response"))

    assert res.cid == mock_cid

    auth.response_policies.response_policies_api.create_policies.assert_called_once_with(
        body={"resources": [mock_policy]}
    )


@respol_test()
def test_add_policy_to_group(auth, **_):
    """Unit test for ResponsePoliciesApiModule.add_policy_to_group"""
    policy_id = "00000000000000000000000000000000"
    group_id = "00000000000000000000000000000000"
    policy = mock_policies[0]

    def mock_query_combined_policies_(filter):  # pylint: disable=redefined-builtin
        assert filter == f"id: '{policy_id}'"

        return {
            "body": {
                "resources": [policy],
                "meta": {
                    "pagination": {
                        "total": 1,
                    }
                }
            }
        }

    auth.response_policies.response_policies_api.configure_mock(**{
        "query_combined_policies": mock_query_combined_policies_,
    })

    updated_policy = auth.response_policies.add_policy_to_group(policy_id, group_id)

    auth.response_policies.response_policies_api.perform_policies_action.assert_called_once_with(
        action_name="add-host-group",
        action_parameters=[{"name": "group_id", "value": group_id}],
        ids=[policy_id],
    )

    assert updated_policy.dump() == policy


@respol_test()
def test_modify_policy(auth, **_):
    """Unit test for ResponsePoliciesApiModule.modify_policy"""
    raw_policy = mock_policies[0]

    raw_updated_policy = copy.deepcopy(raw_policy)
    raw_updated_policy["id"] = "11111111111111111111111111111111"

    policy = Policy(data_dict=raw_policy, style="response")

    def mock_update_policies(body):  # pylint: disable=unused-argument
        return {
            "body": {
                "resources": [raw_updated_policy]
            }
        }

    auth.response_policies.response_policies_api.configure_mock(**{
        "update_policies.side_effect": mock_update_policies
    })

    updated_policy = auth.response_policies.modify_policy(policy)

    auth.response_policies.response_policies_api.update_policies.assert_called_once_with(
        body={"resources": [policy.flat_dump()]}
    )

    assert updated_policy.dump() == raw_updated_policy
