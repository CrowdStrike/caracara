"""
Falcon Filter class, allowing for dynamically generated FQL strings.
"""
import logging

from typing import Any, List
from uuid import uuid4

from caracara.filters.fql import FalconFilterAttribute


class FalconFilter:
    """
    Class to handle filtering hosts within Falcon.
    This encompasses the various known types of
    filter, and allows building up FQL queries,
    ready to pass straight into Falcon API calls
    as GET parameters.
    """
    available_filters = {}
    filters = {}
    logger = logging.getLogger(__name__)

    def set_filter_value(self, filter_id: str, value):
        """
        A filter_id is provided by add_filter, and can be used to
        reference a given filter.
        This is because it is possible to combine filters of the same
        type (e.g. to have a date range).
        """
        self.logger.info("Setting filter %s to %s", filter_id, value)
        if filter_id not in self.filters:
            raise Exception(f"Filter with ID {filter_id} does not exist here")

        self.filters[filter_id].set_value(value)

    def set_filter_operator(self, filter_id: str, operator: str):
        """
        A filter_id is provided by add_filter, and can be used to
        reference a given filter.
        This is because it is possible to combine filters of the same
        type (e.g. to have a date range).
        """
        self.logger.info("Setting the filter operator of filter %s to %s", filter_id, operator)
        if filter_id not in self.filters:
            raise Exception(f"Filter with ID {filter_id} does not exist here")

        self.filters[filter_id].set_operator(operator)

    def add_filter(self, new_filter: FalconFilterAttribute) -> str:
        """
        Adds a filter built and configured externally to this object
        """
        filter_id = str(uuid4())
        self.logger.info("Adding a new %s filter with filter ID %s", new_filter.name, filter_id)
        self.filters[filter_id] = new_filter
        return filter_id

    def remove_filter(self, filter_id: str):
        """Remove a filter from the current filter class by ID"""
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
        Creates a new filter based on a template, and returns an ID in case the developer wishes
        to remove this filter from the resultalt FQL string later.
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
        Create a filter from a key->value string. Examples:
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
        """Returns a valid FQL string based on the Falcon Filter object"""
        fql = '+'.join(x.get_fql() for x in self.filters.values())
        self.logger.info("Generated FQL: %s", fql)
        return fql

    def __init__(self, filters: List[FalconFilterAttribute] = None):
        """
        Set up a new Falcon Filter object. If filter data
        already exists this can be passed in as a dict
        so that the FQL can be generated instantly.
        Otherwise, the user can add filter data
        at will, and then dump to FQL when ready.
        """
        self.logger.debug("Initialising a new FalconFilter object")
        if filters:
            for initial_filter in filters:
                self.add_filter(initial_filter)

    def __str__(self):
        return self.get_fql()
