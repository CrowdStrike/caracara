"""Unit tests for CustomIoaApiModule"""
import copy
from typing import Dict, List
from unittest.mock import MagicMock

import falconpy
import pytest

from caracara import Client
from caracara.modules.custom_ioa import IoaRuleGroup
from caracara.modules.custom_ioa.rules import CustomIoaRule, PatternSeverity
from caracara.modules.custom_ioa.rule_types import RuleType


@pytest.fixture
def client():
    auth = MagicMock(autospec=falconpy.OAuth2)
    client = Client(falconpy_authobject=auth)
    return client


@pytest.fixture
def custom_ioa_api(client):
    custom_ioa_api = MagicMock(autospec=falconpy.CustomIOA)
    client.custom_ioas.custom_ioa_api = custom_ioa_api
    return custom_ioa_api


@pytest.fixture
def simple_rule_type():
    rule_type = RuleType(
        id_="test_rule_type_simple",
        name="SimpleType",
        long_desc="Simple rule type for testing",
        platform="windows",
        disposition_map={1: "Test Action"},
        fields=[],
    )

    return rule_type


# Common mock functions


def create_mock_create_rule_group(assigned_id: str):
    def mock_create_rule_group(body):
        new_body = {
            "customer_id": "test_customer",
            "id": assigned_id,
            "name": body["name"],
            "description": body["description"],
            "platform": body["platform"],
            "enabled": False,
            "deleted": False,
            "rule_ids": [],
            "rules": [],
            "version": 1,
            "committed_on": "2022-01-01T12:00:00.000000000Z",
            "created_on": "2022-01-01T12:00:00.000000000Z",
            "created_by": "caracara@test.com",
            "modified_on": "2022-01-01T12:00:00.000000000Z",
            "modified_by": "caracara@test.com",
            "comment": body["comment"],
        }
        return {"body": {"resources": [new_body]}}
    return mock_create_rule_group


def create_mock_create_rule(assigned_id: str, rule_types: List[RuleType]):
    rule_type_map = dict((rule_type.id_, rule_type) for rule_type in rule_types)

    def mock_create_rule(body, comment=None):
        rule_type = rule_type_map[body["ruletype_id"]]
        new_body = {
            "customer_id": "test_customer",
            "instance_id": assigned_id,
            "name": body["name"],
            "description": body["description"],
            "pattern_id": "",  # TODO pattern_id stuff
            "pattern_severity": body["pattern_severity"],
            "disposition_id": body["disposition_id"],
            "action_label": rule_type.disposition_map[body["disposition_id"]],
            "ruletype_id": body["ruletype_id"],
            "ruletype_name": rule_type.name,
            "field_values": body["field_values"],
            "enabled": False,
            "deleted": False,
            "instance_version": 0,
            "version_ids": [0],
            "magic_cookie": 0,
            "committed_on": "2022-01-01T12:00:00.000000000Z",
            "created_on": "2022-01-01T12:00:00.000000000Z",
            "created_by": "caracara@test.com",
            "modified_on": "2022-01-01T12:00:00.000000000Z",
            "modified_by": "caracara@test.com",
            "comment": body["comment"] if comment is None else comment,
        }
        return {"body": {"resources": [new_body]}}
    return mock_create_rule


def create_mock_get_rule_types(rule_types):
    return create_mock_get_resources(
        dict((rule_type.id_, rule_type.dump(released=True, channel=0)) for rule_type in rule_types)
    )


def create_mock_query_resources(resources):
    def mock_resources(limit, offset):
        return {"body": {
            "meta": {"pagination": {"total": len(resources)}},
            "resources": resources[offset:offset+limit],
        }}
    return mock_resources


def create_mock_get_resources(resource_map):
    def mock_get_resources(ids):
        return {"body": {"resources": [resource_map[id_] for id_ in ids]}}
    return mock_get_resources


def test_create_rule_group_no_rules(client: Client, custom_ioa_api: falconpy.CustomIOA):
    """Tests `CustomIoaApiModule.create_rule_group` on a group with zero rules"""
    # Setup
    group = IoaRuleGroup(
        name="test rule group",
        description="test description",
        platform="windows",
    )

    # Mock functions
    custom_ioa_api.create_rule_group.side_effect = create_mock_create_rule_group(
        assigned_id="test_rule_group")

    # Call caracara function
    new_group = client.custom_ioas.create_rule_group(
        group=group, comment="rule group creation test")

    # Assert falconpy called correctly
    custom_ioa_api.create_rule_group.assert_called_once_with(body={
        "name": "test rule group",
        "description": "test description",
        "platform": "windows",
        "comment": "rule group creation test",
    })
    # Assert returned group is as expected
    assert group.name == new_group.name
    assert group.description == new_group.description
    assert group.platform == new_group.platform
    assert new_group.exists_in_cloud()


def test_create_rule_group_with_rules(
        client: Client, custom_ioa_api: falconpy.CustomIOA, simple_rule_type: RuleType):
    """Tests `CustomIoaApiModule.create_rule_group` on a group with rules"""
    # Setup
    group = IoaRuleGroup(
        name="test rule group name",
        description="test rule group desc",
        platform="windows",
    )
    rule = CustomIoaRule(
        name="test rule name",
        description="test rule desc",
        severity=PatternSeverity.CRITICAL,
        rule_type=simple_rule_type,
    )
    rule.set_action("Test Action")
    group.add_rule(rule)

    # Mock functions
    custom_ioa_api.create_rule_group.side_effect = create_mock_create_rule_group(
        assigned_id="test_rule_group")
    custom_ioa_api.create_rule.side_effect = create_mock_create_rule(
        assigned_id="test_rule", rule_types=[simple_rule_type])
    custom_ioa_api.query_rule_types.side_effect = create_mock_query_resources(
        resources=[simple_rule_type.id_])
    custom_ioa_api.get_rule_types.side_effect = create_mock_get_rule_types(
        rule_types=[simple_rule_type])

    # Call caracara function
    new_group = client.custom_ioas.create_rule_group(
        group=group, comment="Rule group creation test")

    # Assert falconpy called correctly
    custom_ioa_api.create_rule_group.assert_called_once_with(body={
        "name": "test rule group name",
        "description": "test rule group desc",
        "platform": "windows",
        "comment": "Rule group creation test",
    })
    custom_ioa_api.create_rule.assert_called_once_with(
        body={
            "name": "test rule name",
            "description": "test rule desc",
            "disposition_id": 1,
            "field_values": [],
            "pattern_severity": PatternSeverity.CRITICAL,
            "rulegroup_id": "test_rule_group",
            "ruletype_id": "test_rule_type_simple",
            "comment": "Rule group creation test",
        },
    )
    # Assert returned group is as expected
    assert group.name == new_group.name
    assert group.description == new_group.description
    assert group.platform == new_group.platform
    assert new_group.exists_in_cloud()
    assert len(new_group.rules) == 1
    new_rule = new_group.rules[0]
    assert new_rule.name == rule.name
    assert new_rule.description == rule.description
    assert new_rule.severity == rule.severity
    assert new_rule.rule_type == rule.rule_type
    assert new_rule.disposition_id == rule.disposition_id
    assert new_rule.fields == rule.fields
    assert new_rule.exists_in_cloud()
