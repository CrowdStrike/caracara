"""
Caracara Examples: Utillities.

A series of functions to improve example output.
"""
import json

from typing import Dict, List


def prettify_json(data: List or Dict) -> str:
    """Dums dictionaries and lists as formatted JSON."""
    return json.dumps(data, sort_keys=True, indent=4)


def pretty_print(data: List or Dict, rewrite_new_lines: bool = False) -> str:
    """Format dictionaries and lists nicely, and optionally rewrite new line characters."""
    pretty_data = prettify_json(data)
    if rewrite_new_lines:
        pretty_data = pretty_data.replace("\\n", "\n")
    return pretty_data
