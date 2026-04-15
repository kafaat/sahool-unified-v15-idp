"""Unit tests for shared.platform.ContextMiddleware JWT handling.

Covers the defense-in-depth JWT verification policy:
1. When JWT_SECRET_KEY is set, the signature is ALWAYS verified locally,
   regardless of TRUST_GATEWAY_JWT.
2. When JWT_SECRET_KEY is absent and TRUST_GATEWAY_JWT=true, a manual
   unverified decode is used, still enforcing token expiry.
3. When JWT_SECRET_KEY is absent and TRUST_GATEWAY_JWT is not set, any
   authenticated request is rejected.

The middleware is exercised through its internal helpers (`_decode_jwt`
and `_decode_claims_unverified`) so tests do not need a live FastAPI app.
"""

from __future__ import annotations

import base64
import json
import os
import time
from unittest.mock import patch

import jwt
import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from shared.platform import ContextMiddleware  # noqa: E402

SECRET = "test-secret-key-for-unit-tests-only-32chars"
OTHER_SECRET = "a-completely-different-attacker-key-32ch"


def _make_manual_token(claims: dict, header: dict | None = None) -> str:
    """Build a JWT manually with an arbitrary (unsigned) signature segment."""
    header = header or {"alg": "HS256", "typ": "JWT"}

    def b64(obj: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip("=")

    return f"{b64(header)}.{b64(claims)}.fake-signature"


@pytest.fixture
def middleware():
    """Return a ContextMiddleware instance with a dummy ASGI app."""
    dummy_app = lambda scope, receive, send: None  # noqa: E731 - tests don't exercise ASGI
    return ContextMiddleware(dummy_app, service_name="test-service")


class TestDecodeClaimsUnverified:
    """Tests for the manual base64 claim decoder used in the gateway-trust path."""

    def test_decodes_valid_claims(self):
        token = _make_manual_token({"sub": "u1", "tid": "t1", "exp": int(time.time()) + 60})
        claims = ContextMiddleware._decode_claims_unverified(token)
        assert claims["sub"] == "u1"
        assert claims["tid"] == "t1"

    def test_rejects_expired_token(self):
        token = _make_manual_token({"sub": "u1", "exp": int(time.time()) - 1})
        with pytest.raises(ValueError, match="expired"):
            ContextMiddleware._decode_claims_unverified(token)

    def test_rejects_missing_exp_claim(self):
        token = _make_manual_token({"sub": "u1"})
        with pytest.raises(ValueError, match="'exp' claim"):
            ContextMiddleware._decode_claims_unverified(token)

    def test_rejects_non_numeric_exp_claim(self):
        token = _make_manual_token({"sub": "u1", "exp": "tomorrow"})
        with pytest.raises(ValueError, match="numeric"):
            ContextMiddleware._decode_claims_unverified(token)

    def test_rejects_malformed_token(self):
        with pytest.raises(ValueError, match="Malformed"):
            ContextMiddleware._decode_claims_unverified("not.enough")

    def test_rejects_non_dict_payload(self):
        bad_payload = base64.urlsafe_b64encode(b'["a", "b"]').decode().rstrip("=")
        token = f"header.{bad_payload}.sig"
        with pytest.raises(ValueError, match="JSON object"):
            ContextMiddleware._decode_claims_unverified(token)

    def test_rejects_invalid_json_payload(self):
        bad_payload = base64.urlsafe_b64encode(b"not json").decode().rstrip("=")
        token = f"header.{bad_payload}.sig"
        with pytest.raises(ValueError, match="Invalid JWT payload"):
            ContextMiddleware._decode_claims_unverified(token)

    def test_handles_base64_padding_edge_cases(self):
        # Exercise claim lengths that exercise all 4 possible base64 padding states.
        for length in range(5):
            claims = {"sub": "a" * length, "exp": int(time.time()) + 60}
            token = _make_manual_token(claims)
            decoded = ContextMiddleware._decode_claims_unverified(token)
            assert decoded["sub"] == "a" * length


class TestDecodeJwtDefenseInDepth:
    """Tests for the top-level _decode_jwt dispatch (signed vs. unverified paths)."""

    def test_verifies_signature_when_secret_is_set(self, middleware):
        token = jwt.encode(
            {"sub": "u1", "exp": int(time.time()) + 60},
            SECRET,
            algorithm="HS256",
        )
        with patch.dict(os.environ, {"JWT_SECRET_KEY": SECRET, "JWT_ALGORITHM": "HS256"}):
            claims = middleware._decode_jwt(token)
        assert claims["sub"] == "u1"

    def test_rejects_tampered_token_when_secret_is_set(self, middleware):
        # Token signed with the attacker's key should be rejected even if
        # the gateway-trust flag is on — that's the whole point of defense-in-depth.
        tampered = jwt.encode(
            {"sub": "attacker", "exp": int(time.time()) + 60},
            OTHER_SECRET,
            algorithm="HS256",
        )
        with patch.dict(
            os.environ,
            {"JWT_SECRET_KEY": SECRET, "JWT_ALGORITHM": "HS256", "TRUST_GATEWAY_JWT": "true"},
        ):
            with patch.object(ContextMiddleware, "_trust_gateway", True):
                with pytest.raises(jwt.InvalidSignatureError):
                    middleware._decode_jwt(tampered)

    def test_uses_unverified_path_when_no_secret_but_trust_gateway_true(self, middleware):
        token = _make_manual_token({"sub": "u1", "exp": int(time.time()) + 60})
        with patch.dict(os.environ, {"JWT_ALGORITHM": "HS256"}, clear=False):
            os.environ.pop("JWT_SECRET_KEY", None)
            with patch.object(ContextMiddleware, "_trust_gateway", True):
                claims = middleware._decode_jwt(token)
        assert claims["sub"] == "u1"

    def test_rejects_when_no_secret_and_trust_gateway_false(self, middleware):
        token = _make_manual_token({"sub": "u1", "exp": int(time.time()) + 60})
        with patch.dict(os.environ, {"JWT_ALGORITHM": "HS256"}, clear=False):
            os.environ.pop("JWT_SECRET_KEY", None)
            with patch.object(ContextMiddleware, "_trust_gateway", False):
                with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
                    middleware._decode_jwt(token)
