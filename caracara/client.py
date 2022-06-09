"""Caracara API Client."""

import logging

try:
    from falconpy import (
        OAuth2,
        confirm_base_region,
        confirm_base_url
    )
except ImportError as no_falconpy:
    raise SystemExit("The crowdstrike-falconpy library is not installed.") from no_falconpy

from caracara.common import FILTER_ATTRIBUTES as common_filter_attributes
from caracara.common.interpolation import VariableInterpolator
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
        """
        Falcon Filter wrapper class.

        Create a sub-class of the FalconFilter class which we own locally within
        the client. This allows us to dynamically calculate the FQL filter attributes
        that we hava available and make them available at runtime.
        """

    def __init__(  # pylint: disable=R0913,R0914,R0915
        self,
        client_id: str = None,
        client_secret: str = None,
        cloud_name: str = "auto",
        member_cid: str = None,
        ssl_verify: bool = True,
        timeout: float = None,
        proxy: str = None,
        user_agent: str = None,
        verbose: bool = False,
        falconpy_authobject: OAuth2 = None,
    ):
        """Configure a Caracara Falcon API Client object."""
        self.logger = logging.getLogger(__name__)

        if client_id is None and client_secret is None and falconpy_authobject is None:
            raise Exception(
                "You must provide either a Client ID and Client Secret, "
                "or a pre-created FalconPy OAuth2 object"
            )

        if client_id is not None and client_secret is None:
            raise Exception("You cannot provide a Client ID without a Client Secret")

        if client_id is not None and falconpy_authobject is not None:
            raise Exception(
                "Please provide either a Client ID/Client Secret pair, "
                "or a pre-created FalconPy OAuth2 object, but not both"
            )

        self.logger.info("Setting up the Caracara client and configuring authentication")

        if client_id:
            # Load all parameters for the FalconPy authentication object into a dictionary
            # and handle environment variable interpolation
            interpolator = VariableInterpolator()
            cloud_name = interpolator.interpolate(cloud_name)
            client_id = interpolator.interpolate(client_id)
            member_cid = interpolator.interpolate(member_cid)
            user_agent = interpolator.interpolate(user_agent)
            proxy = interpolator.interpolate(proxy)
            auth_keys = {
                "base_url": cloud_name,
                "client_id": client_id,
                "client_secret": interpolator.interpolate(client_secret),
                "member_cid": member_cid,
                "proxy": proxy,
                "user_agent": user_agent,
                "ssl_verify": ssl_verify,
                "timeout": timeout,
            }

            self.logger.info(
                "Client ID: %s; Cloud: %s; Member CID: %s",
                client_id, cloud_name, member_cid,
            )
            self.logger.debug("SSL verification is %s", ssl_verify)
            self.logger.debug("Timeout: %s", str(timeout))
            self.logger.debug("Configured proxy: %s", proxy)

            # Remove all None values, as we do not wish to override any FalconPy defaults
            for k in list(auth_keys.keys()):
                if auth_keys[k] is None:
                    del auth_keys[k]

            if not user_agent:
                user_agent = user_agent_string()
            self.logger.debug("User agent: %s", user_agent)

            self.verbose = verbose
            self.logger.debug("Verbose mode: %s", verbose)

            base_url = confirm_base_region(confirm_base_url(provided_base=cloud_name))
            self.logger.info("Base URL: %s", base_url)

            self.logger.debug("Configuring api_authentication object as an OAuth2 object")
            self.api_authentication = OAuth2(**auth_keys)
        elif falconpy_authobject:
            self.logger.info(
                "Using pre-created FalconPy OAuth2 object. All other options will be ignored"
            )
            self.api_authentication = falconpy_authobject
        else:
            raise Exception("Impossible authentication scenario")
        self.api_authentication.token()  # Need to force the authentication to resolve the base_url
        self.logger.info("Resolved Base URL: %s", self.api_authentication.base_url)
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
