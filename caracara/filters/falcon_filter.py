"""
Falcon FQL Filter Wrapper class.

This class keeps track of Falcon FQL filter objects, and can return a valid, fully generated
FQL string representing all the filter objects within it.
"""
import logging

from typing import Any, List
from uuid import uuid4

from caracara.filters.fql import FalconFilterAttribute


class FalconFilter:
    """
    Falcon FQL Filter Wrapper class.

    Class to handle filtering hosts within Falcon. This encompasses the various known types of
    filter, and allows building up FQL queries, ready to pass straight into Falcon API calls
    as GET parameters.

    Each filter is referred to within the class by a unique, randomly generated ID. This is beacuse
    it is possible to combine filters of the same type (e.g., to have a date range), so the filter
    type cannot be used as a key within the internal dictionary.
    """

    available_filters = {}
    filters = {}
    logger = logging.getLogger(__name__)

    def set_filter_value(self, filter_id: str, value):
        """Set the value for a filter by filter ID."""
        self.logger.info("Setting filter %s to %s", filter_id, value)
        if filter_id not in self.filters:
            raise Exception(f"Filter with ID {filter_id} does not exist here")

        self.filters[filter_id].set_value(value)

    def set_filter_operator(self, filter_id: str, operator: str):
        """Set the operator / comparator for an FQL filter by filter ID."""
        self.logger.info("Setting the filter operator of filter %s to %s", filter_id, operator)
        if filter_id not in self.filters:
            raise Exception(f"Filter with ID {filter_id} does not exist here")

        self.filters[filter_id].set_operator(operator)

    def add_filter(self, new_filter: FalconFilterAttribute) -> str:
        """Add a filter built externally to this object to the internal filter dictionary."""
        filter_id = str(uuid4())
        self.logger.info("Adding a new %s filter with filter ID %s", new_filter.name, filter_id)
        self.filters[filter_id] = new_filter
        return filter_id

    def remove_filter(self, filter_id: str):
        """Remove a filter from the current filter object by filter ID."""
        if filter_id in self.filters:
            self.logger.info("Removing filter with ID %s", filter_id)
            del self.filters[filter_id]
        else:
            self.logger.info(
                "Attempted to remove filter with ID %s, but it does not exist",
                filter_id,
            )

    def create_new_filter(
        self,
        filter_name: str,
        initial_value: Any = None,
        initial_operator: str = "EQUAL"
    ) -> str:
        """
        Create a new filter and add it to the FalconFilter object.

        This function will create a new filter via the filter's friendly name.
        The new filter's unique ID string is returned in case the developer wishes
        to reference and/or remove this specific filter within the FalconFilter object later.
        """
        self.logger.debug(
            "Creating a new %s filter (initial operator: %s; initial value: %s",
            filter_name, initial_operator, initial_value,
        )
        if filter_name not in self.available_filters:
            raise Exception(filter_name)

        new_filter = self.available_filters[filter_name]()
        if initial_value:
            new_filter.set_value(initial_value)
        if initial_operator:
            new_filter.set_operator(initial_operator)

        filter_id = self.add_filter(new_filter)
        self.logger.info("Created new %s filter with ID %s", filter_name, filter_id)
        return filter_id

    def create_new_filter_from_kv_string(self, key_string: str, value):
        """
        Create a filter from a key->value string.

        Examples:
        -> Domain__NOT=ExcludeDomain.com
        -> LastSeen__GTE=1970-01-01T00:00:00Z
        """
        self.logger.info("Loading filter from KV string: %s", key_string)

        if "__" in key_string:
            filter_name, operator = key_string.split("__")
        else:
            filter_name = key_string
            operator = None  # None operator results in the default

        if isinstance(value, str):
            if ',' in value:
                value = value.split(',')

        if operator:
            return self.create_new_filter(
                filter_name=filter_name,
                initial_value=value,
                initial_operator=operator
            )

        return self.create_new_filter(
            filter_name=filter_name,
            initial_value=value
        )

    def get_fql(self) -> str:
        """Return a valid FQL string based on the filters within the FalconFilter object."""
        fql = '+'.join(x.get_fql() for x in self.filters.values())
        self.logger.info("Generated FQL: %s", fql)
        return fql

    def __init__(self, filters: List[FalconFilterAttribute] = None):
        """
        Set up a new Falcon Filter object.

        If filter data already exists, this can be passed in as a dictionary so that the
        FQL can be generated instantly. Otherwise, the developer can add filter data at will,
        and then dump to FQL when ready.
        """
        self.logger.debug("Initialising a new FalconFilter object")
        if filters:
            for initial_filter in filters:
                self.add_filter(initial_filter)

    def __str__(self):
        """Dump the filters within the FalconFilter object to an FQL string."""
        return self.get_fql()
