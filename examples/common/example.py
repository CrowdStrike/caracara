"""Caracara Examples: Common Backend."""

# pylint: disable=duplicate-code
import logging
import os
import sys
from functools import wraps
from typing import Dict

import yaml

from caracara import Client
from caracara.common.csdialog import csradiolist_dialog
from caracara.common.interpolation import VariableInterpolator

_config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "config.yml",
)


def _select_profile(config: dict) -> str:
    """Display a selection menu for the user to choose a profile from config.yml."""
    profiles = config["profiles"]
    profile_names = profiles.keys()
    profile_pairs = []
    for profile_name in profile_names:
        falcon = profiles[profile_name].get("falcon")
        if falcon is None:
            print(f"{profile_name} does not have a falcon stanza; skipping")
            continue
        cln = VariableInterpolator()
        client_id = cln.interpolate(
            str(profiles[profile_name]["falcon"].get("client_id", "ENVIRONMENT"))
        )
        profile_text = f"{profile_name} (Client ID: {client_id[0:7]}{'x'*24})"
        profile_pairs.append((profile_name, profile_text))

    profile_name = csradiolist_dialog(
        title="Profile Selection",
        text="Choose a profile from your examples config.yml",
        values=profile_pairs,
    ).run()

    if profile_name is None:
        print("No profile chosen. Exiting example.")
        sys.exit(1)

    print(f"Using the {profile_name} profile")
    return profile_name


def _get_profile() -> Dict:
    """Load a profile from config.yml and return its settings as a Dictionary."""
    if not os.path.exists(_config_path):
        raise FileNotFoundError(f"You must create the file {_config_path}")

    with open(_config_path, "r", encoding="utf8") as yaml_config_file:
        config = yaml.safe_load(yaml_config_file)

    if "profiles" not in config:
        raise KeyError("You must create a profiles stanza in the configuration YAML file")

    profile_names = list(config["profiles"].keys())
    global_config = None
    if "globals" in config:
        global_config = config["globals"]
    # Check for default profile
    default_name = None
    for prof in profile_names:
        if config["profiles"][prof].get("default", False):
            default_name = prof
            # First one we encounter is the default
            break

    # Check to see if the user provided us with a profile name as the first argument
    profile_name = None
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
        if profile_name not in profile_names:
            raise KeyError(f"The profile named {profile_name} does not exist in config.yml")
    elif len(profile_names) == 1:
        # There's only one, treat it as the default
        profile_name = profile_names[0]
    elif default_name:
        # Default profile key has been set
        profile_name = default_name
    else:
        profile_name = _select_profile(config)

    profile = config["profiles"][profile_name]
    return profile, global_config


def _configure_logging(profile: Dict) -> None:
    """Set up the logger based on the configuration in config.yml."""
    log_format = "%(name)s: %(message)s"
    log_level = logging.INFO

    if "logging" in profile:
        logging_data = profile["logging"]
        if "level" in logging_data:
            level_str = str.upper(logging_data["level"])
            if hasattr(logging, level_str):
                log_level = getattr(logging, level_str)
            else:
                raise ValueError(f"{level_str} is not a valid logging level")

        if "format" in logging_data:
            log_format = logging_data["format"]

    logging.basicConfig(format=log_format, level=log_level)


def _get_example_settings(profile: Dict, example_abs_path: str, globalsettings: Dict) -> Dict:
    """Load example-specific settings from config.yml based on the filename."""
    # Get the base path of the examples module by obtaining the common
    # path between this file and the example in question
    common_path = os.path.commonpath([__file__, example_abs_path])

    # Strip away the common path from the path to the example
    example_rel_path = example_abs_path.replace(common_path, "")

    # Remove the leading / or \
    if example_rel_path.startswith(os.path.sep):
        example_rel_path = example_rel_path[1:]

    # Remove the file extension so that we get just the example name, without the .py
    example_rel_path, _ = os.path.splitext(example_rel_path)

    # Split the resultant path into a list of sections
    example_dict_path = example_rel_path.split(os.path.sep)

    # Set our example module and name
    example_module = example_dict_path[0]
    example_name = example_dict_path[1]

    # Get global settings for this example
    global_settings = globalsettings.get("examples", {})
    global_module_settings = global_settings.get(example_module, {})
    global_example_settings = global_module_settings.get(example_name, {})

    # Get profile settings for this example
    profile_module_settings = profile.get("examples", {}).get(example_module, {})
    profile_example_settings = profile_module_settings.get(example_name, {})

    # Overlay global example settings with profile-specific example settings
    # The dicts are expanded in order, so the profile-specific settings will overlay the global ones
    merged_example_settings = {**global_example_settings, **profile_example_settings}

    # Return back the merged settings dictionary
    return merged_example_settings


def caracara_example(example_func):
    """Caracara Example Decorator."""

    @wraps(example_func)
    def wrapped(*args, **kwargs):
        profile, global_config = _get_profile()
        if not profile:
            raise TypeError("No profile chosen; aborting")

        if "falcon" not in profile:
            raise KeyError(
                "You must create a falcon stanza within the profile's "
                "section of the configuration YAML file"
            )

        falcon_config: Dict = profile["falcon"]

        _configure_logging(profile)

        client = Client(**falcon_config)

        example_settings = _get_example_settings(
            profile,
            example_func.__globals__["__file__"],
            global_config,
        )

        # Pass data back to the example via keyword arguments
        kwargs["client"] = client
        kwargs["logger"] = logging.getLogger(example_func.__name__)
        kwargs["settings"] = example_settings

        return example_func(*args, **kwargs)

    return wrapped
