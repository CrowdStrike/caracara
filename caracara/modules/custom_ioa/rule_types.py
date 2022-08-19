from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RuleType:
    id_: str
    name: str
    long_desc: str
    platform: str
    disposition_map: Dict[int, str]
    fields: List[RuleTypeField]

    def __init__(self, data_dict: dict = {}):
        self._load_data_dict(data_dict=data_dict)

    def __repr__(self) -> str:
        return (
            f"<RuleType(id_={repr(self.id_)}, name={repr(self.name)}, "
            f"platform={repr(self.platform)}, ...)>"
        )

    def _load_data_dict(self, data_dict: dict):
        self.id_ = data_dict["id"]
        self.name = data_dict["name"]
        self.long_desc = data_dict["long_desc"]
        self.platform = data_dict["platform"]
        self.disposition_map = {}
        for mapping in data_dict["disposition_map"]:
            self.disposition_map[mapping["id"]] = mapping["label"]
        self.fields = []
        for raw_field in data_dict["fields"]:
            self.fields.append(RuleTypeField(data_dict=raw_field))

    def get_field(
        self, field_name_or_label: str, field_type: Optional[str] = None
    ) -> Optional[RuleTypeField]:
        for field in self.fields:
            if (field_name_or_label in [field.name, field.label]
                    and (field_type is None or field.type == field_type)):
                return field
        return None


@dataclass
class RuleTypeField:
    label: str
    name: str
    type: str
    options: List[RuleTypeFieldOption]

    def __init__(self, data_dict: dict = {}):
        self._load_data_dict(data_dict=data_dict)

    def _load_data_dict(self, data_dict: dict):
        self.label = data_dict["label"]
        self.name = data_dict["name"]
        self.type = data_dict["type"]
        self.options = []
        for raw_option in data_dict["options"]:
            self.options.append(RuleTypeFieldOption(data_dict=raw_option))

    def to_concrete_field(self):
        field = {
            "label": self.label,
            "name": self.name,
            "type": self.type,
        }

        if self.type == "excludable":
            field["values"] = [{"label": "include", "value": ".*"}]
        elif self.type == "set":
            field["values"] = [option.dump() for option in self.options]
        else:
            raise Exception(f"Unknown rule field type {repr(self.type)}")

        return field


@dataclass
class RuleTypeFieldOption:
    label: str
    value: str

    def __init__(self, data_dict: dict = {}):
        self._load_data_dict(data_dict=data_dict)

    def _load_data_dict(self, data_dict: dict):
        self.label = data_dict["label"]
        self.value = data_dict["value"]

    def dump(self):
        return {"label": self.label, "value": self.value}
