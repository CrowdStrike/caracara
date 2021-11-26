"""Generic toolbox"""
try:
    from falconpy import OAuth2
except ImportError as no_falconpy:
    raise SystemExit(
        "CrowdStrike FalconPy must be installed in order to use this application.\n"
        "Please execute `python3 -m pip install crowdstrike-falconpy` and try again."
        ) from no_falconpy


class Toolbox():
    """Generic Toolbox base class"""
    def __init__(self, api: object = None, verbose: bool = True, **kwargs):
        """Opens the toolbox"""
        if api:
            self.api = api
        else:
            # Error handling
            self.api = OAuth2(client_id=kwargs.get("key", None),
                              client_secret=kwargs.get("secret", None),
                              base_url=kwargs.get("base", "us1"),
                              ssl_verify=kwargs.get("use_ssl", True),
                              timeout=kwargs.get("timeout", None),
                              proxy=kwargs.get("proxy", None)
                              )
        self.verbose = verbose
        self.indicator = ["⠧", "⠇", "⠏", "⠹", "⠸", "⠼"]
        self.position = 0

    def display(self, message):
        """Provides informational updates"""
        if self.verbose:
            msg = f" {self.next()} {message}"
            print("%-80s" % msg, end="\r", flush=True)  # pylint: disable=C0209  # May change this

    def close(self):
        """Revokes the token and destroys the API object"""
        self.api.deauthenticate()
        self.api = None

    def next(self):
        """Gets the next indicator and increments the position"""
        ind = self.indicator[self.position]
        self.position += 1
        if self.position >= (len(self.indicator) - 1):
            self.position = 0

        return ind
