"""Caracara wrapper for Policies API.

This file contains wrapper classes that can represent policies in a generic way.
It is to be extended by the respective modules (response_policies, prevention_policies, etc.)
"""
# Disable TODO warning, to be removed when a wrapper is implemented for `ioa_rule_groups`
# pylint: disable=W0511
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List


class PolicySetting(ABC):
    """Generic policy setting class.

    Contains a list of settings and settings groups. This is recursive, as Falcon allows
    nested policy settings.
    """

    def __init__(self, data_dict: Dict = None):
        """Initialise a policy setting from a Falcon dictionary."""
        self.name: str = None

        if data_dict:
            self._load_data_dict(data_dict)

    def _load_data_dict(self, data_dict: Dict):
        self.name = data_dict.get("name")

    @abstractmethod
    def dump(self) -> Dict:
        """Return a dictionary encompassing all Policy object content.

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API.
        """

    @abstractmethod
    def flat_dump(self) -> Dict:
        """Return a stripped down dictionary representing all settings and their values.

        This dictionary is designed for use with CrowdStrike API policy verbs (i.e., policy
        creation (POST) and modification (PATCH), and therefore is limited only to the content
        required to execute these actions.
        """


class GroupAssignment(PolicySetting):
    """Represents an assignment rule that maps a policy to a host group."""

    def __init__(self, data_dict: Dict = None):
        """Configure a new Group Assignment object."""
        self.assignment_rule: str = None
        self.created_by: str = None
        self.created_timestamp: datetime = None
        self.description: str = None
        self.group_id: str = None
        self.group_type: str = None
        self.modified_by: str = None
        self.modified_timestamp: datetime = None

        super().__init__(data_dict)

    def _load_data_dict(self, data_dict: Dict):
        self.assignment_rule = data_dict.get("assignment_rule")
        self.created_by = data_dict.get("created_by")
        self.created_timestamp = data_dict.get("created_timestamp")
        self.description = data_dict.get("description")
        self.group_id = data_dict.get("id")
        self.group_type = data_dict.get("group_type")
        self.modified_by = data_dict.get("modified_by")
        self.modified_timestamp = data_dict.get("modified_timestamp")

        super()._load_data_dict(data_dict)

    def dump(self) -> Dict:
        """Return a dictionary representing a group assignment.

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API.
        """
        return {
            "assignment_rule": self.assignment_rule,
            "created_by": self.created_by,
            "created_timestamp": self.created_timestamp,
            "description": self.description,
            "group_type": self.group_type,
            "id": self.group_id,
            "modified_by": self.modified_by,
            "modified_timestamp": self.modified_timestamp,
            "name": self.name,
        }

    def flat_dump(self) -> Dict:
        """Return a stripped down dictionary representing a group assignment.

        This dictionary is designed for use with CrowdStrike API policy verbs (i.e., policy
        creation (POST) and modification (PATCH), and therefore is limited only to the content
        required to execute these actions.
        """
        return {
            "assignment_rule": self.assignment_rule,
            "description": self.description,
            "group_type": self.group_type,
            "id": self.group_id,
            "name": self.name,
        }


class ChangeablePolicySetting(PolicySetting, ABC):
    """Policy setting with an attribbute that can be changed.

    The actual type of setting must be derived from this (e.g., a toggle setting).
    """

    def __init__(self, data_dict: Dict = None):
        """Configure a new Changeable Policy Setting.

        This constructor only handles parameters that are available in all policy settings.
        Individual policy settings (such as toggles and sliders) have their own additional
        settings to store the values that are passed to and from the API.
        """
        self.description: str = None
        self.name: str = None
        self.setting_id: str = None

        super().__init__(data_dict)

    @property
    @abstractmethod
    def setting_type(self) -> str:
        """Store the type of setting.

        Examples: toggle, mlslider.
        """

    @abstractmethod
    def _dump_value(self) -> Dict[str, str]:
        """Generate the setting type-specific value dictionary."""

    def _load_data_dict(self, data_dict: Dict):
        super()._load_data_dict(data_dict)

        self.description = data_dict.get("description")
        self.setting_id = data_dict.get("id")
        self.setting_type = data_dict.get("type")

    def dump(self) -> Dict:
        """Return a dictionary representing a policy setting.

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API if this policy
        already happened to exist in the Cloud.
        """
        return {
            "description": self.description,
            "id": self.setting_id,
            "name": self.name,
            "type": self.setting_type,
            "value": self._dump_value(),
        }

    def flat_dump(self) -> Dict:
        """Return a stripped down dictionary representing a policy setting.

        This dictionary is designed for use with CrowdStrike API policy verbs (i.e., policy
        creation (POST) and modification (PATCH), and therefore is limited only to the content
        required to execute these actions.
        """
        return {
            "id": self.setting_id,
            "value": self._dump_value(),
        }


