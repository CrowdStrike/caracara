"""Caracara HostsApiModule filters."""
import datetime

from caracara.common.constants import FILTER_OPERATORS, PLATFORMS
from caracara.filters.utils import (
    ISOTimestampChecker,
    RelativeTimestamp,
)
from caracara.filters.fql import FalconFilterAttribute


class HostContainedFilterAttribute(FalconFilterAttribute):
    """Filter hosts based on containment status."""

    name = "Contained"
    fql = "status"
    options = {
        "Contained": "contained",
        "Containment Pending": "containment_pending",
        "Not Contained": "normal",
    }
    restrict = True


class HostDomainFqlFilterAttribute(FalconFilterAttribute):
    """Filter by host AD domain."""

    name = "Domain"
    fql = "machine_domain"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts an AD domain, e.g. GOODDOMAIN or "
            "gooddomain.company.com. You can also provide multiple "
            "domains as a Python list or comma delimited string"
        )


class HostGroupIdFilterAttribute(FalconFilterAttribute):
    """Filter by host group ID."""

    name = "GroupID"
    fql = "groups"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts one or more Group IDs as either one "
            "string, or as a comma delimited list of strings. For example, "
            "075e03f5e5c04d83b4831374e7dc01c3 would target hosts within "
            "the group with ID 075e03f5e5c04d83b4831374e7dc01c3 only, or "
            "abcdefg123,abcdefg321 would target hosts in either group."
        )


class HostHostnameFilterAttribute(FalconFilterAttribute):
    """Filter by system hostname."""

    name = "Hostname"
    fql = "hostname"

    def example(self) -> str:
        """Show filter example."""
        return (
            "Provide either a single hostname string, or a list of hostnames "
            "via a comma delimited string or Python list. For example, "
            "you can omit two specific hosts with Hostname__NOT=HOST1,HOST2"
        )


class HostLastSeenFilterAttrribute(FalconFilterAttribute):
    """Filter for hosts last seen within a given timeframe."""

    name = "LastSeen"
    fql = "last_seen"
    types = [str]
    valid_operators = [
        "EQUAL",
        "GT",
        "GTE",
        "LT",
        "LTE",
    ]
    operator = "GTE"

    def _check_value(self, value) -> bool:
        """Confirm the provided value."""
        # Recycle the main check code first to make sure
        # we are working with a string input
        super()._check_value(value)

        if value.startswith(('-', '+')):
            rel_ts = RelativeTimestamp()
            returned = rel_ts.check_relative_timestamp(value)
        else:
            itc = ISOTimestampChecker()
            returned = itc.is_iso_format(value)

        return returned

    def get_fql(self) -> str:
        """Retrieve FQL syntax string."""
        if self.value is None:
            return ""

        operator_symbol = FILTER_OPERATORS[self.operator]

        if self.value.startswith(('-', '+')):
            rel_ts = RelativeTimestamp()
            new_timestamp = rel_ts.convert_relative_timestamp(
                datetime.datetime.utcnow(),
                self.value
            )
            value = new_timestamp.strftime(
                '%Y-%m-%dT%H:%M:%SZ'
            )
        else:
            value = self.value

        fql_string = f"{self.fql}: {operator_symbol}'{value}'"
        return fql_string

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts two types of parameter: a fixed ISO 8601 "
            "timestamp (such as 2020-01-01:01:00:00Z), or a relative "
            "timestamp such as -30m. -30m means time now, minus thirty "
            "minutes, so is best combined with an operator such as GTE. "
            "A popular example is LastSeen__GTE=-30m, to stipulate all hosts "
            "that have been online in the past half hour (i.e. are likely to "
            "be online)"
        )


class HostFirstSeenFilterAttribute(HostLastSeenFilterAttrribute):
    """Filter for hosts first seen by Falcon within a given timeframe."""

    # NB: this filter inherits from Last Seen to avoid tonnes of duplicated code
    name = "FirstSeen"
    fql = "first_seen"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts two types of parameter: a fixed ISO 8601 "
            "timestamp (such as 2020-01-01:01:00:00Z), or a relative "
            "timestamp such as -30m. -30m means time now, minus thirty "
            "minutes, so is best combined with an operator such as GTE. "
            "One example is FirstSeen__GTE=-1d, to filter for all new hosts "
            "that have been added to Falcon within the past 1 day."
        )


class HostLocalIPFilterAttribute(FalconFilterAttribute):
    """Filter by host local IP addresses."""

    name = "LocalIP"
    fql = "local_ip"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts an IP address string associated with a "
            "network card, e.g. 172.16.1.2 or 172.16.* to cover the /16 "
            "range. You can also comma delimit strings for multiple matches, "
            "e.g. 172.16.1.2,172.16.1.3 to target hosts with each of those "
            "IPs, or provide a Python list of IP strings"
        )


class HostOSFqlFilterAttribute(FalconFilterAttribute):
    """
    Filter by host operating system types.

    Current valid options are Windows, Mac and Linux.
    """

    name = "OS"
    fql = "platform_name"
    options = PLATFORMS
    restrict = True


class HostOSVersionFqlFilterAttribute(FalconFilterAttribute):
    """Filter by Operating System version (e.g., Windows 7, RHEL 7.9, etc.)."""

    name = "OSVersion"
    fql = "os_version"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts a name of an operating system version "
            "and can be supplied many times. For example, Windows 7, "
            "RHEL 7.9, Catalina (10.15), etc."
        )


class HostRoleFilterAttribute(FalconFilterAttribute):
    """
    Filter by host role.

    Current valid options are DC, Server and Workstation.
    """

    name = "Role"
    fql = "product_type_desc"
    options = {
        "DC": "Domain Controller",
        "Server": "Server",
        "Workstation": "Workstation",
    }
    restrict = True


class HostSiteFilterAttribute(FalconFilterAttribute):
    """Filter by site name."""

    name = "Site"
    fql = "site_name"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts one or more site names as either one "
            "string, or as a comma delimtied list of strings. For example, "
            "London,Manchster1,Manchester2 would target hosts within any of "
            "those three sites."
        )


class HostTagFilterAttribute(FalconFilterAttribute):
    """
    Filter by sensor tag.

    - Tags created in Falcon should be prepended with FalconGroupingTag/
    - Tags created during the Sensor installion, or added to the restriry sould be prepended with
      SensorGroupingTag/
    """

    name = "Tag"
    description = "Filter by sensor tag"
    fql = "tags"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts one or more sensor tags as either one "
            "string, or as a comma delimited list of strings. For example, "
            "tag1,tag2,tag3 to filter by hosts with one of those tags."
        )


class HostOUFilterAttribute(FalconFilterAttribute):
    """Filter by Organisational Unit (OU)."""

    name = "OU"
    fql = "ou"

    def example(self) -> str:
        """Show filter example."""
        return (
            "This filter accepts an Organisational Unit (OU) name as a "
            "string. You can also comma delimit OUs for multiple matches, "
            "e.g. UKServers,USServers to target hosts within any of those "
            "OUs. Programmatically, you can pass a Python list of OUs."
        )


FILTER_ATTRIBUTES = [
    HostContainedFilterAttribute,
    HostDomainFqlFilterAttribute,
    HostGroupIdFilterAttribute,
    HostHostnameFilterAttribute,
    HostLastSeenFilterAttrribute,
    HostFirstSeenFilterAttribute,
    HostLocalIPFilterAttribute,
    HostOSFqlFilterAttribute,
    HostOSVersionFqlFilterAttribute,
    HostRoleFilterAttribute,
    HostSiteFilterAttribute,
    HostTagFilterAttribute,
    HostOUFilterAttribute,
]
