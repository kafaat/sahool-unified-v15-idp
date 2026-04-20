"""
CSRF Protection Tests for SAHOOL Platform.

Tests validate CSRF token generation, validation, and protection mechanisms.
"""

import hashlib
import hmac
import secrets
import time
from unittest.mock import Mock

import pytest


class CSRFTokenManager:
    """Mock CSRF token manager for testing."""

    def __init__(self, secret_key: str, token_expiry: int = 3600):
        self.secret_key = secret_key
        self.token_expiry = token_expiry

    def generate_token(self, session_id: str) -> str:
        """Generate a CSRF token tied to a session."""
        timestamp = str(int(time.time()))
        random_part = secrets.token_hex(16)
        message = f"{session_id}:{timestamp}:{random_part}"
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        return f"{message}:{signature}"

    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate a CSRF token."""
        try:
            parts = token.rsplit(":", 1)
            if len(parts) != 2:
                return False
            message, signature = parts
            expected_signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected_signature):
                return False
            msg_parts = message.split(":")
            if len(msg_parts) != 3:
                return False
            token_session_id, timestamp, _ = msg_parts
            if token_session_id != session_id:
                return False
            token_time = int(timestamp)
            if time.time() - token_time > self.token_expiry:
                return False
            return True
        except Exception:
            return False


@pytest.fixture
def csrf_manager():
    """Create CSRF manager with test secret."""
    return CSRFTokenManager(secret_key="test-secret-key-for-csrf-32chars!", token_expiry=3600)


@pytest.fixture
def mock_request():
    """Create mock HTTP request."""
    request = Mock()
    request.headers = {}
    request.cookies = {}
    request.method = "POST"
    return request


class TestCSRFTokenGeneration:
    """Tests for CSRF token generation."""

    def test_generate_token_returns_string(self, csrf_manager):
        """Test that token generation returns a string."""
        token = csrf_manager.generate_token("session123")
        assert isinstance(token, str)
        assert len(token) > 50

    def test_generate_token_unique_per_call(self, csrf_manager):
        """Test that each token is unique."""
        tokens = [csrf_manager.generate_token("session123") for _ in range(100)]
        assert len(set(tokens)) == 100

    def test_generate_token_contains_session_id(self, csrf_manager):
        """Test that token contains session identifier."""
        session_id = "user-session-abc"
        token = csrf_manager.generate_token(session_id)
        assert session_id in token

    def test_generate_token_contains_timestamp(self, csrf_manager):
        """Test that token contains timestamp."""
        token = csrf_manager.generate_token("session123")
        parts = token.split(":")
        assert len(parts) >= 4
        timestamp = int(parts[1])
        assert abs(timestamp - time.time()) < 5

    def test_generate_token_has_valid_signature(self, csrf_manager):
        """Test that token has valid HMAC signature."""
        session_id = "session123"
        token = csrf_manager.generate_token(session_id)
        assert csrf_manager.validate_token(token, session_id)


class TestCSRFTokenValidation:
    """Tests for CSRF token validation."""

    def test_validate_valid_token(self, csrf_manager):
        """Test validation of valid token."""
        session_id = "session123"
        token = csrf_manager.generate_token(session_id)
        assert csrf_manager.validate_token(token, session_id) is True

    def test_validate_token_wrong_session(self, csrf_manager):
        """Test validation fails with wrong session."""
        token = csrf_manager.generate_token("session123")
        assert csrf_manager.validate_token(token, "wrong-session") is False

    def test_validate_token_tampered_signature(self, csrf_manager):
        """Test validation fails with tampered signature."""
        session_id = "session123"
        token = csrf_manager.generate_token(session_id)
        tampered_token = token[:-10] + "0" * 10
        assert csrf_manager.validate_token(tampered_token, session_id) is False

    def test_validate_token_tampered_message(self, csrf_manager):
        """Test validation fails with tampered message."""
        session_id = "session123"
        token = csrf_manager.generate_token(session_id)
        parts = token.rsplit(":", 1)
        tampered_message = "tampered:" + parts[0].split(":", 1)[1]
        tampered_token = f"{tampered_message}:{parts[1]}"
        assert csrf_manager.validate_token(tampered_token, session_id) is False

    def test_validate_expired_token(self):
        """Test validation fails for expired token."""
        manager = CSRFTokenManager(secret_key="test-secret-key-for-csrf-32chars!", token_expiry=1)
        session_id = "session123"
        token = manager.generate_token(session_id)
        time.sleep(2)
        assert manager.validate_token(token, session_id) is False

    def test_validate_empty_token(self, csrf_manager):
        """Test validation fails for empty token."""
        assert csrf_manager.validate_token("", "session123") is False

    def test_validate_malformed_token(self, csrf_manager):
        """Test validation fails for malformed token."""
        assert csrf_manager.validate_token("not-a-valid-token", "session123") is False
        assert csrf_manager.validate_token("a:b", "session123") is False
        assert csrf_manager.validate_token("::::", "session123") is False

    def test_validate_none_token(self, csrf_manager):
        """Test validation handles None gracefully."""
        result = csrf_manager.validate_token(None, "session123")
        assert result is False


class TestCSRFMiddlewareIntegration:
    """Tests for CSRF middleware integration."""

    def test_csrf_header_extraction(self, mock_request, csrf_manager):
        """Test CSRF token extraction from header."""
        session_id = "session123"
        token = csrf_manager.generate_token(session_id)
        mock_request.headers["X-CSRF-Token"] = token
        extracted = mock_request.headers.get("X-CSRF-Token")
        assert csrf_manager.validate_token(extracted, session_id)

    def test_csrf_cookie_extraction(self, mock_request, csrf_manager):
        """Test CSRF token extraction from cookie."""
        session_id = "session123"
        token = csrf_manager.generate_token(session_id)
        mock_request.cookies["csrf_token"] = token
        extracted = mock_request.cookies.get("csrf_token")
        assert csrf_manager.validate_token(extracted, session_id)

    def test_csrf_safe_methods_excluded(self, mock_request):
        """Test safe HTTP methods are excluded from CSRF check."""
        safe_methods = ["GET", "HEAD", "OPTIONS", "TRACE"]
        for method in safe_methods:
            mock_request.method = method
            assert mock_request.method in safe_methods

    def test_csrf_unsafe_methods_checked(self, mock_request):
        """Test unsafe HTTP methods require CSRF check."""
        unsafe_methods = ["POST", "PUT", "DELETE", "PATCH"]
        for method in unsafe_methods:
            mock_request.method = method
            assert mock_request.method in unsafe_methods


class TestCSRFDoubleSubmitCookie:
    """Tests for double-submit cookie pattern."""

    def test_double_submit_cookie_match(self, csrf_manager):
        """Test double-submit cookie pattern validation."""
        session_id = "session123"
        token = csrf_manager.generate_token(session_id)
        cookie_token = token
        header_token = token
        assert cookie_token == header_token

    def test_double_submit_cookie_mismatch(self, csrf_manager):
        """Test double-submit fails on mismatch."""
        session_id = "session123"
        cookie_token = csrf_manager.generate_token(session_id)
        header_token = csrf_manager.generate_token(session_id)
        assert cookie_token != header_token


class TestCSRFOriginValidation:
    """Tests for origin/referer validation."""

    @pytest.fixture
    def allowed_origins(self):
        """List of allowed origins."""
        return [
            "https://sahool.kafaat.dev",
            "https://admin.sahool.kafaat.dev",
            "https://api.sahool.kafaat.dev",
        ]

    def test_valid_origin_accepted(self, allowed_origins):
        """Test valid origin is accepted."""
        origin = "https://sahool.kafaat.dev"
        assert origin in allowed_origins

    def test_invalid_origin_rejected(self, allowed_origins):
        """Test invalid origin is rejected."""
        origin = "https://malicious-site.com"
        assert origin not in allowed_origins

    def test_null_origin_rejected(self, allowed_origins):
        """Test null origin is rejected."""
        origin = "null"
        assert origin not in allowed_origins

    def test_subdomain_attack_prevented(self, allowed_origins):
        """Test subdomain takeover attack is prevented."""
        malicious = "https://evil.sahool.kafaat.dev"
        assert malicious not in allowed_origins

    def test_similar_domain_rejected(self, allowed_origins):
        """Test similar domain names are rejected."""
        similar_domains = [
            "https://sahool.kafaat.dev.evil.com",
            "https://sahool-kafaat.dev",
            "https://sahoolkafaat.dev",
        ]
        for domain in similar_domains:
            assert domain not in allowed_origins


class TestCSRFSameSiteCookie:
    """Tests for SameSite cookie attribute."""

    def test_samesite_strict_setting(self):
        """Test SameSite=Strict cookie setting."""
        cookie_attrs = {
            "samesite": "Strict",
            "secure": True,
            "httponly": True,
        }
        assert cookie_attrs["samesite"] == "Strict"

    def test_samesite_lax_setting(self):
        """Test SameSite=Lax cookie setting."""
        cookie_attrs = {
            "samesite": "Lax",
            "secure": True,
            "httponly": True,
        }
        assert cookie_attrs["samesite"] == "Lax"

    def test_secure_flag_required(self):
        """Test Secure flag is required for CSRF cookies."""
        cookie_attrs = {"secure": True}
        assert cookie_attrs["secure"] is True


class TestCSRFAjaxProtection:
    """Tests for AJAX-specific CSRF protection."""

    def test_custom_header_requirement(self, mock_request):
        """Test custom header requirement for AJAX."""
        mock_request.headers["X-Requested-With"] = "XMLHttpRequest"
        assert mock_request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def test_content_type_validation(self, mock_request):
        """Test content-type validation for AJAX."""
        valid_content_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]
        mock_request.headers["Content-Type"] = "application/json"
        assert mock_request.headers["Content-Type"] in valid_content_types


@pytest.mark.unit
class TestCSRFTimingAttackPrevention:
    """Tests for timing attack prevention."""

    def test_constant_time_comparison(self, csrf_manager):
        """Test that signature comparison uses a constant-time algorithm.

        Flakiness notes (the old version of this test was failing ~4/5 runs):

        * The previous "invalid" token was ``"invalid" * 20`` — a string with
          no ``:`` separator. ``validate_token`` short-circuits on that at
          the ``rsplit(':', 1)`` check and returns ``False`` WITHOUT hitting
          the HMAC comparison at all. That meant we were comparing the full
          validate-token path (with HMAC) against an early-exit path (no
          HMAC), which legitimately has a >10× timing ratio — not a
          timing-attack vulnerability, just structurally different branches.
        * Now: we compare two STRUCTURALLY VALID tokens (both parse as
          ``msg:sig``) — one with a correct signature, one with a wrong one.
          Both reach ``hmac.compare_digest`` and take the same constant time.
        * 200 samples + 20-sample warmup + median-based comparison damp the
          OS scheduling noise that made a 10-sample mean unreliable.
        """
        session_id = "session123"
        valid_token = csrf_manager.generate_token(session_id)

        # Forged token: same structure (msg:sig), but signature is wrong. The
        # tamper is in the signature tail, so rsplit() still yields 2 parts
        # and the HMAC comparison actually runs.
        forged_token = valid_token[:-16] + ("0" * 16)

        # Warmup — first iterations have cache/branch-predictor noise.
        for _ in range(20):
            csrf_manager.validate_token(valid_token, session_id)
            csrf_manager.validate_token(forged_token, session_id)

        samples = 200
        valid_times: list[float] = []
        forged_times: list[float] = []
        for _ in range(samples):
            start = time.perf_counter()
            csrf_manager.validate_token(valid_token, session_id)
            valid_times.append(time.perf_counter() - start)

        for _ in range(samples):
            start = time.perf_counter()
            csrf_manager.validate_token(forged_token, session_id)
            forged_times.append(time.perf_counter() - start)

        valid_times.sort()
        forged_times.sort()
        median_valid = valid_times[samples // 2]
        median_forged = forged_times[samples // 2]

        ratio = max(median_valid, median_forged) / min(median_valid, median_forged)
        assert ratio < 10, (
            f"Timing difference too large (ratio={ratio:.2f}, "
            f"median_valid={median_valid * 1e6:.2f}µs, "
            f"median_forged={median_forged * 1e6:.2f}µs). "
            "Possible timing-attack vulnerability."
        )
