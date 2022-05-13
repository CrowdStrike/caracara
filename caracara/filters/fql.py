"""Falcon Query Language (FQL) generation code."""
from abc import ABC, abstractmethod
from typing import List

from caracara.common.constants import FILTER_OPERATORS


class FalconFilterAttribute(ABC):
    """
    Generic Falcon Filter Attribute.

    Class to represent an something that can be filtered on, such as a
    computer domain, OS or computer role (e.g. Server, DC, Workstation).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Store the friendly name for the filter. Cannot include spaces. Example: OS."""

    @property
    def description(self) -> str:
        """
        Store a short description of the filter and what it can be used for.

        Defaults to returning the doc string.
        """
        return __doc__

    @property
    @abstractmethod
    def fql(self) -> str:
        """Return the name of the attribute as it will be written when converted to FQL."""

    def example(self) -> str:
        """
        Store example usage of the filter.

        Auto-generated based on options, but can be overridden with a simple string function.
        """
        if not hasattr(self, 'options'):
            raise NotImplementedError(
                "Filter should implement its example string as no set "
                "options are programmed into this filter."
            )

        if isinstance(self.options, list):
            return (
                "This filter accepts one or more of the following "
                "options as a comma delimited list or bare string: " +
                ", ".join(self.options)
            )

        if isinstance(self.options, dict):
            return (
                "This filter accepts one or more of the following "
                "options as a comma delimited list or bare string: " +
                ", ".join(self.options.keys())
            )

        # We have reached a self.options type that we do not support yet (or is incorrect)
        raise NotImplementedError(
            "Filter should implement its example string as the options "
            "are of an unknown type."
        )

    # Define the acceptable types for this filter's value passed in by the
    # code or user
    types: List = [str, list]

    # Default to not restricting the values to a predefined list
    restrict: bool = False

    # A list of valid values
    options: None

    # The current value of this filter instance
    value = None

    # Valid operators (e.g. EQUAL, NOT, etc.)
    valid_operators: List[str] = [
        "EQUAL",
        "NOT",
    ]

    # Current operator, which defaults to EQUAL unless overridden
    operator = "EQUAL"

    def __str__(self):
        """Convert a filter attribute to a valid FQL string."""
        return f'{self.name}: {self.operator} {self.value}'

    def _options_is_dict(self) -> bool:
        if isinstance(self.options, dict):
            return True

        if isinstance(self.options, list):
            return False

        # self.options is of an invalid type according to the specification
        raise Exception(
            f'The filter {self.name} was initialised incorrectly'
        )

    def _check_option(self, value: str) -> bool:
        if self.options is None:
            raise Exception(
                (
                    f'The filter {self.name} was initialised '
                    'incorrectly. options cannot be None here.'
                )
            )

        if self._options_is_dict():
            if value in self.options.keys():
                return True
        else:
            if value in self.options:
                return True

        return False

    def _check_value(self, value) -> bool:
        """Check whether a certain value will fulfill the criteria given."""
        # If the type of the value is invalid then the value is automatically
        # marked as invalid
        if not any((isinstance(value, x) for x in self.types)):
            return False

        # If the type of the value is valid and the value itself is not
        # restricted to a fixed list, then the value is okay
        if not self.restrict:
            return True

        # We now cover the main cases (string or list of strings);
        # therefore, if the types list above is changed for a given subclass
        # then this function will need to be overridden
        if isinstance(value, str):
            return self._check_option(value)

        if isinstance(value, list):
            for sub_value in value:
                if not isinstance(sub_value, str):
                    return False
                if not self._check_option(sub_value):
                    return False
            return True

        # The filter value is not an instance of a supported type
        raise Exception(
            f'The filter {self.name} was initialised incorrectly. '
            '_check_value must be overridden to use a different type of '
            'value coercion.'
        )

    def set_value(self, value):
        """Set the filter value utilising internal sanity checks."""
        if self._check_value(value):
            self.value = value
        else:
            raise Exception(
                self.name,
                str(value)
            )

    def set_operator(self, operator: str):
        """Set the operator to be applied to the filter (e.g., =, >)."""
        if operator in self.valid_operators:
            self.operator = operator
        else:
            raise Exception(
                self.name,
                operator,
                self.valid_operators
            )

    def get_fql(self) -> str:
        """
        Convert the internal data structure to useful FQL.

        For different types of filters this function may need to be overridden.
        It will work for str and list(str) filters out the box.
        """
        operator_symbol = FILTER_OPERATORS[self.operator]

        if self.value is None:
            return f'{self.fql}:{operator_symbol}null'

        if self.restrict and self._options_is_dict():
            if isinstance(self.value, str):
                fql_value = "'" + self.options[self.value] + "'"
            else:
                fql_value = (
                    '[' +
                    ','.join(
                        f"'{self.options[x]}'" for x in self.value
                    ) +
                    ']'
                )
        else:
            if isinstance(self.value, str):
                fql_value = f"'{self.value}'"
            else:
                fql_value = (
                    '[' +
                    ','.join(
                        f"'{x}'" for x in self.value
                    ) +
                    ']'
                )
        fql_string = f'{self.fql}: {operator_symbol}{fql_value}'
        return fql_string
