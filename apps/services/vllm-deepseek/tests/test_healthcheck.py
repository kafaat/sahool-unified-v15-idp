"""
Tests for vllm-deepseek healthcheck.py.

All tests are fully offline — HTTP calls are mocked.
"""

from __future__ import annotations

import os
import sys
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

# Make sure the service root is importable
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)


# ---------------------------------------------------------------------------
# check() function tests
# ---------------------------------------------------------------------------


def test_check_returns_true_on_200():
    """check() returns True when the server responds HTTP 200."""
    import healthcheck

    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.status = 200

    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert healthcheck.check(port=8270, timeout=5) is True


def test_check_returns_false_on_non_200():
    """check() returns False when the server responds with a non-200 status."""
    import healthcheck

    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.status = 503

    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert healthcheck.check(port=8270, timeout=5) is False


def test_check_returns_false_on_connection_error():
    """check() returns False when the server is unreachable."""
    import healthcheck

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
        assert healthcheck.check(port=8270, timeout=5) is False


def test_check_returns_false_on_os_error():
    """check() returns False on generic OSError (e.g., timeout)."""
    import healthcheck

    with patch("urllib.request.urlopen", side_effect=OSError("timed out")):
        assert healthcheck.check(port=8270, timeout=5) is False


# ---------------------------------------------------------------------------
# main() exit-code tests
# ---------------------------------------------------------------------------


def test_main_exits_0_when_healthy():
    """main() must sys.exit(0) when the server is healthy."""
    import healthcheck

    with patch.object(healthcheck, "check", return_value=True), patch("sys.argv", ["healthcheck.py"]):
        with pytest.raises(SystemExit) as exc_info:
            healthcheck.main()
    assert exc_info.value.code == 0


def test_main_exits_1_when_unhealthy():
    """main() must sys.exit(1) when the server is unhealthy."""
    import healthcheck

    with patch.object(healthcheck, "check", return_value=False), patch("sys.argv", ["healthcheck.py"]):
        with pytest.raises(SystemExit) as exc_info:
            healthcheck.main()
    assert exc_info.value.code == 1


def test_check_uses_correct_url():
    """check() must probe the /health path on the configured port."""
    import healthcheck

    captured_url = []

    def fake_urlopen(url, timeout):
        captured_url.append(url)
        raise urllib.error.URLError("closed")

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        healthcheck.check(port=9999, timeout=2)

    assert captured_url[0] == "http://localhost:9999/health"
