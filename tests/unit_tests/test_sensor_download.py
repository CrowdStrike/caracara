"""Unit tests for SensorDownloadApiModule."""

import hashlib
import os
from unittest.mock import MagicMock, patch

import falconpy
import pytest

from caracara import Client
from caracara.common.exceptions import GenericAPIError

# pylint: disable=unused-argument, redefined-builtin

# Real content bytes and their SHA256 hashes, used for download integrity checks.
MOCK_CONTENT_LINUX = b"fake linux installer bytes"
MOCK_CONTENT_WINDOWS = b"fake windows lts installer bytes"
MOCK_SHA256 = hashlib.sha256(MOCK_CONTENT_LINUX).hexdigest()
MOCK_SHA256_LTS = hashlib.sha256(MOCK_CONTENT_WINDOWS).hexdigest()

mock_installer_linux = {
    "description": "Falcon sensor for Linux",
    "file_size": len(MOCK_CONTENT_LINUX),
    "file_type": "rpm",
    "name": "falcon-sensor-7.15.0-17206.x86_64.rpm",
    "os": "RHEL",
    "os_version": "8",
    "platform": "Linux",
    "release_date": "2024-01-15T00:00:00Z",
    "sha256": MOCK_SHA256,
    "version": "7.15.0",
    "architectures": ["x86_64"],
    "ltv_expiry_date": None,
    "ltv_promoted_date": None,
    "is_lts": False,
    "lts_expiry_date": None,
}

mock_installer_windows_lts = {
    "description": "Falcon sensor for Windows (LTS)",
    "file_size": len(MOCK_CONTENT_WINDOWS),
    "file_type": "exe",
    "name": "WindowsSensor.exe",
    "os": "Windows",
    "os_version": "10",
    "platform": "Windows",
    "release_date": "2024-01-01T00:00:00Z",
    "sha256": MOCK_SHA256_LTS,
    "version": "7.14.0",
    "architectures": ["x86_64"],
    "ltv_expiry_date": None,
    "ltv_promoted_date": None,
    "is_lts": True,
    "lts_expiry_date": "2025-01-01T00:00:00Z",
}

mock_installers = [mock_installer_linux, mock_installer_windows_lts]


def _make_stream_mock(content: bytes) -> MagicMock:
    """Return a mock requests.Response that streams the provided bytes."""
    mock = MagicMock()
    mock.iter_content.return_value = [content]
    return mock


def sensor_download_test():
    """Decorator with common setup for all sensor download tests."""

    def decorator(func):
        @patch(
            "caracara.modules.sensor_download.sensor_download.SensorDownload",
            autospec=falconpy.SensorDownload,
        )
        @patch("caracara.client.OAuth2", autospec=True)
        def test_new_func(mock_oauth2, mock_sensor_download, tmp_path):
            auth = Client(  # nosec B106:hardcoded_password_funcarg
                client_id="testing id",
                client_secret="testing secret",
                cloud_name="auto",
            )
            return func(auth=auth, mock_sensor_download=mock_sensor_download, tmp_path=tmp_path)

        return test_new_func

    return decorator


def mock_get_combined_installers_v3(
    filter, sort, offset, limit
):  # pylint: disable=redefined-builtin
    """Return a paginated mock response for get_combined_sensor_installers_by_query_v3."""
    return {
        "body": {
            "resources": mock_installers[offset : offset + limit],
            "meta": {
                "pagination": {
                    "total": len(mock_installers),
                    "offset": offset,
                    "limit": limit,
                },
            },
            "errors": [],
        },
        "status_code": 200,
    }


def mock_get_installer_ids(filter, sort, offset, limit):  # pylint: disable=redefined-builtin
    """Return a paginated mock response for get_sensor_installers_by_query_v3."""
    all_ids = [i["sha256"] for i in mock_installers]
    return {
        "body": {
            "resources": all_ids[offset : offset + limit],
            "meta": {
                "pagination": {
                    "total": len(all_ids),
                    "offset": offset,
                    "limit": limit,
                },
            },
            "errors": [],
        },
        "status_code": 200,
    }


def mock_get_installer_entities_v3(ids):
    """Return a mock response for get_sensor_installer_entities_v3 by SHA256."""
    sha256 = ids if isinstance(ids, str) else ids[0]
    for installer in mock_installers:
        if installer["sha256"] == sha256:
            return {"body": {"resources": [installer], "errors": []}, "status_code": 200}
    return {"body": {"resources": [], "errors": []}, "status_code": 200}


