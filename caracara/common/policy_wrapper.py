"""
Caracara wrapper for Policies API.

This file contains wrapper classes that can represent policies in a generic way.
It is to be extended by the respective modules (response_policies, prevention_policies, etc.)
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List


class PolicySetting(ABC):
    """
    Generic policy setting class.

    Contains a list of settings and settings groups. This is recursive, as Falcon allows
    nested policy settings.
    """

    name: str = None

    def __init__(self, data_dict: Dict = None):
        """Initialise a policy setting from a Falcon dictionary."""
        if data_dict:
            self._load_data_dict(data_dict)

    @abstractmethod
    def _load_data_dict(self, data_dict: Dict):
        self.name = data_dict.get("name")

    @abstractmethod
    def dump(self) -> Dict:
        """
        Return a dictionary encompassing all Policy object content.

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API.
        """

    @abstractmethod
    def flat_dump(self) -> Dict:
        """
        Return a stripped down dictionary representing all settings and their values.

        This dictionary is designed for use with CrowdStrike API policy verbs (i.e., policy
        creation (POST) and modification (PATCH), and therefore is limited only to the content
        required to execute these actions.
        """


class GroupAssignment(PolicySetting):
    """Represents an assignment rule that maps a policy to a host group."""

    def _load_data_dict(self, data_dict: Dict):
        super()._load_data_dict(data_dict)

        self.assignment_rule: str = data_dict.get("assignment_rule")
        self.created_by: str = data_dict.get("created_by")
        self.created_timestamp: datetime = data_dict.get("created_timestamp")
        self.description: str = data_dict.get("description")
        self.group_id: str = data_dict.get("id")
        self.group_type: str = data_dict.get("group_type")
        self.modified_by: str = data_dict.get("modified_by")
        self.modified_timestamp: str = data_dict.get("modified_timestamp")

    def dump(self) -> Dict:
        """
        Return a dictionary representing a group assignment.

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
        """
        Return a stripped down dictionary representing a group assignment.

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
    """
    Policy setting with an attribbute that can be changed.

    The actual type of setting must be derived from this (e.g., a toggle setting).
    """

    description: str = None
    name: str = None
    setting_id: str = None
    setting_type: str = None

    @property
    @abstractmethod
    def setting_type(self) -> str:
        """
        Store the type of setting.

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
        """
        Return a dictionary representing a policy setting.

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
        """
        Return a stripped down dictionary representing a policy setting.

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

    enabled: bool = None
    setting_type: str = "toggle"

    def _dump_value(self) -> Dict[str, str]:
        return {
            "enabled": self.enabled,
        }

    def _load_data_dict(self, data_dict: Dict):
        super()._load_data_dict(data_dict)
        value_dict = data_dict.get("value")
        self.enabled = value_dict.get("enabled")


class MLSliderPolicySetting(ChangeablePolicySetting):
    """
    Machine Learning (ML) policy setting.

    Each ML slider has string values for detection and prevention.
    """

    detection: str = None
    prevention: str = None
    setting_type: str = "mlslider"

    def _dump_value(self) -> Dict[str, str]:
        return {
            "detection": self.detection,
            "prevention": self.prevention,
        }

    def _load_data_dict(self, data_dict: Dict):
        super()._load_data_dict(data_dict)
        value_dict = data_dict.get("value")
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
        # Configure settings as an instance variable to avoid passing the same list reference
        # around between different instances of this classs
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
        """
        Return a dictionary representing a policy settings group.

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API if this policy
        already happened to exist in the Cloud.
        """
        return {
            "name": self.name,
            "settings": [x.dump() for x in self.settings],
        }

    def flat_dump(self) -> Dict:
        """
        Return a stripped down dictionary representing a policy settings group.

        This dictionary is designed for use with CrowdStrike API policy verbs (i.e., policy
        creation (POST) and modification (PATCH), and therefore is limited only to the content
        required to execute these actions.
        """
        return {
            "settings": [x.flat_dump() for x in self.settings],
        }


class Policy:
    """
    A generic policy class.

    Each policy object is comprised of one or more policy settings groups. These groups in turn
    contain individual policy settings that correspond to settings available within the Falcon
    Console. Each group of settings is handled by a PolicySettingGroup object.

    Each policy can be assigned to one or more groups. Each group assignment is handled by a
    GroupAssignent object.
    """

    cid: str = None
    created_by: str = None
    created_timestamp: datetime = None
    description: str = None
    enabled: bool = None
    groups: List[GroupAssignment] = None
    modified_by: str = None
    modified_timestamp: str = None
    name: str = None
    platform_name: str = None
    policy_id: str = None
    settings_groups: List[PolicySettingGroup] = None
    settings_key_name = "settings"

    def __init__(self, data_dict: Dict = None, style: str = "response"):
        """
        Return a completely built Policy object.

        The object can be created blank, or populated based on a Falcon API response dictionary.
        """
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

        # Load all groups as GroupAssignment objects
        groups: List[Dict] = data_dict.get("groups", [])
        for group_dict in groups:
            self.groups.append(GroupAssignment(data_dict=group_dict))

        # Load all groups of settings
        settings_groups: List[Dict] = data_dict.get(self.settings_key_name)
        for settings_group_dict in settings_groups:
            self.settings_groups.append(PolicySettingGroup(data_dict=settings_group_dict))

    def dump(self) -> Dict:
        """
        Return a dictionary representing a full policy.

        This dictionary is compliant with the CrowdStrike API specification, and therefore
        can replicate the exact response sent back by the CrowdStrike API if this policy
        already happened to exist in the Cloud.
        """
        return {
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

    def flat_dump(self) -> Dict:
        """
        Return a stripped down dictionary representing a full policy.

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