class TogglePolicySetting(ChangeablePolicySetting):
    """Toggle policy setting that has two options: enabled and disabled."""

    setting_type = "toggle"

    def __init__(self, data_dict: Dict = None):
        """Configure a new Toggle.

        We default this to None so that no position is ever assumed.
        """
        self.enabled: bool = None

        super().__init__(data_dict)

    def _dump_value(self) -> Dict[str, str]:
        return {
            "enabled": self.enabled,
        }

    def _load_data_dict(self, data_dict: Dict):
        super()._load_data_dict(data_dict)

        value_dict = data_dict.get("value")
        self.enabled = value_dict.get("enabled")


class MLSliderPolicySetting(ChangeablePolicySetting):
    """Machine Learning (ML) policy setting.

    Each ML slider has string values for detection and prevention.
    """

    setting_type = "mlslider"

    def __init__(self, data_dict: Dict = None):
        """Configure a new ML Slider.

        We initially set detection and prevention to None so that no assumption is made
        about the protection levels stored by the Cloud or desired by a user.
        """
        self.detection: str = None
        self.prevention: str = None

        super().__init__(data_dict)

    def _dump_value(self) -> Dict[str, str]:
        return {
            "detection": self.detection,
            "prevention": self.prevention,
        }

    def _load_data_dict(self, data_dict: Dict):
        super()._load_data_dict(data_dict)

        value_dict: Dict = data_dict.get("value")
        self.detection = value_dict.get("detection")
        self.prevention = value_dict.get("prevention")


SETTINGS_TYPE_MAP = {
    "mlslider": MLSliderPolicySetting,
    "toggle": TogglePolicySetting,
}


class PolicySettingGroup(PolicySetting):
    """Policy setting with a list of other settings within it."""

    def __init__(self, data_dict: Dict = None):
        """Return a new policy settings group, optionally configured via a dictionary."""
        self.settings: List[PolicySetting] = []

        super().__init__(data_dict)

    def _load_data_dict(self, data_dict: Dict):
        super()._load_data_dict(data_dict)

        inner_settings: List[Dict] = data_dict.get("settings", [])
        for inner_setting_dict in inner_settings:
            setting_template_name = inner_setting_dict.get("type")
            if setting_template_name in SETTINGS_TYPE_MAP:
                setting_template = SETTINGS_TYPE_MAP[setting_template_name]
                self.settings.append(setting_template(data_dict=inner_setting_dict))
            else:
                raise Exception(f"Setting type {setting_template_name} is not yet supported")

    def dump(self) -> Dict:
        """Return a dictionary representing a policy settings group.

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API if this policy
        already happened to exist in the Cloud.
        """
        return {
            "name": self.name,
            "settings": [x.dump() for x in self.settings],
        }

    def flat_dump(self) -> Dict:
        """Return a stripped down dictionary representing a policy settings group.

        This dictionary is designed for use with CrowdStrike API policy verbs (i.e., policy
        creation (POST) and modification (PATCH), and therefore is limited only to the content
        required to execute these actions.
        """
        return {
            "settings": [x.flat_dump() for x in self.settings],
        }


