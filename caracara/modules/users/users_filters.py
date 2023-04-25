"""User Management-Specific FQL Filters."""
from caracara.filters.fql import FalconFilterAttribute


class UsersAssignedCIDsFilterAttribute(FalconFilterAttribute):
    """Filter by CIDs assigned to a user."""

    name = "AssignedCIDs"
    fql = "assigned_cids"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts a CID that the user should be assigned to."
        )


class UsersCIDFilterAttribute(FalconFilterAttribute):
    """Filter by a user's home CID."""

    name = "CID"
    fql = "cid"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts a CID that would represent the user's home CID."
        )


class UsersFirstNameFilterAttribute(FalconFilterAttribute):
    """Filter by a user's first name."""

    name = "FirstName"
    fql = "first_name"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts a user's first name, such as John."
        )


class UsersLastNameFilterAttribute(FalconFilterAttribute):
    """Filter by a user's last name."""

    name = "LastName"
    fql = "last_name"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts a user's last name, such as Smith."
        )


class UsersNameFilterAttribute(FalconFilterAttribute):
    """Filter by a user's name."""

    name = "Name"
    fql = "name"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts a user's name, such as John Smith."
        )


FILTER_ATTRIBUTES = [
    UsersAssignedCIDsFilterAttribute,
    UsersCIDFilterAttribute,
    UsersFirstNameFilterAttribute,
    UsersLastNameFilterAttribute,
    UsersNameFilterAttribute,
]
