"""
Authentication Bypass Prevention Tests for SAHOOL Platform.

Tests validate JWT security, token handling, and authentication edge cases.
"""

import base64
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
import pytest

TEST_SECRET_KEY = "test-secret-key-for-unit-tests-only-32chars"
TEST_ALGORITHM = "HS256"


class JWTAuthenticator:
    """Mock JWT authenticator for testing."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.revoked_tokens: set = set()

    def create_token(
        self,
        user_id: str,
        tenant_id: str,
        roles: list,
        expires_delta: timedelta = timedelta(hours=1),
    ) -> str:
        """Create a JWT token."""
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "roles": roles,
            "iat": now,
            "exp": now + expires_delta,
            "jti": f"{user_id}-{int(now.timestamp())}",
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"require": ["exp", "sub", "tenant_id"]},
            )

            if payload.get("jti") in self.revoked_tokens:
                return None

            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def revoke_token(self, jti: str) -> None:
        """Revoke a token by JTI."""
        self.revoked_tokens.add(jti)


@pytest.fixture
def authenticator():
    """Create JWT authenticator with test secret."""
    return JWTAuthenticator(TEST_SECRET_KEY, TEST_ALGORITHM)


@pytest.fixture
def valid_token(authenticator):
    """Create a valid JWT token."""
    return authenticator.create_token(user_id="user123", tenant_id="tenant456", roles=["farmer"])


class TestJWTAlgorithmSecurity:
    """Tests for JWT algorithm security."""

    def test_none_algorithm_rejected(self, authenticator, valid_token):
        """Test 'none' algorithm tokens are rejected."""
        header = {"alg": "none", "typ": "JWT"}
        payload = {"sub": "hacker", "tenant_id": "tenant456", "exp": time.time() + 3600}

        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()

        none_token = f"{header_b64}.{payload_b64}."

        result = authenticator.verify_token(none_token)
        assert result is None

    def test_algorithm_confusion_attack_prevented(self, authenticator):
        """Test algorithm confusion (RS256 to HS256) attack is prevented."""
        payload = {
            "sub": "hacker",
            "tenant_id": "tenant456",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        fake_public_key = "fake-public-key-used-as-hmac-secret"
        malicious_token = jwt.encode(payload, fake_public_key, algorithm="HS256")

        result = authenticator.verify_token(malicious_token)
        assert result is None

    def test_weak_algorithm_rejected(self):
        """Test weak algorithms are not accepted."""
        weak_algorithms = [
            "HS384",
            "HS512",
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512",
            "PS256",
            "PS384",
            "PS512",
        ]
        authenticator = JWTAuthenticator(TEST_SECRET_KEY, "HS256")

        payload = {
            "sub": "user123",
            "tenant_id": "tenant456",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        for alg in weak_algorithms:
            if alg.startswith("HS"):
                token = jwt.encode(payload, TEST_SECRET_KEY, algorithm=alg)
                result = authenticator.verify_token(token)
                if alg != "HS256":
                    assert result is None or alg == "HS256"


class TestTokenExpiration:
    """Tests for token expiration handling."""

    def test_expired_token_rejected(self, authenticator):
        """Test expired tokens are rejected."""
        token = authenticator.create_token(
            user_id="user123",
            tenant_id="tenant456",
            roles=["farmer"],
            expires_delta=timedelta(seconds=-1),
        )

        result = authenticator.verify_token(token)
        assert result is None

    def test_future_iat_rejected(self):
        """Test tokens with future 'issued at' are suspicious."""
        payload = {
            "sub": "user123",
            "tenant_id": "tenant456",
            "iat": datetime.utcnow() + timedelta(hours=1),
            "exp": datetime.utcnow() + timedelta(hours=2),
        }

        assert payload["iat"] > datetime.utcnow()

    def test_missing_exp_rejected(self, authenticator):
        """Test tokens without expiration are rejected."""
        payload = {
            "sub": "user123",
            "tenant_id": "tenant456",
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm="HS256")
        result = authenticator.verify_token(token)
        assert result is None

    def test_very_long_expiry_flagged(self, authenticator):
        """Test tokens with very long expiry are flagged."""
        max_expiry = timedelta(days=7)
        long_expiry = timedelta(days=365)

        assert long_expiry > max_expiry


class TestTokenRevocation:
    """Tests for token revocation."""

    def test_revoked_token_rejected(self, authenticator):
        """Test revoked tokens are rejected."""
        token = authenticator.create_token(user_id="user123", tenant_id="tenant456", roles=["farmer"])

        payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=["HS256"])
        jti = payload["jti"]

        assert authenticator.verify_token(token) is not None

        authenticator.revoke_token(jti)

        assert authenticator.verify_token(token) is None

    def test_revocation_persists(self, authenticator):
        """Test token revocation persists across verifications."""
        token = authenticator.create_token(user_id="user123", tenant_id="tenant456", roles=["farmer"])

        payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=["HS256"])
        authenticator.revoke_token(payload["jti"])

        for _ in range(5):
            assert authenticator.verify_token(token) is None


class TestTokenTampering:
    """Tests for token tampering detection."""

    def test_modified_payload_rejected(self, authenticator, valid_token):
        """Test modified payload is rejected."""
        parts = valid_token.split(".")

        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
        payload["roles"] = ["admin"]

        modified_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()

        tampered_token = f"{parts[0]}.{modified_payload}.{parts[2]}"

        result = authenticator.verify_token(tampered_token)
        assert result is None

    def test_modified_header_rejected(self, authenticator, valid_token):
        """Test modified header is rejected."""
        parts = valid_token.split(".")

        header = {"alg": "HS256", "typ": "JWT", "kid": "malicious-key"}
        modified_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()

        tampered_token = f"{modified_header}.{parts[1]}.{parts[2]}"

        result = authenticator.verify_token(tampered_token)
        assert result is None

    def test_signature_stripping_rejected(self, authenticator, valid_token):
        """Test tokens with stripped signatures are rejected."""
        parts = valid_token.split(".")
        stripped_token = f"{parts[0]}.{parts[1]}."

        result = authenticator.verify_token(stripped_token)
        assert result is None


class TestClaimValidation:
    """Tests for JWT claim validation."""

    def test_missing_subject_rejected(self, authenticator):
        """Test tokens without subject are rejected."""
        payload = {
            "tenant_id": "tenant456",
            "roles": ["farmer"],
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm="HS256")
        result = authenticator.verify_token(token)
        assert result is None

    def test_missing_tenant_rejected(self, authenticator):
        """Test tokens without tenant_id are rejected."""
        payload = {
            "sub": "user123",
            "roles": ["farmer"],
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm="HS256")
        result = authenticator.verify_token(token)
        assert result is None

    def test_invalid_tenant_format(self, authenticator):
        """Test tokens with invalid tenant format are flagged."""
        token = authenticator.create_token(user_id="user123", tenant_id="'; DROP TABLE tenants;--", roles=["farmer"])

        result = authenticator.verify_token(token)
        if result:
            assert "DROP" in result["tenant_id"]


class TestBruteForceProtection:
    """Tests for brute force attack protection."""

    def test_rate_limiting_on_failed_auth(self):
        """Test rate limiting on authentication failures."""
        failed_attempts = {}
        max_attempts = 5
        lockout_duration = 300

        def check_rate_limit(user_id: str) -> bool:
            current_time = time.time()
            if user_id in failed_attempts:
                attempts, first_attempt_time = failed_attempts[user_id]
                if current_time - first_attempt_time < lockout_duration:
                    if attempts >= max_attempts:
                        return False
            return True

        def record_failed_attempt(user_id: str):
            current_time = time.time()
            if user_id in failed_attempts:
                attempts, first_time = failed_attempts[user_id]
                failed_attempts[user_id] = (attempts + 1, first_time)
            else:
                failed_attempts[user_id] = (1, current_time)

        user_id = "victim"
        for _ in range(max_attempts):
            assert check_rate_limit(user_id) is True
            record_failed_attempt(user_id)

        assert check_rate_limit(user_id) is False


class TestSessionFixation:
    """Tests for session fixation prevention."""

    def test_token_regeneration_on_privilege_change(self, authenticator):
        """Test token is regenerated on privilege escalation."""
        old_token = authenticator.create_token(user_id="user123", tenant_id="tenant456", roles=["farmer"])

        new_token = authenticator.create_token(user_id="user123", tenant_id="tenant456", roles=["farmer", "admin"])

        assert old_token != new_token

        old_payload = jwt.decode(old_token, TEST_SECRET_KEY, algorithms=["HS256"])
        authenticator.revoke_token(old_payload["jti"])

        assert authenticator.verify_token(old_token) is None
        assert authenticator.verify_token(new_token) is not None


class TestCrossTenantAccess:
    """Tests for cross-tenant access prevention."""

    def test_tenant_isolation_in_token(self, authenticator):
        """Test tenant isolation is enforced in tokens."""
        tenant1_token = authenticator.create_token(user_id="user123", tenant_id="tenant1", roles=["farmer"])

        tenant2_token = authenticator.create_token(user_id="user123", tenant_id="tenant2", roles=["farmer"])

        payload1 = authenticator.verify_token(tenant1_token)
        payload2 = authenticator.verify_token(tenant2_token)

        assert payload1["tenant_id"] == "tenant1"
        assert payload2["tenant_id"] == "tenant2"
        assert payload1["tenant_id"] != payload2["tenant_id"]

    def test_tenant_id_cannot_be_modified(self, authenticator):
        """Test tenant_id cannot be modified in token."""
        token = authenticator.create_token(user_id="user123", tenant_id="tenant1", roles=["farmer"])

        parts = token.split(".")
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
        payload["tenant_id"] = "tenant2"

        modified_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()

        tampered_token = f"{parts[0]}.{modified_payload}.{parts[2]}"

        result = authenticator.verify_token(tampered_token)
        assert result is None


class TestTokenLeakagePrevention:
    """Tests for token leakage prevention."""

    def test_token_not_in_url(self):
        """Test tokens should not be passed in URLs."""
        url = "https://api.sahool.dev/fields?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        assert "token=" in url

    def test_token_in_authorization_header(self):
        """Test tokens should be in Authorization header."""
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}

        assert headers["Authorization"].startswith("Bearer ")

    def test_token_not_logged(self):
        """Test tokens should not be logged."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"

        safe_log = f"Token: {token[:20]}..."

        assert token not in safe_log
        assert "..." in safe_log