def mock_download_stream(id, stream):  # pylint: disable=redefined-builtin
    """Return a mock streaming response whose bytes hash to the expected SHA256."""
    content_map = {
        MOCK_SHA256: MOCK_CONTENT_LINUX,
        MOCK_SHA256_LTS: MOCK_CONTENT_WINDOWS,
    }
    if id not in content_map:
        return {"status_code": 404, "body": {"errors": [{"code": 404, "message": "Not found"}]}}
    return _make_stream_mock(content_map[id])


@sensor_download_test()
def test_describe_installers(auth: Client, mock_sensor_download, **_):
    """describe_installers returns a list of all installer metadata dicts."""
    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_combined_sensor_installers_by_query_v3.side_effect": (
                mock_get_combined_installers_v3
            ),
        }
    )

    result = auth.sensor_download.describe_installers()

    assert len(result) == len(mock_installers)
    assert result[0]["name"] == mock_installer_linux["name"]
    assert result[1]["name"] == mock_installer_windows_lts["name"]


@sensor_download_test()
def test_describe_installers_with_filter_string(auth: Client, mock_sensor_download, **_):
    """describe_installers accepts a raw FQL filter string."""
    captured = {}

    def capture_filter(filter, sort, offset, limit):  # pylint: disable=redefined-builtin
        captured["filter"] = filter
        return mock_get_combined_installers_v3(filter, sort, offset, limit)

    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_combined_sensor_installers_by_query_v3.side_effect": capture_filter,
        }
    )

    auth.sensor_download.describe_installers(filters="platform:'Linux'")

    assert captured["filter"] == "platform:'Linux'"


@sensor_download_test()
def test_describe_installers_with_falcon_filter(auth: Client, mock_sensor_download, **_):
    """describe_installers converts a FalconFilter object to an FQL string."""
    captured = {}

    def capture_filter(filter, sort, offset, limit):  # pylint: disable=redefined-builtin
        captured["filter"] = filter
        return mock_get_combined_installers_v3(filter, sort, offset, limit)

    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_combined_sensor_installers_by_query_v3.side_effect": capture_filter,
        }
    )

    falcon_filter = auth.FalconFilter(dialect="sensor_download")
    falcon_filter.create_new_filter("platform", "Linux")

    auth.sensor_download.describe_installers(filters=falcon_filter)

    assert captured["filter"] == "platform: 'linux'"


@sensor_download_test()
def test_get_installer_ids(auth: Client, mock_sensor_download, **_):
    """get_installer_ids returns a list of SHA256 hashes."""
    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_sensor_installers_by_query_v3.side_effect": mock_get_installer_ids,
        }
    )

    result = auth.sensor_download.get_installer_ids()

    assert len(result) == len(mock_installers)
    assert MOCK_SHA256 in result
    assert MOCK_SHA256_LTS in result


@sensor_download_test()
def test_download_installer_uses_canonical_name(auth: Client, mock_sensor_download, tmp_path, **_):
    """download_installer looks up the canonical filename when none is provided."""
    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_sensor_installer_entities_v3.side_effect": mock_get_installer_entities_v3,
            "download_sensor_installer_v2.side_effect": mock_download_stream,
        }
    )

    result = auth.sensor_download.download_installer(
        sha256=MOCK_SHA256,
        destination_path=str(tmp_path),
        show_progress=False,
    )

    assert result == os.path.join(str(tmp_path), mock_installer_linux["name"])
    auth.sensor_download.sensor_download_api.download_sensor_installer_v2.assert_called_once_with(
        id=MOCK_SHA256,
        stream=True,
    )
    assert os.path.exists(result)


@sensor_download_test()
def test_download_installer_with_custom_filename(auth: Client, mock_sensor_download, tmp_path, **_):
    """download_installer uses the caller-provided filename and skips the metadata call."""
    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "download_sensor_installer_v2.side_effect": mock_download_stream,
        }
    )

    result = auth.sensor_download.download_installer(
        sha256=MOCK_SHA256,
        destination_path=str(tmp_path),
        filename="my-sensor.rpm",
        show_progress=False,
    )

    assert result == os.path.join(str(tmp_path), "my-sensor.rpm")
    # No metadata lookup should occur when a filename is provided
    auth.sensor_download.sensor_download_api.get_sensor_installer_entities_v3.assert_not_called()
    assert os.path.exists(result)


