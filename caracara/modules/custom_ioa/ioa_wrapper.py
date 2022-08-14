"""Caracara wrapper for IOA API models"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List


class IoaRuleGroup:
    """A class representing an IOA Rule Group.

    An IOA Rule Group stores Custom IOA Rules (represented by instances of `CustomIoaRule`), and can
    be assigned to any number of host groups.

    Note that IOA Rule Groups are versioned, and you can't push changes with <TODO: function here>
    if the local version does not match the current cloud version. If you run into this error you
    can update an instance of this class to match the state in the CrowdStrike cloud with <TODO: put
    function here>."""
    comment: str = None
    committed_on: datetime = None
    created_by: str = None
    created_on: datetime = None
    customer_id: str = None
    deleted: bool = None
    description: str = None
    enabled: str = None
    id_: str = None
    modified_by: str = None
    modified_on: datetime = None
    name: str = None
    platform: str = None
    rule_ids: List[str] = None
    rules: List[CustomIoaRule] = None
    version: int = None

    def __init__(self, data_dict: Dict = None):
        """Return a completely built IOA Rule Group object.

        The object can be created blank, or populated based on a Falcon API response dictionary."""

        if data_dict is not None:
            self._load_data_dict(data_dict=data_dict)

    def _load_data_dict(self, data_dict: Dict = None):
        """Load an IOA Rule Group dictionary from Falcon and set up the object accordingly."""
        self.comment = data_dict.get("comment")
        self.committed_on = data_dict.get("committed_on")
        self.created_by = data_dict.get("created_by")
        self.created_on = data_dict.get("created_on")
        self.customer_id = data_dict.get("customer_id")
        self.deleted = data_dict.get("deleted")
        self.description = data_dict.get("description")
        self.enabled = data_dict.get("enabled")
        self.id_ = data_dict.get("id")
        self.modified_by = data_dict.get("modified_by")
        self.modified_on = data_dict.get("modified_on")
        self.name = data_dict.get("name")
        self.platform = data_dict.get("platform")
        self.rule_ids = data_dict.get("rule_ids")
        self.version = data_dict.get("version")

        self.rules = []
        for rule_dict in data_dict.get("rules", []):
            self.rules.append(CustomIoaRule(group=self, data_dict=rule_dict))

    def dump(self) -> Dict:
        """Return a dictionary representing a full IOA Rule Group

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API if this IOA Rule Group
        already happened to exist in the Cloud."""
        dumped = {
            "comment": self.comment,
            "committed_on": self.committed_on,
            "created_by": self.created_by,
            "created_on": self.created_on,
            "customer_id": self.customer_id,
            "deleted": self.deleted,
            "description": self.description,
            "enabled": self.enabled,
            "id": self.id_,
            "modified_by": self.modified_by,
            "modified_on": self.modified_on,
            "name": self.name,
            "platform": self.platform,
            "rule_ids": self.rule_ids,
            "version": self.version,
            "rules": []
        }

        for rule in self.rules:
            dumped["rules"].append(rule.dump())

    def flat_dump(self, mode: str = 'auto') -> Dict:
        """Return a stripped down dictionary representing a full IOA Rule Group.

        This dictionary is designed for use with CrowdStrike API verbs (i.e., creation (POST) and
        modification (PATCH), and therefore is limited only to the content required to execute these
        actions).

        Mode can be one of ['auto', 'create', 'update'] (default: 'auto'):
        - 'auto':   Will attempt to automatically choose 'create' or 'update' based on whether this
                    object has an id (i.e. `self.id_` is not `None`).
        - 'create': Will return in a format that can passed to the appropriate CrowdStrike API
                    endpoint to create a new rule group.
        - 'update': Will return in a format that can be passed to the appropriate CrowdStrike API
                    endpoint to update an existing rule group"""
        if mode not in ['auto', 'create', 'update']:
            raise ValueError("'mode' argument must be one of ['auto', 'create', 'update']")

        if mode == 'auto':
            if self.id_ is None:
                mode = 'create'
            else:
                mode = 'update'

        dumped = {
            "comment": self.comment,
            "description": self.description,
            "name": self.name,
            "platform": self.platform,
        }

        if mode == 'update':
            dumped["id"] = self.id_
            dumped["rulegroup_version"] = self.version


class CustomIoaRule:
    """A class representing a Custom IOA Rule.

    A Custom IOA Rule is associated with a single IOA Rule Group (represented by instances of
    `IoaRuleGroup`). So a Custom IOA Rule is uniquely identified by a combination of it's own ID and
    its group ID.

    TODO: put more info about how to make rules

    Note that Custom IOA Rule are versioned, and you can't push changes with <TODO: function here>
    if the local version does not match the current cloud version. If you run into this error you
    can update an instance of this class to match the state in the CrowdStrike cloud with <TODO: put
    function here>."""
    action_label: str = None
    comment: str = None
    committed_on: datetime = None
    created_by: str = None
    created_on: datetime = None
    customer_id: str = None
    deleted: bool = None
    description: str = None
    disposition_id: str = None
    enabled: bool = None
    field_values: List[Dict]
    instance_id: str = None
    instance_version: int = None
    magic_cookie: int = None
    modified_by: str = None
    modified_on: datetime = None
    name: str = None
    pattern_id: str = None
    pattern_severity: str = None
    rulegroup_id: str = None
    ruletype_id: str = None
    ruletype_name: str = None
    version_ids: str = List[None]

    # CustomIoaRule is a weak entity, i.e. it depends on an IoaRuleGroup to exist
    group: IoaRuleGroup = None

    def __init__(self, group: IoaRuleGroup, data_dict: Dict = None):
        """Return a completely built Custom IOA Rule object.

        The object can be created blank, or populated based on a Falcon API response dictionary."""
        self.group = group

        if data_dict is not None:
            self._load_data_dict(data_dict=data_dict)

    def _load_data_dict(self, data_dict: Dict = None):
        """Load an Custom IOA Rule dictionary from Falcon and set up the object accordingly."""
        self.action_label = data_dict.get("action_label")
        self.comment = data_dict.get("comment")
        self.committed_on = data_dict.get("committed_on")
        self.created_by = data_dict.get("created_by")
        self.created_on = data_dict.get("created_on")
        self.customer_id = data_dict.get("customer_id")
        self.deleted = data_dict.get("deleted")
        self.description = data_dict.get("description")
        self.disposition_id = data_dict.get("disposition_id")
        self.enabled = data_dict.get("enabled")
        self.field_values = data_dict.get("field_value")
        self.instance_id = data_dict.get("instance_id")
        self.instance_version = data_dict.get("instance_version")
        self.magic_cookie = data_dict.get("magic_cookie")
        self.modified_by = data_dict.get("modified_by")
        self.modified_on = data_dict.get("modified_on")
        self.name = data_dict.get("name")
        self.pattern_id = data_dict.get("pattern_id")
        self.pattern_severity = data_dict.get("pattern_severity")
        self.rulegroup_id = data_dict.get("rulegroup_id")
        self.ruletype_id = data_dict.get("ruletype_id")
        self.ruletype_name = data_dict.get("ruletype_name")
        self.version_ids = data_dict.get("version_ids")

    def dump(self) -> Dict:
        """Return a dictionary representing a full Custom IOA Rule.

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API if this Custom IOA Rule
        already happened to exist in the Cloud."""
        return {
            "action_label": self.action_label,
            "comment": self.comment,
            "committed_on": self.committed_on,
            "created_by": self.created_by,
            "created_on": self.created_on,
            "customer_id": self.customer_id,
            "deleted": self.deleted,
            "description": self.description,
            "disposition_id": self.disposition_id,
            "enabled": self.enabled,
            "field_values": self.field_values,
            "instance_id": self.instance_id,
            "instance_version": self.instance_version,
            "magic_cookie": self.magic_cookie,
            "modified_by": self.modified_by,
            "modified_on": self.modified_on,
            "name": self.name,
            "pattern_id": self.pattern_id,
            "pattern_severity": self.pattern_severity,
            "rulegroup_id": self.rulegroup_id,
            "ruletype_id": self.ruletype_id,
            "ruletype_name": self.ruletype_name,
            "version_ids": self.version_ids,
        }

    def flat_dump(self, mode: str = 'auto') -> Dict:
        """Return a stripped down dictionary representing a full Custom IOA Rule.

        This dictionary is designed for use with CrowdStrike API verbs (i.e., creation (POST) and
        modification (PATCH), and therefore is limited only to the content required to execute these
        actions).

        Mode can be one of ['auto', 'create', 'update'] (default: 'auto'):
        - 'auto':   Will attempt to automatically choose 'create' or 'update' based on whether this
                    object has an id (i.e. `self.id_` is not `None`).
        - 'create': Will return in a format that can passed to the appropriate CrowdStrike API
                    endpoint to create a Custom IOA Rule.
        - 'update': Will return in a format that can be passed to the appropriate CrowdStrike API
                    endpoint to update an existing Custom IOA Rule"""
        if mode not in ['auto', 'create', 'update']:
            raise ValueError("'mode' argument must be one of ['auto', 'create', 'update']")

        if mode == 'auto':
            if self.instance_id is None:
                mode = 'create'
            else:
                mode = 'update'

        if mode == 'create':
            dumped = {
                "comment": self.comment,
                "description": self.description,
                "disposition_id": self.disposition_id,
                "field_values": self.field_values,
                "name": self.name,
                "pattern_severity": self.pattern_severity,
                "rulegroup_id": self.rulegroup_id,
                "ruletype_id": self.ruletype_id,
            }
        elif mode == 'update':
            dumped = {
                "description": self.description,
                "disposition_id": self.disposition_id,
                "enabled": self.enabled,
                "field_values": self.field_values,
                "instance_id": self.instance_id,
                "name": self.name,
                "pattern_severity": self.pattern_severity,
                "rulegroup_version": self.group.id_,
            }

        return dumped
