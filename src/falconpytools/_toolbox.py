"""Generic toolbox"""
try:
    from falconpy.oauth2 import OAuth2
except ImportError as no_falconpy:
    raise SystemExit(
        "CrowdStrike FalconPy must be installed in order to use this application.\n"
        "Please execute `python3 -m pip install crowdstrike-falconpy` and try again."
        ) from no_falconpy


class Toolbox():
    """Generic Toolbox base class"""
    def __init__(self, key: str = None, secret: str = None, api: object = None, verbose: bool = True):
        """Opens the toolbox"""
        if api:
            self.api = api
        else:
            # Error handling, yo
            self.api = OAuth2(client_id=key, client_secret=secret)
        self.verbose = verbose

    def display(self, message):
        """Provides informational updates"""
        if self.verbose:
            print("%-80s" % message, end="\r", flush=True)

    def close(self):
        """Revokes the token and destroys the API object"""
        self.api.deauthenticate()
        self.api = None
