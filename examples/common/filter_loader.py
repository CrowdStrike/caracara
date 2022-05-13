"""
Caracara Examples: Filter Loader.

This module loads a list of filter dictionaries (K->V pairs) and
imports them them into a pre-existing FalconFilter object.

This is used in examples that require filters to be specified in their
respective settings to be loaded and error checked.
"""

from typing import Dict, List

from caracara.filters import FalconFilter


def parse_filter_list(filter_list: List[Dict], filters: FalconFilter) -> None:
    """Load a list or dictionary of filters from a YAML file into a FalconFilter object."""
    if filter_list is None:
        return

    if not isinstance(filter_list, List):
        raise Exception("Filters should be provided as a YAML list")

    for filter_dict in filter_list:
        if not isinstance(filter_dict, Dict):
            raise Exception(f"Filter {filter_dict} is not in the correct format")

        for key, value in filter_dict.items():
            filters.create_new_filter_from_kv_string(key, value)
