"""
Tenant Isolation Security Tests
================================
اختبارات أمان عزل المستأجرين

Deep, non-trivial tests verifying that cross-tenant access is blocked
across database queries, cache, NATS events, authentication, rate limiting,
and input validation boundaries.

These tests exercise real production code paths — not just schema checks —
to ensure multi-tenant isolation cannot be bypassed.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Constants used across tests
# ---------------------------------------------------------------------------
TENANT_A = "11111111-1111-1111-1111-111111111111"
TENANT_B = "22222222-2222-2222-2222-222222222222"
FIELD_ID = "field-001"

# ---------------------------------------------------------------------------
# Helper: load indicators-service module from hyphenated directory path
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

def _load_indicators_main():
    """Load apps/services/indicators-service/src/main.py as a module.

    The directory contains a hyphen which is not a valid Python identifier,
    so we use importlib.util to load it by file path.
    """
    module_name = "indicators_service_main"
    if module_name in sys.modules:
        return sys.modules[module_name]

    src_path = _PROJECT_ROOT / "apps" / "services" / "indicators-service" / "src" / "main.py"
    spec = importlib.util.spec_from_file_location(module_name, src_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# 1. Cross-tenant DB query prevention (indicators-service)
# ===========================================================================


class TestCrossTenantDatabaseIsolation:
    """Verify that indicators-service DB queries filter by tenant_id and
    never leak data from one tenant to another."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock FastAPI app with a fake db_pool that returns
        pre-seeded rows scoped to TENANT_A only."""

        tenant_a_rows = [
            {
                "value": json.dumps({"ndvi": 0.72}),
                "calculated_at": datetime(2026, 1, 1, tzinfo=UTC),
                "indicator_type": "ndvi",
            },
        ]

        async def fake_fetchrow(sql, *args):
            """Simulate a database that only has rows for TENANT_A."""
            # If the query includes a tenant_id parameter, check it
            if len(args) >= 3 and args[2] == TENANT_A:
                return tenant_a_rows[0]
            # Wrong tenant or no tenant filter -> no data
            if len(args) >= 3 and args[2] != TENANT_A:
                return None
            # No tenant param at all -> should not happen when tenant_id is given
            return None

        async def fake_fetch(sql, *args):
            """Simulate a database that only has rows for TENANT_A."""
            if len(args) >= 2 and args[1] == TENANT_A:
                return tenant_a_rows
            if len(args) >= 2 and args[1] != TENANT_A:
                return []
            return []

        mock_conn = AsyncMock()
        mock_conn.fetchrow = fake_fetchrow
        mock_conn.fetch = fake_fetch

        class FakeAcquire:
            async def __aenter__(self):
                return mock_conn

            async def __aexit__(self, *args):
                pass

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = FakeAcquire()

        app = MagicMock()
        app.state = SimpleNamespace(db_pool=mock_pool, nc=None)
        return app

    def test_get_indicator_returns_data_for_correct_tenant(self, mock_app):
        """Verify get_indicator() returns data when queried with the owning tenant.

        Security property: A tenant can access its own indicator data.
        """
        indicators_main = _load_indicators_main()
        get_indicator = indicators_main.get_indicator

        # Patch the module-level 'app' so the function sees our mock
        with patch.object(indicators_main, "app", mock_app):
            result = asyncio.get_event_loop().run_until_complete(
                get_indicator(FIELD_ID, "ndvi", tenant_id=TENANT_A)
            )
            assert result is not None
            assert result["ndvi"] == 0.72

    def test_get_indicator_returns_none_for_wrong_tenant(self, mock_app):
        """Verify get_indicator() returns None when queried with a different tenant.

        Security property: Cross-tenant data access returns empty, not another
        tenant's data.
        """
        indicators_main = _load_indicators_main()
        get_indicator = indicators_main.get_indicator

        with patch.object(indicators_main, "app", mock_app):
            result = asyncio.get_event_loop().run_until_complete(
                get_indicator(FIELD_ID, "ndvi", tenant_id=TENANT_B)
            )
            assert result is None, (
                "get_indicator must return None for a tenant that does not own the field"
            )

    def test_get_all_field_indicators_empty_for_wrong_tenant(self, mock_app):
        """Verify get_all_field_indicators() returns [] for wrong tenant.

        Security property: Listing all indicators for a field scoped to a
        different tenant must yield an empty list, not the real tenant's data.
        """
        indicators_main = _load_indicators_main()
        get_all_field_indicators = indicators_main.get_all_field_indicators

        with patch.object(indicators_main, "app", mock_app):
            result = asyncio.get_event_loop().run_until_complete(
                get_all_field_indicators(FIELD_ID, tenant_id=TENANT_B)
            )
            assert result == [], (
                "get_all_field_indicators must return [] for a non-owning tenant"
            )

    def test_get_all_field_indicators_returns_data_for_correct_tenant(self, mock_app):
        """Verify get_all_field_indicators() returns data for the correct tenant.

        Security property: The owning tenant can see its own indicator list.
        """
        indicators_main = _load_indicators_main()
        get_all_field_indicators = indicators_main.get_all_field_indicators

        with patch.object(indicators_main, "app", mock_app):
            result = asyncio.get_event_loop().run_until_complete(
                get_all_field_indicators(FIELD_ID, tenant_id=TENANT_A)
            )
            assert len(result) == 1
            assert result[0]["ndvi"] == 0.72


# ===========================================================================
# 2. Cross-tenant LLM cache isolation
# ===========================================================================


class TestCrossTenantCacheIsolation:
    """Verify that the LLM provider cache produces different keys for different
    tenants even when the prompt is identical."""

    def test_cache_key_differs_by_tenant(self):
        """Verify _build_cache_key() produces distinct keys per tenant.

        Security property: Two tenants submitting the same prompt must not
        share a cached LLM response.
        """
        from shared.ai.llm_provider import _build_cache_key

        prompt = "What is the best irrigation schedule for wheat?"
        key_a = _build_cache_key(prompt, None, "ollama", "0.7", tenant_id=TENANT_A)
        key_b = _build_cache_key(prompt, None, "ollama", "0.7", tenant_id=TENANT_B)

        assert key_a != key_b, (
            "Cache keys MUST differ when tenant_id differs, even for identical prompts"
        )

    def test_cache_key_without_tenant_differs_from_with_tenant(self):
        """Verify that omitting tenant_id produces a different key from any tenant.

        Security property: A request without tenant context must not collide
        with any tenant-scoped cache entry.
        """
        from shared.ai.llm_provider import _build_cache_key

        prompt = "Nitrogen deficiency in wheat"
        key_no_tenant = _build_cache_key(prompt, None, "ollama", "0.7", tenant_id="")
        key_with_tenant = _build_cache_key(prompt, None, "ollama", "0.7", tenant_id=TENANT_A)

        assert key_no_tenant != key_with_tenant

    def test_cache_key_is_deterministic(self):
        """Verify cache key is deterministic for same inputs.

        Security property: Ensures the hashing is stable and not using random salt
        that could cause cache misses and inconsistent isolation.
        """
        from shared.ai.llm_provider import _build_cache_key

        prompt = "Check soil moisture"
        key1 = _build_cache_key(prompt, "system", "auto", "0.5", tenant_id=TENANT_A)
        key2 = _build_cache_key(prompt, "system", "auto", "0.5", tenant_id=TENANT_A)

        assert key1 == key2, "Cache key must be deterministic for the same inputs"

    def test_cache_key_format_is_sha256(self):
        """Verify cache key is a valid SHA-256 hex digest.

        Security property: Using a cryptographic hash prevents key manipulation
        and ensures uniform distribution in the cache namespace.
        """
        from shared.ai.llm_provider import _build_cache_key

        key = _build_cache_key("test", None, "auto", "0.7", tenant_id=TENANT_A)
        assert re.match(r"^[0-9a-f]{64}$", key), (
            f"Cache key must be a 64-char hex SHA-256 digest, got: {key!r}"
        )


# ===========================================================================
# 3. Cross-tenant NATS event isolation
# ===========================================================================


class TestNATSEventTenantIsolation:
    """Verify that NATS events enforce tenant_id and that the EventPublisher
    rejects events without it."""

    def test_publish_event_rejects_missing_tenant_id(self):
        """Verify EventPublisher.publish_event() returns False for events
        without tenant_id.

        Security property: Events cannot be published to the NATS bus without
        a tenant_id, preventing cross-tenant event leakage.
        """
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import EventPublisher

        publisher = EventPublisher(service_name="test-service")
        publisher._connected = True
        publisher._nc = MagicMock()

        event = BaseEvent(tenant_id=None, source_service="test")
        result = asyncio.get_event_loop().run_until_complete(
            publisher.publish_event("sahool.field.created", event)
        )

        assert result is False, (
            "publish_event must reject events without tenant_id"
        )
        assert publisher._error_count > 0

    def test_publish_json_rejects_missing_tenant_id(self):
        """Verify EventPublisher.publish_json() rejects dict payloads missing tenant_id.

        Security property: Raw JSON event publishing also enforces tenant isolation.
        """
        from shared.events.publisher import EventPublisher

        publisher = EventPublisher(service_name="test-service")
        publisher._connected = True
        publisher._nc = MagicMock()

        data = {"field_id": FIELD_ID, "event_id": "evt-1"}
        result = asyncio.get_event_loop().run_until_complete(
            publisher.publish_json("sahool.field.created", data)
        )

        assert result is False
        assert publisher._rejected_count > 0, (
            "publish_json must increment rejected_count for missing tenant_id"
        )

    def test_publish_json_records_rejected_event_in_dlq(self):
        """Verify rejected events are recorded in the DLQ buffer.

        Security property: Missing-tenant events are tracked for auditing,
        not silently discarded.
        """
        from shared.events.publisher import EventPublisher

        publisher = EventPublisher(service_name="test-service")
        publisher._connected = True
        publisher._nc = MagicMock()

        asyncio.get_event_loop().run_until_complete(
            publisher.publish_json("sahool.test.event", {"field_id": "f1"})
        )

        rejected = publisher.rejected_events
        assert len(rejected) == 1
        assert rejected[0]["reason"] == "missing_tenant_id"
        assert rejected[0]["subject"] == "sahool.test.event"

    def test_tenant_scoped_subject_includes_tenant_id(self):
        """Verify get_tenant_subject() embeds the tenant UUID in the subject.

        Security property: Tenant-scoped NATS subjects route events to
        per-tenant channels, preventing cross-tenant subscription.
        """
        from shared.events.subjects import get_tenant_subject

        subject = get_tenant_subject(TENANT_A, "field", "created")
        assert TENANT_A in subject
        assert subject == f"sahool.tenant.{TENANT_A}.field.created"

    def test_tenant_subject_rejects_non_uuid(self):
        """Verify get_tenant_subject() raises ValueError for non-UUID tenant_id.

        Security property: Prevents subject injection via malformed tenant IDs.
        """
        from shared.events.subjects import get_tenant_subject

        with pytest.raises(ValueError, match="valid UUID"):
            get_tenant_subject("not-a-uuid", "field", "created")

    def test_tenant_subject_rejects_wildcard_injection(self):
        """Verify get_tenant_subject() rejects tenant_ids with NATS wildcards.

        Security property: Prevents a malicious tenant_id like '>' or '*'
        from subscribing to all events across tenants.
        """
        from shared.events.subjects import get_tenant_subject

        for malicious_tid in [
            "11111111-1111-1111-1111-11111111111>",
            "11111111-1111-1111-1111-11111111111*",
        ]:
            with pytest.raises(ValueError):
                get_tenant_subject(malicious_tid, "field", "created")


# ===========================================================================
# 4. Auth endpoint enforcement (indicators-service)
# ===========================================================================


class TestAuthEndpointEnforcement:
    """Verify that _enforce_tenant raises correct HTTP errors for unauthenticated
    and cross-tenant access."""

    def test_enforce_tenant_raises_401_for_no_user(self):
        """Verify _enforce_tenant() returns 401 when user is None.

        Security property: Unauthenticated requests are always rejected.
        """
        from fastapi import HTTPException

        _enforce_tenant = _load_indicators_main()._enforce_tenant

        with pytest.raises(HTTPException) as exc_info:
            _enforce_tenant(None, TENANT_A)
        assert exc_info.value.status_code == 401

    def test_enforce_tenant_raises_403_for_mismatched_tenant(self):
        """Verify _enforce_tenant() returns 403 when JWT tenant != requested tenant.

        Security property: A user from tenant A cannot access tenant B's data
        even with a valid token.
        """
        from fastapi import HTTPException

        _enforce_tenant = _load_indicators_main()._enforce_tenant

        user = SimpleNamespace(tenant_id=TENANT_A, roles=["farmer"])
        with pytest.raises(HTTPException) as exc_info:
            _enforce_tenant(user, TENANT_B)
        assert exc_info.value.status_code == 403
        assert "tenant_mismatch" in str(exc_info.value.detail)

    def test_enforce_tenant_allows_admin_cross_tenant(self):
        """Verify _enforce_tenant() allows admin users to access any tenant.

        Security property: Admin role is the only path to cross-tenant access.
        """
        _enforce_tenant = _load_indicators_main()._enforce_tenant

        admin_user = SimpleNamespace(tenant_id=TENANT_A, roles=["admin"])
        # Should not raise
        _enforce_tenant(admin_user, TENANT_B)

    def test_enforce_tenant_allows_super_admin_cross_tenant(self):
        """Verify _enforce_tenant() allows super_admin users to access any tenant."""
        _enforce_tenant = _load_indicators_main()._enforce_tenant

        super_admin = SimpleNamespace(tenant_id=TENANT_A, roles=["super_admin"])
        _enforce_tenant(super_admin, TENANT_B)

    def test_enforce_tenant_blocks_non_admin_roles(self):
        """Verify non-admin roles (farmer, agronomist, viewer) cannot cross tenants.

        Security property: Only admin and super_admin bypass tenant isolation.
        """
        from fastapi import HTTPException

        _enforce_tenant = _load_indicators_main()._enforce_tenant

        for role in ["farmer", "agronomist", "viewer", "manager", "operator"]:
            user = SimpleNamespace(tenant_id=TENANT_A, roles=[role])
            with pytest.raises(HTTPException) as exc_info:
                _enforce_tenant(user, TENANT_B)
            assert exc_info.value.status_code == 403, (
                f"Role '{role}' should be blocked from cross-tenant access"
            )


# ===========================================================================
# 5. Tenant ID validation
# ===========================================================================


class TestTenantIdValidation:
    """Verify that the indicators-service rejects invalid tenant_id values."""

    def test_rejects_empty_tenant_id(self):
        """Verify empty string tenant_id is rejected.

        Security property: Empty tenant_id cannot bypass tenant filtering.
        """
        from fastapi import HTTPException

        from apps.services.indicators_service.src.main import _validate_tenant_id

        with pytest.raises(HTTPException) as exc_info:
            _validate_tenant_id("")
        assert exc_info.value.status_code == 400

    def test_rejects_whitespace_only_tenant_id(self):
        """Verify whitespace-only tenant_id is rejected.

        Security property: Whitespace cannot trick tenant_id parsing.
        """
        from fastapi import HTTPException

        from apps.services.indicators_service.src.main import _validate_tenant_id

        with pytest.raises(HTTPException) as exc_info:
            _validate_tenant_id("   ")
        assert exc_info.value.status_code == 400

    def test_rejects_overlong_tenant_id(self):
        """Verify tenant_id longer than 255 chars is rejected.

        Security property: Prevents buffer overflow and excessive storage.
        """
        from fastapi import HTTPException

        from apps.services.indicators_service.src.main import _validate_tenant_id

        long_tid = "a" * 256
        with pytest.raises(HTTPException) as exc_info:
            _validate_tenant_id(long_tid)
        assert exc_info.value.status_code == 400

    def test_accepts_valid_tenant_id(self):
        """Verify a valid tenant_id passes validation."""
        from apps.services.indicators_service.src.main import _validate_tenant_id

        # Should not raise
        _validate_tenant_id(TENANT_A)

    def test_accepts_none_tenant_id(self):
        """Verify None tenant_id is accepted (optional parameter)."""
        from apps.services.indicators_service.src.main import _validate_tenant_id

        # Should not raise
        _validate_tenant_id(None)


# ===========================================================================
# 6. Cache key collision prevention
# ===========================================================================


class TestCacheKeyCollisionPrevention:
    """Verify that two tenants with the same field_id get different cache keys."""

    def test_same_field_id_different_tenants_different_keys(self):
        """Verify cache keys include tenant_id so same field_id in different
        tenants never collide.

        Security property: Cache entries for field-001 in tenant A must not
        be served to tenant B requesting field-001.
        """
        from shared.ai.llm_provider import _build_cache_key

        key_a = _build_cache_key(
            f"indicators:{FIELD_ID}:ndvi", None, "auto", "0", tenant_id=TENANT_A
        )
        key_b = _build_cache_key(
            f"indicators:{FIELD_ID}:ndvi", None, "auto", "0", tenant_id=TENANT_B
        )

        assert key_a != key_b, (
            "Same field_id with different tenant_id must produce different cache keys"
        )

    def test_nats_headers_include_tenant_id(self):
        """Verify NATS message headers carry X-Tenant-ID for routing isolation.

        Security property: Downstream consumers can verify tenant ownership
        via the X-Tenant-ID header on every NATS message.
        """
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import _build_nats_headers

        event = BaseEvent(tenant_id=TENANT_A, source_service="test")
        headers = _build_nats_headers(event)

        assert headers is not None
        assert headers["X-Tenant-ID"] == TENANT_A

    def test_nats_headers_omit_tenant_when_missing(self):
        """Verify headers do not contain X-Tenant-ID when event has no tenant.

        Security property: No default/empty tenant is injected that could
        match a real tenant.
        """
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import _build_nats_headers

        event = BaseEvent(tenant_id=None, source_service="test")
        headers = _build_nats_headers(event)

        if headers:
            assert "X-Tenant-ID" not in headers


# ===========================================================================
# 7. Rate limit per-user isolation
# ===========================================================================


class TestRateLimitUserIsolation:
    """Verify that the rate limiter tracks users independently so one user
    exhausting their limit does not affect another."""

    def test_different_users_have_independent_buckets(self):
        """Verify that two users (different IPs, same tenant) get separate
        token buckets.

        Security property: One user's rate limit exhaustion does not
        deny service to another user.
        """
        from shared.middleware.rate_limit import RateLimitConfig, RateLimiter, TierConfig

        limiter = RateLimiter(
            TierConfig(
                free=RateLimitConfig(requests_per_minute=2, requests_per_hour=10, burst_limit=2),
            )
        )

        # Simulate two different client keys (tenant:ip)
        key_user_a = f"{TENANT_A}:10.0.0.1"
        key_user_b = f"{TENANT_A}:10.0.0.2"

        config = RateLimitConfig(requests_per_minute=2, requests_per_hour=10, burst_limit=2)

        # Exhaust user A's bucket
        bucket_a = limiter._get_bucket(key_user_a, config)
        bucket_a.consume(2)

        # User B should still have tokens
        bucket_b = limiter._get_bucket(key_user_b, config)
        assert bucket_b.consume(1) is True, (
            "User B's bucket must be independent of User A's exhausted bucket"
        )

    def test_different_tenants_have_independent_buckets(self):
        """Verify that two tenants get separate rate limit tracking.

        Security property: Tenant A cannot DoS tenant B by exhausting
        shared rate limit counters.
        """
        from shared.middleware.rate_limit import RateLimitConfig, RateLimiter, TierConfig

        limiter = RateLimiter()

        key_tenant_a = f"{TENANT_A}:10.0.0.1"
        key_tenant_b = f"{TENANT_B}:10.0.0.1"

        config = RateLimitConfig(requests_per_minute=1, requests_per_hour=5, burst_limit=1)

        bucket_a = limiter._get_bucket(key_tenant_a, config)
        bucket_a.consume(1)
        assert bucket_a.consume(1) is False, "Tenant A should be rate limited"

        bucket_b = limiter._get_bucket(key_tenant_b, config)
        assert bucket_b.consume(1) is True, (
            "Tenant B must have its own bucket, unaffected by tenant A"
        )


# ===========================================================================
# 8. Input validation boundaries (Field constraints)
# ===========================================================================


class TestInputValidationBoundaries:
    """Verify that Pydantic field constraints reject invalid data at the boundary."""

    def test_field_id_regex_rejects_special_characters(self):
        """Verify _validate_field_id rejects SQL injection and path traversal.

        Security property: Field IDs cannot contain characters that enable
        injection attacks (;, ', /, .., etc.).
        """
        from fastapi import HTTPException

        from apps.services.indicators_service.src.main import _validate_field_id

        malicious_ids = [
            "'; DROP TABLE--",
            "../../../etc/passwd",
            "field<script>",
            "",
            "a" * 101,
            "field id with spaces",
            "field.with.dots",
        ]

        for bad_id in malicious_ids:
            with pytest.raises(HTTPException) as exc_info:
                _validate_field_id(bad_id)
            assert exc_info.value.status_code == 400, (
                f"_validate_field_id should reject '{bad_id}'"
            )

    def test_field_id_accepts_valid_formats(self):
        """Verify valid field IDs pass validation."""
        from apps.services.indicators_service.src.main import _validate_field_id

        valid_ids = [
            "field-001",
            "FIELD_123",
            "abc",
            "a" * 100,  # Max length
            "123",
            "field-with-hyphens_and_underscores",
        ]

        for valid_id in valid_ids:
            _validate_field_id(valid_id)  # Should not raise

    def test_field_created_event_rejects_negative_area(self):
        """Verify FieldCreatedEvent rejects negative area_hectares.

        Security property: Negative area could cause incorrect billing
        or geospatial calculations.
        """
        from uuid import uuid4

        from pydantic import ValidationError

        from shared.events.contracts import FieldCreatedEvent

        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid4(),
                farm_id=uuid4(),
                tenant_id=uuid4(),
                name="Test Field",
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
                area_hectares=-5.0,
            )

    def test_field_created_event_rejects_empty_name(self):
        """Verify FieldCreatedEvent rejects empty field name.

        Security property: Prevents creation of unnamed fields that could
        confuse audit trails.
        """
        from uuid import uuid4

        from pydantic import ValidationError

        from shared.events.contracts import FieldCreatedEvent

        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid4(),
                farm_id=uuid4(),
                tenant_id=uuid4(),
                name="",
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            )

    def test_field_created_event_rejects_overlong_name(self):
        """Verify FieldCreatedEvent rejects names exceeding max_length=120.

        Security property: Prevents buffer overflow in downstream consumers.
        """
        from uuid import uuid4

        from pydantic import ValidationError

        from shared.events.contracts import FieldCreatedEvent

        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid4(),
                farm_id=uuid4(),
                tenant_id=uuid4(),
                name="A" * 121,
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            )


# ===========================================================================
# 9. Token revocation fail-closed behavior
# ===========================================================================


class TestTokenRevocationFailClosed:
    """Verify that token revocation checks fail closed when Redis is unavailable,
    treating the token as revoked rather than allowing it through."""

    def test_is_token_revoked_returns_true_on_redis_error(self):
        """Verify is_token_revoked() returns True (revoked) when Redis raises.

        Security property: If the revocation store is down, tokens are treated
        as revoked — fail closed, not fail open. A fail-open behavior would
        allow revoked tokens to be accepted during Redis outages.
        """
        from shared.auth.token_revocation import RedisTokenRevocationStore

        store = RedisTokenRevocationStore.__new__(RedisTokenRevocationStore)
        store._initialized = True

        # Create a mock Redis that raises on .exists()
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(side_effect=ConnectionError("Redis unavailable"))
        store._redis = mock_redis

        result = asyncio.get_event_loop().run_until_complete(
            store.is_token_revoked("some-jti-token")
        )

        assert result is True, (
            "is_token_revoked MUST return True (fail closed) when Redis is unavailable. "
            "Returning False would allow revoked tokens through during outages."
        )

    def test_is_token_revoked_returns_false_for_empty_jti(self):
        """Verify empty JTI returns False (not revoked, but also not valid).

        Security property: Empty JTIs are not in the revocation store,
        but the caller must also validate the JTI is non-empty.
        """
        from shared.auth.token_revocation import RedisTokenRevocationStore

        store = RedisTokenRevocationStore.__new__(RedisTokenRevocationStore)
        store._initialized = True
        store._redis = AsyncMock()

        result = asyncio.get_event_loop().run_until_complete(
            store.is_token_revoked("")
        )
        assert result is False

    def test_is_token_revoked_returns_true_for_revoked_token(self):
        """Verify is_token_revoked() correctly identifies a revoked token.

        Security property: A token that has been explicitly revoked must
        always be reported as revoked.
        """
        from shared.auth.token_revocation import RedisTokenRevocationStore

        store = RedisTokenRevocationStore.__new__(RedisTokenRevocationStore)
        store._initialized = True

        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)
        store._redis = mock_redis

        result = asyncio.get_event_loop().run_until_complete(
            store.is_token_revoked("revoked-jti")
        )
        assert result is True


# ===========================================================================
# 10. NATS wildcard matching
# ===========================================================================


class TestNATSWildcardMatching:
    """Verify that NATS wildcard subject functions generate correct patterns."""

    def test_get_wildcard_subject_returns_deep_wildcard(self):
        """Verify get_wildcard_subject() uses '>' for deep matching.

        Security property: The '>' wildcard matches one or more tokens,
        ensuring subscription to all sub-subjects (e.g., sahool.field.created,
        sahool.field.boundary.updated). Using '*' would miss nested subjects.
        """
        from shared.events.subjects import get_wildcard_subject

        result = get_wildcard_subject("field")
        assert result == "sahool.field.>"
        assert result.endswith(">"), (
            "Wildcard subject must end with '>' for deep (multi-level) matching"
        )

    def test_get_wildcard_subject_for_various_domains(self):
        """Verify wildcard subjects are correctly formed for all major domains."""
        from shared.events.subjects import get_wildcard_subject

        domains = ["field", "weather", "billing", "health", "satellite", "agent"]
        for domain in domains:
            result = get_wildcard_subject(domain)
            assert result == f"sahool.{domain}.>", (
                f"Wildcard for '{domain}' must be 'sahool.{domain}.>'"
            )

    def test_event_payload_validation_rejects_missing_tenant_id(self):
        """Verify validate_event_payload() catches missing tenant_id.

        Security property: Events missing tenant_id are caught at validation
        time, not just at publish time.
        """
        from shared.events.contracts import validate_event_payload

        payload = {
            "event_id": "evt-1",
            "timestamp": "2026-01-01T00:00:00Z",
            "source_service": "test",
            # tenant_id intentionally missing
        }

        result = validate_event_payload("sahool.field.created", payload)
        assert result is False, (
            "validate_event_payload must return False when tenant_id is missing"
        )

    def test_event_payload_validation_rejects_empty_tenant_id(self):
        """Verify validate_event_payload() rejects empty-string tenant_id.

        Security property: An empty tenant_id is as dangerous as a missing one.
        """
        from shared.events.contracts import validate_event_payload

        payload = {
            "event_id": "evt-1",
            "timestamp": "2026-01-01T00:00:00Z",
            "source_service": "test",
            "tenant_id": "",
        }

        result = validate_event_payload("sahool.field.created", payload)
        assert result is False, (
            "validate_event_payload must reject empty tenant_id"
        )

    def test_event_payload_validation_strict_raises_on_missing_fields(self):
        """Verify strict mode raises ValueError instead of returning False.

        Security property: In strict mode, missing required fields cause
        immediate failure, suitable for critical code paths.
        """
        from shared.events.contracts import validate_event_payload

        payload = {"event_id": "evt-1"}

        with pytest.raises(ValueError, match="missing required fields"):
            validate_event_payload("sahool.test.event", payload, strict=True)
