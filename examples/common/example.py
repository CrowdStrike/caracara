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

        client_id = falcon.get("client_id")
        if client_id is None:
            print(f"The falcon stanza in {profile_name} does not contain a client ID; skipping")
            continue

        client_id = str(client_id)
        profile_text = f"{profile_name} (Client ID: {client_id[0:7]}{"x"*24})"
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

    with open(_config_path, 'r', encoding='utf8') as yaml_config_file:
        config = yaml.safe_load(yaml_config_file)

    if 'profiles' not in config:
        raise KeyError("You must create a profiles stanza in the configuration YAML file")

    profile_names = list(config['profiles'].keys())
    # Check to see if the user provided us with a profile name as the first argument
    profile_name = None
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
        if profile_name not in profile_names:
            raise KeyError(f"The profile named {profile_name} does not exist in config.yml")
    else:
        profile_name = _select_profile(config)

    profile = config['profiles'][profile_name]
    return profile


def _configure_logging(profile: Dict) -> None:
    """Set up the logger based on the configuration in config.yml."""
    log_format = "%(name)s: %(message)s"
    log_level = logging.INFO

    if 'logging' in profile:
        logging_data = profile['logging']
        if 'level' in logging_data:
            level_str = str.upper(logging_data['level'])
            if hasattr(logging, level_str):
                log_level = getattr(logging, level_str)
            else:
                raise ValueError(f"{level_str} is not a valid logging level")

        if 'format' in logging_data:
            log_format = logging_data['format']

    logging.basicConfig(format=log_format, level=log_level)


def _get_example_settings(profile: Dict, example_abs_path: str) -> Dict:
    """Load example-specific settings from config.yml based on the filename."""
    if 'examples' not in profile:
        return None

    # Get the base path of the examples module by obtaining the common
    # path between this file and the example in question
    common_path = os.path.commonpath([__file__, example_abs_path])

    # Strip away the common path from the path to the example
    example_rel_path = example_abs_path.replace(common_path, '')

    # Remove the leading / or \
    if example_rel_path.startswith(os.path.sep):
        example_rel_path = example_rel_path[1:]

    # Remove the file extension so that we get just the example name, without the .py
    example_rel_path, _ = os.path.splitext(example_rel_path)

    # Split the resultant path into a list of sectiions
    example_dict_path = example_rel_path.split(os.path.sep)

    """
    Iterate over every part of the path to ensure that the example-specific data
    exists within the config.yml. We would rather return None here than throw an
    exception. It is up to each individual module to check whether the settings are
    complete.
    """
    example_settings = profile['examples']
    for path_section in example_dict_path:
        if path_section not in example_settings:
            return None

        example_settings = example_settings[path_section]

    # Returns the settings relative to this particular example
    return example_settings


def caracara_example(example_func):
    """Caracara Example Decorator."""
    @wraps(example_func)
    def wrapped(*args, **kwargs):
        profile = _get_profile()
        if not profile:
            raise TypeError("No profile chosen; aborting")

        if 'falcon' not in profile:
            raise KeyError(
                "You must create a falcon stanza within the profile's "
                "section of the configuration YAML file"
            )

        falcon_config: Dict = profile['falcon']

        if 'client_id' not in falcon_config or 'client_secret' not in falcon_config:
            raise KeyError("You must include, at minimum, a client_id and client_secret")

        _configure_logging(profile)

        client = Client(**falcon_config)

        example_settings = _get_example_settings(
            profile,
            example_func.__globals__['__file__'],
        )

        # Pass data back to the example via keyword arguments
        kwargs['client'] = client
        kwargs['logger'] = logging.getLogger(example_func.__name__)
        kwargs['settings'] = example_settings

        return example_func(*args, **kwargs)

    return wrapped