class Policy:
    """A generic policy class.

    Each policy object is comprised of one or more policy settings groups. These groups in turn
    contain individual policy settings that correspond to settings available within the Falcon
    Console. Each group of settings is handled by a PolicySettingGroup object.

    Each policy can be assigned to one or more groups. Each group assignment is handled by a
    GroupAssignent object.
    """

    def __init__(self, data_dict: Dict = None, style: str = "response"):
        """Return a completely built Policy object.

        The object can be created blank, or populated based on a Falcon API response dictionary.
        """
        # Configure the general settings that every policy will contain
        self.cid: str = None
        self.created_by: str = None
        self.created_timestamp: datetime = None
        self.description: str = None
        self.enabled: bool = None
        self.groups: List[GroupAssignment] = None
        self.modified_by: str = None
        self.modified_timestamp: str = None
        self.name: str = None
        self.platform_name: str = None
        self.policy_id: str = None
        self.settings_groups: List[PolicySettingGroup] = None
        self.settings_key_name = "settings"

        # TODO: Replace with a proper wrapper around ioa_rule_groups, this is temporary so that this
        #       result is still reachable from the 'dump' method when style="prevention".
        self._raw_ioa_rule_groups: List[Dict[str, Any]] = None

        # Set lists up here to ensure we do not pass references around when multiple Policy classes
        # are instantiated
        self.groups = []
        self.settings_groups = []

        # Customise the object so that it stores data appropriately based on the type of
        # policy that it will represent.
        if style == "response":
            self.settings_key_name = "settings"
        elif style == "prevention":
            self.prevention_settings = self.settings_groups
            self.settings_key_name = "prevention_settings"
        else:
            raise ValueError(f"The style provided ({style}) is not valid")

        self.style = style

        if data_dict:
            self._load_data_dict(data_dict=data_dict)

    def _load_data_dict(self, data_dict: Dict = None):
        """Load a policy dictionary from Falcon and set up the object accordingly."""
        self.cid = data_dict.get("cid")
        self.created_by = data_dict.get("created_by")
        self.created_timestamp = data_dict.get("created_timestamp")
        self.description = data_dict.get("description")
        self.enabled = data_dict.get("enabled")
        self.policy_id = data_dict.get("id")
        self.modified_by = data_dict.get("modified_by")
        self.modified_timestamp = data_dict.get("modified_timestamp")
        self.name = data_dict.get("name")
        self.platform_name = data_dict.get("platform_name")
        self._raw_ioa_rule_groups = data_dict.get("ioa_rule_groups")  # TODO: see earlier TODO

        # Load all groups as GroupAssignment objects
        groups: List[Dict] = data_dict.get("groups", [])
        for group_dict in groups:
            self.groups.append(GroupAssignment(data_dict=group_dict))

        # Load all groups of settings
        settings_groups: List[Dict] = data_dict.get(self.settings_key_name)
        for settings_group_dict in settings_groups:
            self.settings_groups.append(PolicySettingGroup(data_dict=settings_group_dict))

    def dump(self) -> Dict:
        """Return a dictionary representing a full policy.

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API if this policy
        already happened to exist in the Cloud.
        """
        dumped = {
            "cid": self.cid,
            "created_by": self.created_by,
            "created_timestamp": self.created_timestamp,
            "description": self.description,
            "enabled": self.enabled,
            "groups": [x.dump() for x in self.groups],
            "id": self.policy_id,
            "modified_by": self.modified_by,
            "modified_timestamp": self.modified_timestamp,
            "name": self.name,
            "platform_name": self.platform_name,
            self.settings_key_name: [x.dump() for x in self.settings_groups],
        }

        if self.style == "prevention":
            dumped["ioa_rule_groups"] = self._raw_ioa_rule_groups  # TODO: see earlier TODO

        return dumped

    def flat_dump(self) -> Dict:
        """Return a stripped down dictionary representing a full policy.

        This dictionary is designed for use with CrowdStrike API policy verbs (i.e., policy
        creation (POST) and modification (PATCH), and therefore is limited only to the content
        required to execute these actions.
        """
        settings: List[Dict] = []
        for settings_group in self.settings_groups:
            settings.extend(settings_group.flat_dump()['settings'])

        data = {
            "description": self.description,
            "name": self.name,
            "platform_name": self.platform_name,
            self.settings_key_name: settings,
        }
        if self.policy_id:
            data['id'] = self.policy_id

        return data
