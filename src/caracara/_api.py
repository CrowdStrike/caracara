"""Generic API interface."""
from ._error import MissingFalconPy

try:
    from falconpy import OAuth2, APIHarness
except ImportError as no_falconpy:
    raise MissingFalconPy from no_falconpy


class ToolboxAPI():
    """Base class to represent the Falcon API."""

    def __init__(self, auth_object: object = None, **kwargs):
        """Initialize an instance of the base class, creating the authorization object.

        :str    key         - API client ID to use for authentication.
        :str    secret      - API client secret to use for authentication.
        :str    base        - Base URL to use for API requests.
        :bool   use_ssl     - Enable / disable SSL verification. Defaults to enabled.
        :float  timeout     - Total time in seconds for API requests before timeout.
        :tuple  timeout     - Connect / Read time in seconds for API requests before timeout.
        :dict   proxy       - List of proxies to use for requests made to the API.
        :object auth_object - Pre-initialized FalconPy OAuth2 authentication object.
        """
        def _service_interface(authorization: object = None, **kwargs):
            """Return a newly created instance of the authorization class if it is not provided."""
            if not authorization:
                current = kwargs.get("session", None)
                authorization = OAuth2(creds=current.creds,
                                       base_url=current.base,
                                       ssl_verify=current.use_ssl,
                                       timeout=current.timeout,
                                       proxy=current.proxy
                                       )
            return authorization

        def _generic_interface(authorization: object = None, **kwargs):
            """Return a newly created instance of the generic class."""
            if not authorization:
                current = kwargs.get("session", None)
                uber = APIHarness(creds=current.creds,
                                  base_url=current.base,
                                  ssl_verify=current.use_ssl,
                                  timeout=current.timeout,
                                  proxy=current.proxy
                                  )
            else:
                uber = APIHarness(creds=authorization.creds,
                                  base_url=authorization.base_url,
                                  ssl_verify=authorization.ssl_verify,
                                  timeout=authorization.timeout,
                                  proxy=authorization.proxy
                                  )
            return uber

        self.auth = _service_interface(auth_object, **kwargs)
        self.generic = _generic_interface(auth_object, **kwargs)
        self.command = self.generic.command

    def authenticated(self):
        """Return the authentication status from the auth object."""
        return self.auth.authenticated()

    def deauthenticate(self):
        """Deauthenticate from the API."""
        self.auth.revoke(self.auth.token_value)
