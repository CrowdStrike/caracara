r"""Caracara base API interface client.

CrowdStrike Caracara
    _______ __ __             __
   |   _   |  |__.-----.-----|  |_
   |.  1___|  |  |  -__|     |   _|
   |.  |___|__|__|_____|__|__|____|
   |:  1   |
   |::.. . |     for FalconPy
   `-------'
"""

import logging

try:
    from falconpy import OAuth2, confirm_base_region, confirm_base_url
except ImportError as no_falconpy:
    raise SystemExit("The crowdstrike-falconpy library is not installed.") from no_falconpy

from caracara_filters import FQLGenerator

from caracara.common.interpolation import VariableInterpolator
from caracara.common.meta import user_agent_string
from caracara.common.module import ModuleMapper
from caracara.modules import (
    CustomIoaApiModule,
    FlightControlApiModule,
    HostsApiModule,
    PreventionPoliciesApiModule,
    ResponsePoliciesApiModule,
    RTRApiModule,
    SensorDownloadApiModule,
    SensorUpdatePoliciesApiModule,
    UsersApiModule,
)


class Client:
    """Falcon API client.

    This class exposes all available Falcon API commands, and proxies requests through
    the FalconPy library.
    """

    class FalconFilter(FQLGenerator):
        """Falcon Filter wrapper class.

        FalconFilter has now been replaced with the externally provided FQLGenerator functionality.
        This subclass allows pre-existing code to continue referencing FalconFilter.
        """

    def __init__(  # pylint: disable=R0913,R0914,R0915,R0917
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
        debug: bool = False,
        debug_record_count: int = None,
        sanitize_log: bool = True,
        falconpy_authobject: OAuth2 = None,
    ):
        """Configure a Caracara Falcon API Client object."""
        self.logger = logging.getLogger(__name__)

        if client_id is not None and client_secret is None:
            raise ValueError("You cannot provide a Client ID without a Client Secret")

        if client_id is not None and falconpy_authobject is not None:
            raise ValueError(
                "Please provide either a Client ID/Client Secret pair, "
                "or a pre-created FalconPy OAuth2 object, but not both"
            )

        self.logger.info("Setting up the Caracara client and configuring authentication")

        if falconpy_authobject:
            self.logger.info(
                "Using pre-created FalconPy OAuth2 object. All other options will be ignored"
            )
            self.api_authentication = falconpy_authobject

        else:
            # Load all parameters for the FalconPy authentication object into a dictionary
            # and handle environment variable interpolation
            interpolator = VariableInterpolator()
            cloud_name = interpolator.interpolate(cloud_name)
            client_id = interpolator.interpolate(client_id)
            client_secret = interpolator.interpolate(client_secret)
            member_cid = interpolator.interpolate(member_cid)
            user_agent = interpolator.interpolate(user_agent)
            proxy = interpolator.interpolate(proxy)
            user_agent = interpolator.interpolate(user_agent)

            if user_agent:
                user_agent = f"{user_agent} ({user_agent_string()})"
            else:
                user_agent = user_agent_string()

            self.logger.debug("User agent: %s", user_agent)

            auth_keys = {
                "base_url": cloud_name,
                "client_id": client_id,
                "client_secret": client_secret,
                "member_cid": member_cid,
                "proxy": proxy,
                "user_agent": user_agent,
                "ssl_verify": ssl_verify,
                "timeout": timeout,
                "debug": debug,
                "debug_record_count": debug_record_count,
                "sanitize_log": sanitize_log,
            }

            self.logger.info(
                "Client ID: %s; Cloud: %s; Member CID: %s",
                client_id,
                cloud_name,
                member_cid,
            )
            self.logger.debug("SSL verification is %s", ssl_verify)
            self.logger.debug("Timeout: %s", str(timeout))
            self.logger.debug("Configured proxy: %s", proxy)

            # Remove all None values, as we do not wish to override any FalconPy defaults
            for k in list(auth_keys.keys()):
                if auth_keys[k] is None:
                    del auth_keys[k]

            self.verbose = verbose
            self.logger.debug("Verbose mode: %s", verbose)

            base_url = confirm_base_region(confirm_base_url(provided_base=cloud_name))
            self.logger.info("Base URL: %s", base_url)

            self.logger.debug("Configuring api_authentication object as an OAuth2 object")
            self.api_authentication = OAuth2(**auth_keys)

        self.logger.info("Requesting API token")
        self.api_authentication.token()  # Need to force the authentication to resolve the base_url
        self.logger.info("Resolved Base URL: %s", self.api_authentication.base_url)

        mapper = ModuleMapper()

        # Configure modules here so that IDEs can pick them up
        self.logger.debug("Setting up Custom IOA module")
        self.custom_ioas = CustomIoaApiModule(self.api_authentication, mapper)
        mapper.custom_ioas = self.custom_ioas

        self.logger.debug("Setting up the Flight Control module")
        self.flight_control = FlightControlApiModule(self.api_authentication, mapper)
        mapper.flight_control = self.flight_control

        self.logger.debug("Setting up the Hosts module")
        self.hosts = HostsApiModule(self.api_authentication, mapper)
        mapper.hosts = self.hosts

        self.logger.debug("Setting up the Prevention Policies module")
        self.prevention_policies = PreventionPoliciesApiModule(self.api_authentication, mapper)
        mapper.prevention_policies = self.prevention_policies

        self.logger.debug("Setting up the Response Policies module")
        self.response_policies = ResponsePoliciesApiModule(self.api_authentication, mapper)
        mapper.response_policies = self.response_policies

        self.logger.debug("Setting up the RTR module")
        self.rtr = RTRApiModule(self.api_authentication, mapper)
        mapper.rtr = self.rtr

        self.logger.debug("Setting up the Sensor Download module")
        self.sensor_download = SensorDownloadApiModule(self.api_authentication, mapper)
        mapper.sensor_download = self.sensor_download

        self.logger.debug("Setting up the Sensor Update Policies module")
        self.sensor_update_policies = SensorUpdatePoliciesApiModule(self.api_authentication, mapper)
        mapper.sensor_update_policies = self.sensor_update_policies

        self.logger.debug("Setting up the Users module")
        self.users = UsersApiModule(self.api_authentication, mapper)
        mapper.users = self.users

        self.logger.info("Caracara client configured")

    def __enter__(self):
        """Allow for entry as a context manager."""
        self.logger.debug("Entering Caracara context manager")
        return self

    def __exit__(self, *args):
        """Discard our token when we exit the context."""
        self.logger.info("Discarding API token on Client exit")
        self.api_authentication.revoke(self.api_authentication.token_value)
        self.logger.debug("Discarding Caracara context manager")
        return args
