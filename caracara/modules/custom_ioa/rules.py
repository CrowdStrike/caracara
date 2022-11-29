"""Module that provides wrappers around IOA Rule Groups and Custom IOA Rules."""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional

from caracara.modules.custom_ioa.rule_types import RuleType


class IoaRuleGroup:
    """A class representing an IOA Rule Group.

    An IOA Rule Group stores Custom IOA Rules (represented by instances of `CustomIoaRule`), and can
    be assigned to any number of host groups.
    """

    # These fields should exist on all instances of this object
    name: str
    description: str
    platform: str
    rules: List[CustomIoaRule]
    rules_to_delete: List[CustomIoaRule]
    group: IoaRuleGroup

    # The fields below will only be populated if `exists_in_cloud()` returns `True`, with the
    # exception of `id` which should be initialised to `None` if this object does not exist on the
    # cloud
    id_: str
    comment: str
    committed_on: datetime
    created_by: str
    created_on: datetime
    customer_id: str
    deleted: bool
    enabled: str
    modified_by: str
    modified_on: datetime
    rule_ids: List[str]
    version: int

    def __init__(self, name: str, description: str, platform: str):
        """Create a new local IOA Rule Group.

        Rules can be added using the `add_rule` method, and this group can be created in the cloud
        using the `create_rule_group` request on the custom IOA module.

        Arguments
        ---------
        `name`: `str`
            The name of this rule group
        `description`: `str`
            The description of this rule group
        `platform`: `str`
            The platform that this rule group is for (typically `windows`, `linux` or `mac`)
        """
        self.name = name
        self.description = description
        self.platform = platform
        self.rules = []
        self.rules_to_delete = []
        self.group = None
        self.id_ = None

    def __repr__(self):
        """Return an unambiguous string representation of the IOA and its ID, platform and name."""
        return (
            f"<{self.__class__.__name__}(id_={repr(self.id_)}, version={repr(self.version)}, "
            f"platform={repr(self.platform)}, name={repr(self.name)}, ...)>"
        )

    @staticmethod
    def from_data_dict(data_dict: dict, rule_type_map: Dict[str, RuleType]) -> IoaRuleGroup:
        """Construct a rule group object from an instance of the `api.RuleGroupV1` API model.

        The API will return an api.RuleGroupV1 object. This function will parse the dictionary
        representation of this object and return an IoaRuleGroup. You must also provide a map
        of rule type IDs to their associated rule types.

        Arguments
        ---------
        `data_dict`: `dict`
            The data returned from the API conforming to `api.RuleGroupV1` in the Swagger doc
        `rule_type_map`: `Dict[str, RuleType]`
            A map from rule type ID to its corresponding rule type object

        Returns
        -------
        `IoaRuleGroup`: The resulting constructed group.
        """
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
            # The following line might raise an index error if there's a rule type on this rule that
            # we don't know about. I don't catch this since I don't think it's likely to happen.
            rule_type = rule_type_map[raw_rule["ruletype_id"]]
            raw_rule["rulegroup_id"] = rule_group.id_  # API doesn't populate this field, so we do
            rule = CustomIoaRule.from_data_dict(data_dict=raw_rule, rule_type=rule_type)
            rule_group.rules.append(rule)

        return rule_group

    def add_rule(self, rule: CustomIoaRule):
        """Add a rule to a group.

        The rule specified is queued up for creation upon the next `update_rule_group` request.
        This method will fail if the provided rule is already associated with another object.

        Arguments
        ---------
        `rule`: `CustomIoaRule`
            The rule to add to this rule group
        """
        if rule.group is not None:
            raise Exception(
                "This rule has already been added to a group!"
            )
        rule.group = self
        self.rules.append(rule)

    def remove_rule(self, index_of_rule: int):
        """Remove a rule from a group.

        The rule specified is queued up for deletion upon the next `update_rule_group` request.

        Arguments
        ---------
        `index_of_rule`: `int`
            Index of the rule to delete within the `rules` member.
        """
        if index_of_rule >= len(self.rules) or index_of_rule < 0:
            raise Exception("Index of rule out of range!")

        removed_rule = self.rules.pop(index_of_rule)
        if removed_rule.exists_in_cloud():
            self.rules_to_delete.append(removed_rule)

    def validation(self):
        """Validate each rule to catch some errors before sending to the API.

        If there is an error an exception will be raised.
        """
        for rule in self.rules:
            rule.validation()

    def exists_in_cloud(self) -> bool:
        """Return if this object reflects an existing rule group in the cloud."""
        return self.id_ is not None

    def dump(self) -> dict:
        """Dump this rule group in conformance with api.RuleGroupV1 object model.

        This object model is defined in the CrowdStrike API Swagger document.
        """
        if not self.exists_in_cloud():
            raise Exception("This group does not exist in the cloud!")
        return {
            "customer_id": self.customer_id,
            "id": self.id_,
            "name": self.name,
            "description": self.description,
            "platform": self.platform,
            "enabled": self.enabled,
            "deleted": self.deleted,
            "rule_ids": [rule.instance_id for rule in self.rules],
            "rules": [rule.dump() for rule in self.rules],
            "version": self.version,
            "committed_on": self.committed_on,
            "created_on": self.created_on,
            "created_by": self.created_by,
            "modified_on": self.modified_on,
            "modified_by": self.modified_by,
            "comment": self.comment,
        }

    def dump_create(self, comment: str, verify: bool = True) -> dict:
        """Dump this rule group in conformance with the api.RuleGroupCreateRequestV1 object model.

        This object model is defined in the CrowdStrike API Swagger document. This function will
        also verify that this group has not been already created when `verify=True`.

        Arguments
        ---------
        `comment`: `str`
            The comment to associated with the creation action
        `verify`: `bool`, optional (default=`True`)
            Whether this method should verify whether the object has been created or not

        Returns
        -------
        `dict`: A dictionary structured in conformance with the api.RuleGroupCreateRequestV1 model.
        """
        if verify and self.exists_in_cloud():
            raise Exception("This group already exists in the cloud!")

        return {
            "name": self.name,
            "description": self.description,
            "platform": self.platform,
            "comment": comment,
        }

    def dump_update(self, comment: str, verify: bool = True) -> dict:
        """Dump this rule group in conformance with the api.RuleGroupModifyRequestV1 model.

        This object model is defined in the CrowdStrike API Swagger document. This function will
        also verify that this group has already been already created (and so can be updated)
        when `verify=True`.

        Arguments
        ---------
        `comment`: `str`
            The comment to associated with the update action.
        `verify`: `bool`, optional (default=`True`)
            Whether this method should verify whether the object has not been created or not

        Returns
        -------
        `dict`: A dictionary structured in conformance with the api.RuleGroupModifyRequestV1 model.
        """
        if verify and not self.exists_in_cloud():
            raise Exception("This group does not exist in the cloud!")

        return {
            "id": self.id_,
            "rulegroup_version": self.version,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "comment": comment,
        }

    def dump_rules_update(self, comment: str) -> dict:
        """Dump the current rules in a format conforming to the api.RuleUpdatesRequestV1 model.

        This object model is defined in the CrowdStrike API Swagger document.

        Arguments
        ---------
        `comment`: `str`
            The comment to associated with the update action.

        Returns
        -------
        `dict`: A dictionary structured in conformance with the api.RuleUpdatesRequestV1 model.
        """
        return {
            "comment": comment,
            "rule_updates": [rule.dump_update(group=self) for rule in self.rules],
            "rulegroup_version": self.version + 1,
            "rulegroup_id": self.id_,
        }