@sensor_download_test()
def test_download_installer_raises_on_api_error(auth: Client, mock_sensor_download, tmp_path, **_):
    """download_installer raises GenericAPIError when the API returns a 4xx status."""
    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_sensor_installer_entities_v3.side_effect": mock_get_installer_entities_v3,
            "download_sensor_installer_v2.return_value": {
                "status_code": 404,
                "body": {
                    "errors": [{"code": 404, "message": "Installer not found"}],
                },
            },
        }
    )

    with pytest.raises(GenericAPIError):
        auth.sensor_download.download_installer(
            sha256=MOCK_SHA256,
            destination_path=str(tmp_path),
        )


@sensor_download_test()
def test_download_installer_raises_on_sha256_mismatch(
    auth: Client, mock_sensor_download, tmp_path, **_
):
    """download_installer raises ValueError and cleans up when SHA256 does not match."""
    corrupt_stream = _make_stream_mock(b"this is not the right content")

    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_sensor_installer_entities_v3.side_effect": mock_get_installer_entities_v3,
            "download_sensor_installer_v2.return_value": corrupt_stream,
        }
    )

    with pytest.raises(ValueError, match="SHA256 mismatch"):
        auth.sensor_download.download_installer(
            sha256=MOCK_SHA256,
            destination_path=str(tmp_path),
            show_progress=False,
        )

    # Partial file must be deleted on mismatch
    assert not os.path.exists(os.path.join(str(tmp_path), mock_installer_linux["name"]))


@sensor_download_test()
def test_download_installer_include_version(auth: Client, mock_sensor_download, tmp_path, **_):
    """download_installer embeds the version in the filename when include_version=True."""
    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_sensor_installer_entities_v3.side_effect": mock_get_installer_entities_v3,
            "download_sensor_installer_v2.side_effect": mock_download_stream,
        }
    )

    result = auth.sensor_download.download_installer(
        sha256=MOCK_SHA256,
        destination_path=str(tmp_path),
        include_version=True,
        show_progress=False,
    )

    version = mock_installer_linux["version"]
    stem, ext = os.path.splitext(mock_installer_linux["name"])
    expected_name = f"{stem}-{version}{ext}"
    assert result == os.path.join(str(tmp_path), expected_name)
    assert os.path.exists(result)


@sensor_download_test()
def test_download_installer_file_exists_error(auth: Client, mock_sensor_download, tmp_path, **_):
    """download_installer raises FileExistsError when the destination file already exists."""
    existing = tmp_path / mock_installer_linux["name"]
    existing.write_bytes(b"old content")

    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_sensor_installer_entities_v3.side_effect": mock_get_installer_entities_v3,
        }
    )

    with pytest.raises(FileExistsError):
        auth.sensor_download.download_installer(
            sha256=MOCK_SHA256,
            destination_path=str(tmp_path),
            show_progress=False,
        )

    # Existing file must be untouched
    assert existing.read_bytes() == b"old content"
    auth.sensor_download.sensor_download_api.download_sensor_installer_v2.assert_not_called()


@sensor_download_test()
def test_download_installer_file_exists_skip(auth: Client, mock_sensor_download, tmp_path, **_):
    """download_installer returns the existing path without downloading when if_exists='skip'."""
    existing = tmp_path / mock_installer_linux["name"]
    existing.write_bytes(b"old content")

    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_sensor_installer_entities_v3.side_effect": mock_get_installer_entities_v3,
        }
    )

    result = auth.sensor_download.download_installer(
        sha256=MOCK_SHA256,
        destination_path=str(tmp_path),
        if_exists="skip",
        show_progress=False,
    )

    assert result == str(existing)
    assert existing.read_bytes() == b"old content"
    auth.sensor_download.sensor_download_api.download_sensor_installer_v2.assert_not_called()


@sensor_download_test()
def test_download_installer_file_exists_overwrite(
    auth: Client, mock_sensor_download, tmp_path, **_
):
    """download_installer replaces the existing file when if_exists='overwrite'."""
    existing = tmp_path / mock_installer_linux["name"]
    existing.write_bytes(b"old content")

    auth.sensor_download.sensor_download_api.configure_mock(
        **{
            "get_sensor_installer_entities_v3.side_effect": mock_get_installer_entities_v3,
            "download_sensor_installer_v2.side_effect": mock_download_stream,
        }
    )

    result = auth.sensor_download.download_installer(
        sha256=MOCK_SHA256,
        destination_path=str(tmp_path),
        if_exists="overwrite",
        show_progress=False,
    )

    assert result == str(existing)
    assert existing.read_bytes() == MOCK_CONTENT_LINUX
