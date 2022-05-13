"""
Caracara: Prevention Policies.

This file contains platform-specific templates representing standard, blank Prevention policies.
"""
from caracara.common.policy_wrapper import (
    ChangeablePolicySetting,
    Policy,
    PolicySettingGroup,
    SETTINGS_TYPE_MAP,
)


COMMAND_TEMPLATES = {
    "AdditionalUserModeData":
    {
        "description": (
            "Allows the sensor to get more data from a user-mode component it loads into all "
            "eligible processes, which augments online machine learning and turns on additional "
            "detections. Recommend testing with critical applications before full deployment."
        ),
        "name": "Additional User Mode Data",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "AdwarePUP": {
        "description": (
            "Use cloud-based machine learning informed by global analysis of executables to "
            "detect and prevent adware and potentially unwanted programs (PUP) for your online "
            "hosts."
        ),
        "name": "Adware & PUP",
        "setting_type": "mlslider",
        "value": {
            "detection": "DISABLED",
            "prevention": "DISABLED",
        },
    },
    "ApplicationExploitationActivity": {
        "description": (
            "Creation of a process, such as a command prompt, from an exploited browser or "
            "browser flash plugin was blocked."
        ),
        "name": "Application Exploitation Activity",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "BackupDeletion": {
        "description": "Deletion of backups often indicative of ransomware activity.",
        "name": "Backup Deletion",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "ChopperWebshell": {
        "description": (
            "Execution of a command shell was blocked and is indicative of the system "
            "hosting a Chopper web page."
        ),
        "name": "Chopper Webshell",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "CloudAntiMalware": {
        "description": (
            "Use cloud-based machine learning informed by global analysis of executables to "
            "detect and prevent known malware for your online hosts."
        ),
        "name": "Cloud Anti-malware",
        "setting_type": "mlslider",
        "value": {
            "detection": "DISABLED",
            "prevention": "DISABLED",
        },
    },
    "CredentialDumping": {
        "description": "Kill suspicious processes determined to be stealing logins and passwords.",
        "name": "Credential Dumping",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "Cryptowall": {
        "description": "A process associated with Cryptowall was blocked.",
        "name": "Cryptowall",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "CustomBlacklisting": {
        "description": (
            "Block processes matching hashes that you add to IOC Management with the action "
            "set to \"Block\" or \"Block, hide detection\"."
        ),
        "name": "Custom Blocking",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "DetectOnWrite": {
        "description": (
            "Use machine learning to analyze suspicious files when they're written to disk. "
            "To adjust detection sensitivity, change Anti-malware Detection levels in Sensor "
            "Machine Learning and Cloud Machine Learning."
        ),
        "name": "Detect on Write",
        "setting_type": "mlslider",
        "value": {
            "detection": "DISABLED",
            "prevention": "DISABLED",
        },
    },
    "DriveByDownload": {
        "description": (
            "A suspicious file written by a browser attempted to execute and was blocked."
        ),
        "name": "Drive-by Download",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "EmpyreBackdoor": {
        "description": "A process with behaviors indicative of the Empyre Backdoor was terminated.",
        "name": "Empyre Backdoor",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "EndUserNotifications": {
        "description": {
            "Mac": (
                "Show a pop-up notification to the end user when the Falcon sensor blocks, kills, "
                "or quarantines. See these messages in Console.app by searching for Process: "
                "Falcon Notifications."
            ),
            "Windows": (
                "Show a pop-up notification to the end user when the Falcon sensor blocks, "
                "kills, or quarantines. These messages also show up in the Windows Event Viewer "
                "under Applications and Service Logs."
            ),
        },
        "name": "Notify End Users",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "EngineProtectionV2": {
        "description": (
            "Provides visibility into malicious System Management Automation engine usage by "
            "any application. Requires Interpreter-Only."
        ),
        "name": "Engine (Full Visibility)",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "FileEncryption": {
        "description": (
            "A process that created a file with a known ransomware extension was terminated."
        ),
        "name": "File Encryption",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "FileSystemAccess": {
        "description": (
            "A process associated with a high volume of file system operations typical of "
            "ransomware behavior was terminated."
        ),
        "name": "File System Access",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "FilesystemVisibility": {
        "description": (
            "Allows the sensor to monitor filesystem activity for additional telemetry "
            "and improved detections."
        ),
        "name": "Filesystem Visibility",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "FirmwareAnalysisExtraction": {
        "description": (
            "Provides visibility into BIOS. Detects suspicious and unexpected images. Recommend "
            "testing to monitor system startup performance before full deployment."
        ),
        "name": "BIOS Deep Visibility",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "FirmwareDeepVisibility": {
        "description": "Provides visibility into BIOS. Detects suspicious and unexpected images.",
        "name": "BIOS Deep Visibility",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "FirmwareStandardVisibility": {
        "description": (
            "Provides visibility into BIOS configurations to detect vulnerable settings. For "
            "Big Sur, both kernel extension approval and reboot are required."
        ),
        "name": "BIOS Standard Visibility",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "ForceASLR": {
        "description": (
            "An Address Space Layout Randomization (ASLR) bypass attempt was detected and "
            "blocked. This may have been part of an attempted exploit."
        ),
        "name": "Force ASLR",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "ForceDEP": {
        "description": (
            "A process that had Force Data Execution Prevention (Force DEP) applied tried "
            "to execute non-executable memory and was blocked."
        ),
        "name": "Force DEP",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "HardwareEnhancedExploitDetection": {
        "description": (
            "Provides additional visibility into application exploits by using CPU hardware "
            "features that detect suspicious control flows. Available only for hosts running "
            "Windows 10 (RS4) or Windows Server 2016 Version 1803 or later and Skylake or "
            "later CPU."
        ),
        "name": "Hardware-Enhanced Exploit Detection",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "HashCollector": {
        "description": "An attempt to dump a user's hashed password was blocked.",
        "name": "Hash Collector",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "HeapSprayPreallocation": {
        "description": (
            "A heap spray attempt was detected and blocked. This may have been part of an "
            "attempted exploit."
        ),
        "name": "Heap Spray Preallocation",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "HTTPDetections": {
        "description": (
            "Allows the sensor to monitor unencrypted HTTP traffic and certain encrypted HTTPS "
            "traffic on the sensor for malicious patterns and generate detection events on "
            "non-Server systems."
        ),
        "name": "HTTP Detections",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "IntelPrevention": {
        "description": (
            "Block processes that CrowdStrike Intelligence analysts classify as malicious. "
            "These are focused on static hash-based IOCs."
        ),
        "name": "Intelligence-Sourced Threats",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "InterpreterProtection": {
        "description": (
            "Provides visibility into malicious PowerShell interpreter usage. For hosts running "
            "Windows 10, Script-Based Execution Monitoring may be used instead."
        ),
        "name": "Interpreter-Only",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "JavaScriptViaRundll32": {
        "description": "JavaScript executing from a command line via rundll32.exe was prevented.",
        "name": "JavaScript Execution Via Rundll32",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "KcPasswordDecoded": {
        "description": (
            "An attempt to recover a plaintext password via the kcpassword file was blocked."
        ),
        "name": "KcPassword Decoded",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "Locky": {
        "description": "A process determined to be associated with Locky was blocked.",
        "name": "Locky",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "MaliciousPowershell": {
        "description": (
            "Block execution of scripts and commands that CrowdStrike analysts classify as "
            "suspicious. Requires Interpreter-Only and/or Script-Based Execution Monitoring."
        ),
        "name": "Suspicious Scripts and Commands",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "NetworkVisibility": {
        "description": (
            "Allows the sensor to monitor network activity for additional telemetry and "
            "improved detections."
        ),
        "name": "Network Visibility",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "NextGenAV": {
        "description": (
            "Quarantine executable files after they're prevented by NGAV. When this is "
            "enabled, we recommend setting anti-malware prevention levels to Moderate "
            "and not using other antivirus solutions."
        ),
        "name": "Quarantine",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "NullPageAllocation": {
        "description": (
            "Allocating memory to the NULL (0) memory page was detected and blocked. This may "
            "have been part of an attempted exploit."
        ),
        "name": "NULL Page Allocation",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "OnSensorMLAdwarePUPSlider": {
        "description": (
            "For offline and online hosts, use sensor-based machine learning to identify and "
            "analyze unknown executables as they run to detect and prevent adware and "
            "potentially unwanted programs (PUP)."
        ),
        "name": "Adware & PUP",
        "setting_type": "mlslider",
        "value": {
            "detection": "DISABLED",
            "prevention": "DISABLED",
        },
    },
    "OnSensorMLSlider": {
        "description": (
            "For offline and online hosts, use sensor-based machine learning to identify and "
            "analyze unknown executables as they run to detect and prevent malware."
        ),
        "name": "Sensor Anti-malware",
        "setting_type": "mlslider",
        "value": {
            "detection": "DISABLED",
            "prevention": "DISABLED",
        },
    },
    "PreventSuspiciousProcesses": {
        "description": (
            "Block processes that CrowdStrike analysts classify as suspicious. These are focused "
            "on dynamic IOAs, such as malware, exploits and other threats."
        ),
        "name": "Suspicious Processes",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "ProcessHollowing": {
        "description": "Kill processes that unexpectedly injected code into another process.",
        "name": "Code Injection",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "QuarantineOnWrite": {
        "description": (
            "Use machine learning to quarantine suspicious files when they're written to disk. To "
            "adjust quarantine sensitivity, change Anti-malware Prevention levels in Sensor "
            "Machine Learning and Cloud Machine Learning."
        ),
        "name": "Quarantine on Write",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "RedactHTTPDetectionDetails": {
        "description": (
            "Remove certain information from HTTP Detection events, including URL, raw HTTP "
            "header and POST bodies if they were present. This does not affect the generation "
            "of HTTP Detections, only additional details that would be included and may include "
            "personal information (depending on the malware in question). When disabled, the "
            "information is used to improve the response to detection events. Has no effect "
            "unless HTTP Detections is also enabled."
        ),
        "name": "Redact HTTP Detection Details",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "AutomatedRemediation": {
        "description": (
            "Perform advanced remediation for IOA detections to kill processes, quarantine "
            "files, remove scheduled tasks, and clear and delete ASEP registry values."
        ),
        "name": "Advanced Remediation",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "ScriptBasedExecutionMonitoring": {
        "description": {
            "Linux": (
                "Provides visibility into suspicious scripts, including shell and "
                "other scripting languages.",
            ),
            "Mac": (
                "Provides visibility into suspicious scripts, including shell and "
                "other scripting languages."
            ),
            "Windows": (
                "For hosts running Windows 10 and Servers 2016 and later, "
                "provides visibility into suspicious scripts and VBA macros in Office "
                "documents. Requires Quarantine & Security Center Registration toggle "
                "to be enabled."
            ),
        },
        "name": "Script-Based Execution Monitoring",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "SEHOverwriteProtection": {
        "description": (
            "Overwriting a Structured Exception Handler (SEH) was detected and may have been "
            "blocked. This may have been part of an attempted exploit."
        ),
        "name": "SEH Overwrite Protection",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "SensorTamperingProtection": {
        "description": (
            "Blocks attempts to tamper with the sensor. If disabled, the sensor still creates "
            "detections for tampering attempts but doesn't block them. Disabling not recommended."
        ),
        "name": "Sensor Tampering Protection",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "SuspiciousKernelDrivers": {
        "description": (
            "Block the loading of kernel drivers that CrowdStrike analysts have identified as "
            "suspicious. Available on Windows 10 and Windows Server 2016 and later."
        ),
        "name": "Suspicious Kernel Drivers",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "SuspiciousRegistryOperations": {
        "description": (
            "Block registry operations that CrowdStrike analysts classify as suspicious. Focuses "
            "on dynamic IOAs, such as ASEPs and security config changes. The associated process "
            "may be killed."
        ),
        "name": "Suspicious Registry Operations",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "UnknownDetectionRelatedExecutables": {
        "description": (
            "Upload all unknown detection-related executables for advanced "
            "analysis in the cloud."
        ),
        "name": "Unknown Detection-Related Executables",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "UnknownExecutables": {
        "description": "Upload all unknown executables for advanced analysis in the cloud.",
        "name": "Unknown Executables",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "VolumeShadowCopyAudit": {
        "description": (
            "Create an alert when a suspicious process deletes volume shadow copies. "
            "Recommended: Use audit mode with a test group to try allowlisting trusted "
            "software before turning on Protect."
        ),
        "name": "Volume Shadow Copy - Audit",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "VolumeShadowCopyProtect": {
        "description": "Prevent suspicious processes from deleting volume shadow copies.",
        "name": "Volume Shadow Copy - Protect",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "WindowsLogonBypassStickyKeys": {
        "description": (
            "A command line process associated with Windows logon bypass was prevented "
            "from executing."
        ),
        "name": "Windows Logon Bypass (\"Sticky Keys\")",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
    "XPCOMShell": {
        "description": "The execution of an XPCOM shell was blocked.",
        "name": "XPCOM Shell",
        "setting_type": "toggle",
        "value": {
            "enabled": False,
        },
    },
}

OPTION_PLATFORM_MAPPING = {
    "Linux": {
        "User-Mode Capabilities": [
            "UnknownDetectionRelatedExecutables",
            "UnknownExecutables",
        ],
        "Enhanced Visibility": [
            "ScriptBasedExecutionMonitoring",
            "FilesystemVisibility",
            "NetworkVisibility",
        ],
        "Cloud Machine Learning": [
            "CloudAntiMalware",
        ],
        "Sensor Machine Learning": [
            "OnSensorMLSlider",
        ],
        "Execution Blocking": [
            "CustomBlacklisting",
            "PreventSuspiciousProcesses",
        ],
    },
    "Mac": {
        "User-Mode Capabilities": [
            "EndUserNotifications",
            "UnknownDetectionRelatedExecutables",
            "UnknownExecutables",
        ],
        "Enhanced Visibility": [
            "ScriptBasedExecutionMonitoring",
        ],
        "Firmware": [
            "FirmwareStandardVisibility",
            "FirmwareDeepVisibility",
        ],
        "Cloud Machine Learning": [
            "CloudAntiMalware",
            "AdwarePUP",
        ],
        "Sensor Machine Learning": [
            "OnSensorMLSlider",
            "OnSensorMLAdwarePUPSlider",
        ],
        "Quarantine": [
            "NextGenAV",
        ],
        "Execution Blocking": [
            "CustomBlacklisting",
            "PreventSuspiciousProcesses",
            "IntelPrevention",
        ],
        "Unauthorized Remote Access IOAs": [
            "XPCOMShell",
            "ChopperWebshell",
            "EmpyreBackdoor",
        ],
        "Credential Dumping IOAs": [
            "KcPasswordDecoded",
            "HashCollector",
        ],
    },
    "Windows": {
        "User-Mode Capabilities": [
            "EndUserNotifications",
            "UnknownDetectionRelatedExecutables",
            "UnknownExecutables",
            "SensorTamperingProtection",
        ],
        "Enhanced Visibility": [
            "AdditionalUserModeData",
            "InterpreterProtection",
            "EngineProtectionV2",
            "ScriptBasedExecutionMonitoring",
            "HTTPDetections",
            "RedactHTTPDetectionDetails",
            "HardwareEnhancedExploitDetection",
        ],
    },
    "Firmware": [
        "FirmwareAnalysisExtraction",
    ],
    "Cloud Machine Learning": [
        "CloudAntiMalware",
        "AdwarePUP",
    ],
    "Sensor Machine Learning": [
        "OnSensorMLSlider",
    ],
    "On Write": [
        "DetectOnWrite",
        "QuarantineOnWrite",
    ],
    "Quarantine": [
        "NextGenAV",
    ],
    "Execution Blocking": [
        "CustomBlacklisting",
        "PreventSuspiciousProcesses",
        "SuspiciousRegistryOperations",
        "MaliciousPowershell",
        "IntelPrevention",
        "SuspiciousKernelDrivers",
    ],
    "Exploit Mitigation": [
        "ForceASLR",
        "ForceDEP",
        "HeapSprayPreallocation",
        "NullPageAllocation",
        "SEHOverwriteProtection",
    ],
    "Ransomware": [
        "BackupDeletion",
        "Cryptowall",
        "FileEncryption",
        "Locky",
        "FileSystemAccess",
        "VolumeShadowCopyAudit",
        "VolumeShadowCopyProtect",
    ],
    "Exploitation Behavior": [
        "ApplicationExploitationActivity",
        "ChopperWebshell",
        "DriveByDownload",
        "ProcessHollowing",
        "JavaScriptViaRundll32",
    ],
    "Lateral Movement and Credential Access": [
        "WindowsLogonBypassStickyKeys",
        "CredentialDumping",
    ],
    "Remediation": [
        "AutomatedRemediation",
    ],
}


def generate_prevention_template(platform_name: str) -> Policy:
    """
    Generate a blank prevention policy object.

    This policy contains all settings in their default disabled states, ready for
    user or developer modification.
    """
    if platform_name not in OPTION_PLATFORM_MAPPING:
        raise Exception(f"The platform name {platform_name} is not valid")

    policy = Policy(style="prevention")
    policy.name = "Example Prevention Policy"
    policy.description = "Prevention policy generated from a template"
    policy.platform_name = platform_name

    for group_name, group_settings in OPTION_PLATFORM_MAPPING[platform_name].items():
        group = PolicySettingGroup()
        group.name = group_name

        for setting_id in group_settings:
            setting_data = COMMAND_TEMPLATES[setting_id]
            setting_desc = setting_data['description']
            if isinstance(setting_desc, dict):
                setting_desc = setting_desc[platform_name]
            setting_name = setting_data['name']
            setting_type = setting_data['setting_type']
            setting_value = setting_data['value']
            setting_template: ChangeablePolicySetting = SETTINGS_TYPE_MAP[setting_type]
            loadable_setting_data = {
                "description": setting_desc,
                "id": setting_id,
                "name": setting_name,
                "type": setting_type,
                "value": setting_value,
            }
            setting = setting_template(data_dict=loadable_setting_data)
            group.settings.append(setting)

        policy.settings_groups.append(group)

    return policy
