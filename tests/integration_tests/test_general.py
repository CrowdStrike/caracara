"""
Caracara general tests
"""
import os

from falconpy import BaseURL

from caracara import (
    __version__,
    Client,
)

AUTH = Client(
    client_id=os.getenv("FALCON_CLIENT_ID"),
    client_secret=os.getenv("FALCON_CLIENT_SECRET"),
    cloud_name="auto",
)


def test_version():
    """Assert that the reflective version loading code works"""
    assert __version__ == '0.1.2'


def cloud_validation_testing():
    """
    Validates whether Caracara correctly interfaces with FalconPy to communicate
    with the Falcon API endpoints across multiple clouds"""
    correct_cloud_data = [
        "US1",
        "eu1",
        "https://api.crowdstrike.com",
        "api.laggar.gcw.crowdstrike.com",
    ]
    incorrect_cloud_data = [
        "US3",
        "http://api.crowdstrike.com",
        "api.us-2.crowdstrike.co",
        "https://eu-1.crowdstrike.com",
    ]
    test_results = []
    for check in correct_cloud_data:
        passed = False
        check = check.replace("https://", "")
        for base in BaseURL:
            if check.lower() == base.name.lower() or check.lower() == base.value.lower():
                passed = True
        test_results.append(passed)

    for check in incorrect_cloud_data:
        passed = True
        check = check.replace("https://", "")
        for base in BaseURL:
            if check.lower() == base.name.lower() or check.lower() == base.value.lower():
                passed = False
        test_results.append(passed)

    return min(test_results)


def test_cloud_validation():
    """Validates whether FalconPy could connect to the Falcon cloud"""
    assert cloud_validation_testing() is True


def test_creation():
    """Validates whether Caracara correctly handles authentication data"""
    assert AUTH.api_authentication.authenticated() is True
