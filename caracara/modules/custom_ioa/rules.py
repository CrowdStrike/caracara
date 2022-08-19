from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from wsgiref import validate

from caracara.modules.custom_ioa.rule_types import RuleType

# TODO check these are actually correct


class PatternSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class IoaRuleGroup:
    """A class representing an IOA Rule Group.

    An IOA Rule Group stores Custom IOA Rules (represented by instances of `CustomIoaRule`), and can
    be assigned to any number of host groups.

    Note that IOA Rule Groups are versioned, and you can't push changes with <TODO: function here>
    if the local version does not match the current cloud version. If you run into this error you
    can update an instance of this class to match the state in the CrowdStrike cloud with <TODO: put
    function here>."""

    # API fields
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
    # end API fields

    def __init__(self, name: str, description: str, platform: str):
        """Return a completely built IOA Rule Group object.

        The object can be created blank, or populated based on a Falcon API response dictionary."""
        self.name = name
        self.description = description
        self.platform = platform
        self.rules = []

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(id_={repr(self.id_)}, version={repr(self.version)}, "
            f"name={repr(self.name)}, ...)>"
        )

    @staticmethod
    def from_data_dict(data_dict: dict, rule_types: Dict[str, RuleType]):
        rule_group = IoaRuleGroup(
            name=data_dict["name"],
            description=data_dict["description"],
            platform=data_dict["platform"]
        )

        rule_group.comment = data_dict["comment"]
        rule_group.committed_on = data_dict["committed_on"]
        rule_group.created_by = data_dict["created_by"]
        rule_group.created_on = data_dict["created_on"]
        rule_group.customer_id = data_dict["customer_id"]
        rule_group.deleted = data_dict["deleted"]
        rule_group.enabled = data_dict["enabled"]
        rule_group.id_ = data_dict["id"]
        rule_group.modified_by = data_dict["modified_by"]
        rule_group.modified_on = data_dict["modified_on"]
        rule_group.rule_ids = data_dict["rule_ids"]
        rule_group.version = data_dict["version"]

        for raw_rule in data_dict.get("rules", []):
            rule_type = rule_types.get(raw_rule.get("ruletype_id"))
            rule = CustomIoaRule.from_data_dict(data_dict=raw_rule, rule_type=rule_type)
            rule.rulegroup_id = rule_group.id_  # API doesn't seem to populate this field so we will
            rule_group.rules.append(rule)

        return rule_group

    def validation(self):  # TODO consider separate validation for create / update
        for rule in self.rules:
            rule.validation()

    def exists_in_cloud(self) -> bool:
        return self.id_ is not None

    def dump_create(self, comment: str, verify: bool = True):
        if verify and self.exists_in_cloud():
            raise Exception("This group already exists in the cloud!")

        return {
            "name": self.name,
            "description": self.description,
            "platform": self.platform,
            "comment": comment,
        }

    def dump_update(self, comment: str, verify: bool = True):
        if verify and not self.exists_in_cloud():
            raise Exception("This group does not exist in the cloud!")

        return {
            "id": self.id_,
            "rulegroup_version": self.version,
            "name": self.name,
            "description": self.description,
            "platform": self.platform,
            "enabled": self.enabled,
            "comment": comment,
        }

    def dump_rules_update(self, comment: str):
        return {
            "comment": comment,
            "rule_updates": [rule.dump_update(group=self) for rule in self.rules],
            "rulegroup_version": self.version + 1,
            "rulegroup_id": self.id_,
        }


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

    action_label: str
    comment: str
    committed_on: datetime
    created_by: str
    created_on: datetime
    customer_id: str
    deleted: bool
    description: str
    disposition_id: str
    enabled: bool
    instance_id: str = None
    instance_version: int
    magic_cookie: int
    modified_by: str
    modified_on: datetime
    name: str
    version_ids: List[str]

    severity: PatternSeverity
    rule_type: RuleType
    fields: Dict[(str, str), dict]  # (name, type) -> raw dict

    def __init__(
        self,
        name: str,
        description: str,
        severity: PatternSeverity,
        rule_type: RuleType,
    ):
        """Return a completely built Custom IOA Rule object.

        The object can be created blank, or populated based on a Falcon API response dictionary."""

        self.name = name
        self.description = description
        self.severity = severity
        self.rule_type = rule_type

        self.fields = {}
        for field_type in self.rule_type.fields:
            field = field_type.to_concrete_field()
            self.fields[(field["name"], field["type"])] = field

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(rulegroup_id={repr(self.rulegroup_id)}, "
            f"instance_id={repr(self.instance_id)}, instance_version={repr(self.instance_version)} "
            f"name={repr(self.name)}, ruletype={repr(self.rule_type)}, ...)>"
        )

    @staticmethod
    def from_data_dict(data_dict: dict, rule_type: RuleType):
        # note that this won't account for group
        rule = CustomIoaRule(
            name=data_dict["name"],
            description=data_dict["description"],
            severity=data_dict.get("pattern_severity"),
            rule_type=rule_type,
        )

        rule.action_label = data_dict["action_label"]
        rule.committed_on = data_dict["committed_on"]
        rule.created_by = data_dict["created_by"]
        rule.created_on = data_dict["created_on"]
        rule.customer_id = data_dict["customer_id"]
        rule.deleted = data_dict["deleted"]
        rule.description = data_dict["description"]
        rule.disposition_id = data_dict["disposition_id"]
        rule.enabled = data_dict["enabled"]
        rule.instance_id = data_dict["instance_id"]
        rule.instance_version = data_dict["instance_version"]
        rule.magic_cookie = data_dict["magic_cookie"]
        rule.modified_by = data_dict["modified_by"]
        rule.modified_on = data_dict["modified_on"]
        rule.version_ids = data_dict["version_ids"]

        rule.fields = {}
        for field_value in data_dict["field_values"]:
            rule.fields[(field_value["name"], field_value["type"])] = field_value

        return rule

    def validation(self):
        # Check an action / disposition has been set
        if not hasattr(self, "disposition_id"):
            raise Exception("Rule has no action, make sure to set one with the set_action method")

        # Check that at least one excludable field is non-default
        if all(
            all(value["value"] == ".*" for value in field["values"])
            for field in self.fields.values()
            if field["type"] == "excludable"
        ):
            raise Exception(
                "All excludable/regex fields set to the default of '.*' which the API will reject, "
                "set one to something else with the set_excludable_field method"
            )

    def exists_in_cloud(self) -> bool:
        return self.instance_id is not None

    def get_possible_actions(self):
        return list(self.rule_type.disposition_map.values())

    def set_action(self, action: str or int):
        if isinstance(action, int):
            if action in self.rule_type.disposition_map.keys():
                self.disposition_id = action
                self.action_label = self.rule_type.disposition_map[action]
            else:
                raise Exception("Invalid action/disposition id!")
        else:
            matches = [id_ for (id_, label)
                       in self.rule_type.disposition_map.items() if label == action]
            if len(matches) > 0:
                self.disposition_id = matches[0]
                self.action_label = action
            else:
                raise Exception("Invalid action/disposition label!")

    def set_excludable_field(self, name_or_label: str, include: str, exclude: Optional[str] = None):
        field = self.rule_type.get_field(name_or_label, "excludable")

        if field is None:
            raise Exception(
                f"Rule type {repr(self.rule_type.name)} has no fields with name or label "
                f"{repr(name_or_label)} and type \"excludable\""
            )

        values = [{
            "label": "include",
            "value": include,
        }]

        if exclude is not None:
            values.append({
                "label": "exclude",
                "value": exclude
            })

        self.fields[(field.name, "excludable")] = {
            "name": field.name,
            "label": field.label,
            "type": field.type,
            "values": values,
        }

    def get_set_field_options(self, name_or_label: str):
        field = self.rule_type.get_field(name_or_label, "set")
        return [option.value for option in field.options]

    def set_set_field(self, name_or_label: str, selected_options: str):
        field = self.rule_type.get_field(name_or_label, "set")

        if field is None:
            raise Exception(
                f"Rule type {repr(self.rule_type.name)} has no fields with name or label "
                f"{repr(name_or_label)} and type \"excludable\""
            )

        values = []
        for value in selected_options:
            # Find all options that have 'label' or 'value' matching the selected option
            matching_options = [option for option in field.options if value in
                                [option.label, option.value]]

            if len(matching_options) == 0:
                raise Exception(
                    f"No option matching {repr(value)} in field {repr(field.name)} in rule with "
                    f"type \"set\""
                )

            option = matching_options[0]
            values.append(option.dump())

        self.fields[(field.name, "set")] = {
            "name": field.name,
            "label": field.label,
            "type": field.type,
            "values": values,
        }

    def dump_update(self, group: IoaRuleGroup, verify: bool = True):
        if verify:
            if not self.exists_in_cloud():
                raise Exception("Can't update a rule that hasn't been created in the cloud")
            self.validation()

        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "instance_id": self.instance_id,
            "pattern_severity": self.severity,
            "disposition_id": self.disposition_id,
            "field_values": list(self.fields.values()),
        }

    def dump_create(self, comment: str, group: IoaRuleGroup, verify: bool = True):
        if verify:
            if self.exists_in_cloud():
                raise Exception("This rule already exists in the cloud!")
            self.validation()

        return {
            "name": self.name,
            "description": self.description,
            "pattern_severity": self.severity,
            "disposition_id": self.disposition_id,
            "field_values": list(self.fields.values()),
            "rulegroup_id": group.id_,
            "ruletype_id": self.rule_type.id_,
            "comment": comment,
        }