class CustomIoaRule:
    """A class representing a Custom IOA Rule.

    A Custom IOA Rule is associated with a single IOA Rule Group (represented by instances of
    `IoaRuleGroup`). So, a Custom IOA Rule is uniquely identified by a combination of its own ID and
    its group ID.

    A rule can be created with a provided `RuleType`. Right now you must query the rule types using
    the `describe_rule_types` request on the custom IOA module, and pick the one you want. In the
    future, we may provide a quicker method.

    Every rule needs to have its action/disposition set using `set_action`.

    Additionally, if a rule has options for a regex (known as an 'excludable' field), this has an
    include and an optional exclude regex that can be provided. These parameters can be set using
    the `set_excludable_field` method.

    Sometimes the rule may have an option to select a number of checkboxes in a set of values (known
    as a 'set' field). The options for this field can be set with `set_set_field`.

    The easiest way to find out the action/field names and possible values is to look at their names
    and options on the CrowdStrike Falcon web interface.
    """

    # These fields should exist on all instances of this object
    name: str
    description: str
    severity: str
    rule_type: RuleType
    fields: Dict[(str, str), dict]  # (name, type) -> raw dict

    # This field should exist if this object has been added to a group
    group: IoaRuleGroup

    # All these fields should exist if `exists_in_cloud()` returns True, with the exception of
    # instance_id which should exist and initialised to `None` if this object does not exist in the
    # cloud
    instance_id: str
    action_label: str
    comment: str
    committed_on: datetime
    created_by: str
    created_on: datetime
    customer_id: str
    deleted: bool
    disposition_id: str
    enabled: bool
    instance_version: int
    magic_cookie: int
    modified_by: str
    modified_on: datetime
    version_ids: List[str]
    pattern_id: str

    def __init__(
        self,
        name: str,
        description: str,
        severity: str,
        rule_type: RuleType,
    ):
        """Construct a local rule object.

        This rule needs to be customised using the `set_*` methods (see the class docstring for more
        information). After that, it can be added to a rule group using the `add_rule` method on an
        `IoaRuleGroup` object, and created in the cloud by either creating that group if it doesn't
        exist (with `create_rule_group`), or updating it if it already exists (with
        `update_rule_group`)

        Arguments
        ---------
        `name`: `str`
            The name of this rule
        `description`: `str`
            The description of this rule
        `severity`: `str`
            The severity of this rule (typically `informational`, `low`, `medium`, `high` or
            `critical`)
        `rule_type`: `RuleType`
            The type of this rule.
        """
        self.name = name
        self.description = description
        self.severity = severity
        self.rule_type = rule_type
        self.group = None
        self.instance_id = None

        self.fields = {}
        for field_type in rule_type.fields:
            field = field_type.to_concrete_field()
            self.fields[(field["name"], field["type"])] = field

    def __repr__(self):
        """Return an unambiguous string representation of the CustomIoaRule and its properties.

        This function will display the rule's group, ID, version, name and type.
        """
        return (
            f"<{self.__class__.__name__}(group={repr(self.group)}, "
            f"instance_id={repr(self.instance_id)}, instance_version={repr(self.instance_version)} "
            f"name={repr(self.name)}, ruletype={repr(self.rule_type)}, ...)>"
        )

    @staticmethod
    def from_data_dict(data_dict: dict, rule_type: RuleType) -> CustomIoaRule:
        """Construct a rule object from an instance of the `api.RuleV1` object.

        This object will conform to the `api.RuleV1` object model defined by the CrowdStrike API
        Swagger document, and will be returned from the API. You must also provide the rule's type
        for this function to succeed.

        Arguments
        ---------
        `data_dict`: `dict`
            The data returned from the API conforming to `api.RuleV1` in the Swagger doc
        `rule_type`: `RuleType`
            The type of this rule.

        Returns
        -------
        `CustomIoaRule`: The resulting constructed rule.
        """
        # note that this won't account for group
        rule = CustomIoaRule(
            name=data_dict["name"],
            description=data_dict["description"],
            severity=data_dict["pattern_severity"],
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
        rule.pattern_id = data_dict["pattern_id"]
        rule.comment = data_dict["comment"]

        rule.fields = {}
        for field_value in data_dict["field_values"]:
            rule.fields[(field_value["name"], field_value["type"])] = field_value

        return rule

    def validation(self):
        """Validate the IoaRuleGroup to catch errors before sending data to the API.

        This function will raise an exception if there are any issues with the data within this
        object, and contextual information will be provided alongside each exception.
        """
        # Check an action / disposition has been set
        if not hasattr(self, "disposition_id"):
            raise Exception("Rule has no action, make sure to set one with the set_action method")

        # Check that at least one excludable field is non-default
        regex_values = [
            value["value"]
            for field in self.fields.values() if field["type"] == "excludable"
            for value in field["values"]
        ]
        if len(regex_values) > 0 and all(value == ".*" for value in regex_values):
            raise Exception(
                "All excludable/regex fields set to the default of '.*' which the API will reject, "
                "set one to something else with the set_excludable_field method"
            )

    def exists_in_cloud(self) -> bool:
        """Return `True` if this rule object reflects an existing rule in the cloud."""
        return self.instance_id is not None

    def get_possible_actions(self) -> List[str]:
        """Return a list of possible actions to set using the `set_action` method."""
        return list(self.rule_type.disposition_map.values())

    def set_action(self, action: str or int):
        """Set the action/disposition for this rule.

        An action must be set for the API to accept this rule.

        Arguments
        ---------
        `action`: `str` or `int`
            The label of the action to set to, or the disposition ID of the action.
        """
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
        """Set a field of type excludable with a matching name or label to the one provided.

        Fields of type 'excludable' concern regular expression matching. Each field has an include
        (defaulting to `.*`), and an optional exclude. At least one excludable field must be
        non-default for the API to accept this rule.

        Arguments
        ---------
        `name_or_label`: `str`
            The name or label of the field to set.
        `include`: `str`
            The include regex for this field.
        `exclude`: `Optional[str]`
            The exclude regex for this field (optional)
        """
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

    def get_set_field_options(self, name_or_label: str) -> List[str]:
        """Return the available options for a set field.

        Arguments
        ---------
        `name_or_label`: `str`
            The name or label of the set field to check the options of.
        """
        field = self.rule_type.get_field(name_or_label, "set")
        return [option.value for option in field.options]

    def set_set_field(self, name_or_label: str, selected_options: List[str]):
        """Set the options for a set field.

        A set field can be thought of as a list of checkboxes, where you can check a subset of a
        set of values. For a list of available options you cna use the `get_set_field_options`
        method. By default all options are checked.

        Arguments
        ---------
        `name_or_label`: `str`
            The name or label of the set field to set.
        `selected_options`: `List[str]`
            The list of the options selected for this field.
        """
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

    def dump(self) -> dict:
        """Dump this object in conformance with the api.RuleV1 model.

        This object model is defined in the CrowdStrike API Swagger document.
        """
        return {
            "customer_id": self.customer_id,
            "instance_id": self.instance_id,
            "name": self.name,
            "description": self.description,
            "pattern_id": self.pattern_id,
            "pattern_severity": self.severity,
            "disposition_id": self.disposition_id,
            "action_label": self.action_label,
            "ruletype_id": self.rule_type.id_,
            "ruletype_name": self.rule_type.name,
            "field_values": list(self.fields.values()),
            "enabled": self.enabled,
            "deleted": self.deleted,
            "instance_version": self.instance_version,
            "version_ids": self.version_ids,
            "magic_cookie": self.magic_cookie,
            "committed_on": self.committed_on,
            "created_on": self.created_on,
            "created_by": self.created_by,
            "modified_on": self.modified_on,
            "modified_by": self.modified_by,
            "comment": self.comment,
        }

    def dump_update(self, verify: bool = True) -> dict:
        """Dump this object in conformance with the api.RuleUpdateV1 model.

        This object model is defined in the CrowdStrike API Swagger document, excluding
        'rulegroup_version'. This function will check that this object reflects an existing
        (updatable) object in the cloud if verify=`True`.
        """
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

    def dump_create(self, comment: str, verify: bool = True) -> dict:
        """Dump this object in conformance with the `api.RuleCreateV1` model.

        This object model is defined in the CrowdStrike API Swagger document. The function will
        check that this object does not reflect an existing object in the cloud (and so can be
        safely created) if verify=`True`.
        """
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
            "rulegroup_id": self.group.id_,
            "ruletype_id": self.rule_type.id_,
            "comment": comment,
        }