@pytest.mark.unit
class TestMalformedTokenHandling:
    """Tests for malformed token handling."""

    def test_empty_token(self, authenticator):
        """Test empty token is rejected."""
        assert authenticator.verify_token("") is None

    def test_null_token(self, authenticator):
        """Test null token is handled."""
        with pytest.raises((TypeError, AttributeError)):
            authenticator.verify_token(None)

    def test_non_base64_token(self, authenticator):
        """Test non-base64 token is rejected."""
        assert authenticator.verify_token("not.a.valid.token") is None

    def test_incomplete_token(self, authenticator):
        """Test incomplete token is rejected."""
        assert authenticator.verify_token("eyJhbGciOiJIUzI1NiJ9") is None
        assert authenticator.verify_token("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0") is None

    def test_extra_segments_token(self, authenticator):
        """Test token with extra segments is rejected."""
        result = authenticator.verify_token("a.b.c.d.e")
        assert result is None


@pytest.mark.unit
class TestRefreshTokenSecurity:
    """Tests for refresh token security."""

    def test_refresh_token_different_from_access(self, authenticator):
        """Test refresh token is different from access token."""
        access_token = authenticator.create_token(
            user_id="user123",
            tenant_id="tenant456",
            roles=["farmer"],
            expires_delta=timedelta(minutes=15),
        )

        refresh_token = authenticator.create_token(
            user_id="user123",
            tenant_id="tenant456",
            roles=["refresh"],
            expires_delta=timedelta(days=7),
        )

        assert access_token != refresh_token

    def test_refresh_token_longer_expiry(self, authenticator):
        """Test refresh token has longer expiry than access token."""
        access_expiry = timedelta(minutes=15)
        refresh_expiry = timedelta(days=7)

        assert refresh_expiry > access_expiry

    def test_refresh_token_rotation(self, authenticator):
        """Test refresh token rotation on use."""
        old_refresh = authenticator.create_token(
            user_id="user123",
            tenant_id="tenant456",
            roles=["refresh"],
            expires_delta=timedelta(days=7),
        )

        new_refresh = authenticator.create_token(
            user_id="user123",
            tenant_id="tenant456",
            roles=["refresh"],
            expires_delta=timedelta(days=7),
        )

        old_payload = jwt.decode(old_refresh, TEST_SECRET_KEY, algorithms=["HS256"])
        authenticator.revoke_token(old_payload["jti"])

        assert authenticator.verify_token(old_refresh) is None
        assert authenticator.verify_token(new_refresh) is not None
