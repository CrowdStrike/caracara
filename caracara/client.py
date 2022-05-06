"""
Caracara API Client
"""
import logging

try:
    from falconpy import (
        APIHarness,
        OAuth2,
        confirm_base_region,
        confirm_base_url
    )
except ImportError as no_falconpy:
    raise SystemExit("The crowdstrike-falconpy library is not installed.") from no_falconpy

from caracara.common import FILTER_ATTRIBUTES as common_filter_attributes
from caracara.common.meta import user_agent_string
from caracara.filters.falcon_filter import FalconFilter
from caracara.filters.fql import FalconFilterAttribute
from caracara.modules import (
    HostsApiModule,
    PreventionPoliciesApiModule,
    ResponsePoliciesApiModule,
    RTRApiModule,
    MODULE_FILTER_ATTRIBUTES,
)


class Client:
    """
    Falcon API client.

    This class exposes all available Falcon API commands, and proxies requests through
    the FalconPy library.
    """
    class FalconFilter(FalconFilter):
        """Create a sub-class of the FalconFilter class which we own locally within
        the client. This allows us to dynamically calculate the FQL filter attributes
        that we hava available and make them available at runtime.
        """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        client_id: str,
        client_secret: str,
        cloud_name: str = "auto",
        member_cid: str = None,
        ssl_verify: str = True,
        timeout: float = None,
        proxy: str = None,
        user_agent: str = None,
        verbose: bool = False,
    ):
        self.logger = logging.getLogger(__name__)

        self.logger.info("Setting up the Caracara client")
        self.logger.info(
            "Client ID: %s; Cloud: %s; Member CID: %s",
            client_id, client_secret, member_cid
        )
        self.logger.debug("SSL verification is %s", ssl_verify)
        self.logger.debug("Timeout: %f", timeout)
        self.logger.debug("Configured proxy: %s", proxy)

        if not user_agent:
            user_agent = user_agent_string()
        self.logger.debug("User agent: %s", user_agent)

        self.verbose = verbose
        self.logger.debug("Verbose mode: %s", verbose)

        base_url = confirm_base_region(confirm_base_url(provided_base=cloud_name))
        self.logger.info("Base URL: %s", base_url)

        self.logger.debug("Configuring api_authentication object as an OAuth2 object")
        # Pre-configured auth object for service classes
        self.api_authentication = OAuth2(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            member_cid=member_cid,
            ssl_verify=ssl_verify,
            proxy=proxy,
            timeout=timeout,
            user_agent=user_agent,
        )

        self.logger.debug("Configuring an APIHarness to access the uber class")
        # Uber class
        self.api_harness = APIHarness(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            member_cid=member_cid,
            ssl_verify=ssl_verify,
            proxy=proxy,
            timeout=timeout,
            user_agent=user_agent,
        )

        # Configure modules here so that IDEs can pick them up
        self.logger.debug("Setting up Hosts module")
        self.hosts = HostsApiModule(self.api_authentication)
        self.logger.debug("Setting up the Prevention Policies module")
        self.prevention_policies = PreventionPoliciesApiModule(self.api_authentication)
        self.logger.debug("Setting up the Response Policies module")
        self.response_policies = ResponsePoliciesApiModule(self.api_authentication)
        self.logger.debug("Setting up RTR module")
        self.rtr = RTRApiModule(self.api_authentication)

        self.logger.debug("Configuring FQL filters")
        # Pre-configure the FQL modules for faster instantiation later
        filter_attribute_classes = [
            *common_filter_attributes,
            *MODULE_FILTER_ATTRIBUTES,
        ]
        available_filters = {}
        for filter_attribute_class in filter_attribute_classes:
            instance: FalconFilterAttribute = filter_attribute_class()
            available_filters[instance.name] = filter_attribute_class

        # Modify the falcon filter class to contain the available filters
        self.FalconFilter.available_filters = available_filters

        self.logger.info("Caracara client configured")

    def __enter__(self):
        """Allow for entry as a context manager."""
        self.logger.debug("Entering Caracara context manager")
        return self

    def __exit__(self, *args):
        """Discard our token when we exit the context."""
        self.logger.info("Revoking API token")
        self.api_authentication.revoke(self.api_authentication.token_value)
        self.logger.debug("Discarding Caracara context manager")
        return args
