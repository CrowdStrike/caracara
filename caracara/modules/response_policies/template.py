"""
Caracara: Response Policies.

This file contains platform-specific templates representing standard, blank Response policies.
"""
from caracara.common.policy_wrapper import (
    ChangeablePolicySetting,
    Policy,
    PolicySettingGroup,
    SETTINGS_TYPE_MAP,
)


COMMAND_TEMPLATES = {
    "RealTimeFunctionality": {
        "description": (
            "Allow those with Real Time Responder roles to remotely connect to hosts. "
            "Required for all RTR commands and scripts and for partner software update policies."
        ),
        "name": "Real Time Response",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "CustomScripts": {
        "description": (
            "Allows those with RTR Active Responder and RTR Administrator roles to run custom "
            "scripts"
        ),
        "name": "Custom Scripts",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "GetCommand": {
        "description": "Extract files from a remote host via the CrowdStrike cloud",
        "name": "get",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "PutCommand": {
        "description": (
            "Send files to a remote host via the CrowdStrike cloud. Required for partner software "
            "update policies"
        ),
        "name": "put",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "MemDumpCommand": {
        "description": "Dump process memory of a remote host",
        "name": "memdump",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "XMemDumpCommand": {
        "description": "Dump the complete memory of a remote host",
        "name": "xmemdump",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "ExecCommand": {
        "description": "Run any executable on the remote host",
        "name": "run",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "PutAndRunCommand": {
        "description": (
            "Send files to a secure directory on a remote host via the CrowdStrike cloud "
            "and execute them with a single command"
        ),
        "name": "put-and-run",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
}

OPTION_PLATFORM_MAPPING = {
    "Linux": {
        "Enable/Disable": [
            "RealTimeFunctionality",
        ],
        "Custom scripts": [
            "CustomScripts"
        ],
        "High risk commands": [
            "GetCommand",
            "PutCommand",
            "ExecCommand",
        ],
    },
    "Mac": {
        "Enable/Disable": [
            "RealTimeFunctionality",
        ],
        "Custom scripts": [
            "CustomScripts"
        ],
        "High risk commands": [
            "GetCommand",
            "PutCommand",
            "ExecCommand",
            "PutAndRunCommand",
        ]
    },
    "Windows": {
        "Enable/Disable": [
            "RealTimeFunctionality",
        ],
        "Custom scripts": [
            "CustomScripts"
        ],
        "High risk commands": [
            "GetCommand",
            "PutCommand",
            "MemDumpCommand",
            "XMemDumpCommand",
            "ExecCommand",
            "PutAndRunCommand",
        ]
    },
}


def generate_response_template(platform_name: str) -> Policy:
    """
    Generate a blank response policy object.

    This policy contains all settings in their default disabled states, ready for
    user or developer modification.
    """
    if platform_name not in OPTION_PLATFORM_MAPPING:
        raise Exception(f"The platform name {platform_name} is not valid")

    policy = Policy(style="response")
    policy.name = "Example Response Policy"
    policy.description = "Response Policy generated from a template"
    policy.platform_name = platform_name

    for group_name, group_settings in OPTION_PLATFORM_MAPPING[platform_name].items():
        group = PolicySettingGroup()
        group.name = group_name

        for setting_id in group_settings:
            setting_data = COMMAND_TEMPLATES[setting_id]
            setting_type = setting_data['setting_type']
            setting_template: ChangeablePolicySetting = SETTINGS_TYPE_MAP[setting_type]
            loadable_setting_data = {
                **COMMAND_TEMPLATES[setting_id],
                "id": setting_id,
            }
            setting = setting_template(data_dict=loadable_setting_data)
            group.settings.append(setting)

        policy.settings_groups.append(group)

    return policy
