"""Generic API interface"""
try:
    from falconpy.oauth2 import OAuth2
except ImportError as no_falconpy:
    raise SystemExit(
        "CrowdStrike FalconPy must be installed in order to use this application.\n"
        "Please execute `python3 -m pip install crowdstrike-falconpy` and try again."
        ) from no_falconpy


class ToolboxAPI():
    """
    Base class to represent the Falcon API.
    """
    def __init__(self, key: str = None, secret: str = None, auth_object: object = None):
        if auth_object:
            self.auth = auth_object
        else:
            self.auth = OAuth2(
                client_id=key,
                client_secret=secret,
                )

    def authenticated(self):
        """Returns the authentication status from the auth object"""
        return self.auth.authenticated()

    def deauthenticate(self):
        """Deauthenticates from the API"""
        self.auth.revoke(self.auth.token_value)
