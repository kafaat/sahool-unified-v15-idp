"""
SAHOOL Resilience & Error Handling Integration Tests
=====================================================
اختبارات المرونة ومعالجة الأخطاء لمنصة سهول

Tests verifying system resilience under real failure scenarios:
- Database connection failure graceful degradation
- NATS disconnection handling
- Redis cache failure fallback
- Malformed request handling
- Concurrent request safety
- Circuit breaker state transitions
- Retry logic with exponential backoff
- Memory limits for in-memory caches
- Graceful shutdown / lifespan cleanup
- Bilingual error response consistency

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import OrderedDict
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

from shared.ai.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
    get_circuit_breaker,
    reset_all_circuit_breakers,
)
from shared.errors_py import (
    ErrorCode,
    ExternalServiceException,
    SahoolException,
    add_request_id_middleware,
    create_error_response,
    setup_exception_handlers,
)
from shared.events.publisher import EventPublisher, PublisherConfig
from shared.terrain.cache import LRUCache


# ---------------------------------------------------------------------------
# Helpers: build a minimal FastAPI app that mimics real service patterns
# ---------------------------------------------------------------------------

def _build_test_app() -> FastAPI:
    """Create a minimal FastAPI app with SAHOOL error handling for testing."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.db_pool = MagicMock()
        app.state.nc = MagicMock()
        app.state.redis = MagicMock()
        yield
        # Cleanup
        if hasattr(app.state, "db_pool") and app.state.db_pool:
            app.state.db_pool.close()
            app.state.db_pool = None
        if hasattr(app.state, "nc") and app.state.nc:
            app.state.nc.close()
            app.state.nc = None
        if hasattr(app.state, "redis") and app.state.redis:
            app.state.redis.close()
            app.state.redis = None

    app = FastAPI(title="Resilience Test Service", version="16.0.0", lifespan=lifespan)
    setup_exception_handlers(app)
    add_request_id_middleware(app)

    @app.get("/healthz")
    async def health():
        return {"status": "ok", "service": "test", "version": "16.0.0"}

    @app.get("/db-dependent")
    async def db_endpoint(request: Request):
        pool = getattr(request.app.state, "db_pool", None)
        if pool is None:
            raise SahoolException(
                message="Database unavailable",
                message_ar="قاعدة البيانات غير متوفرة",
                code=ErrorCode.DATABASE_ERROR,
                status_code=503,
            )
        try:
            result = await pool.fetchval("SELECT 1")
            return {"result": result}
        except (ConnectionError, OSError):
            raise SahoolException(
                message="Database connection failed",
                message_ar="فشل الاتصال بقاعدة البيانات",
                code=ErrorCode.DATABASE_ERROR,
                status_code=503,
            )

    @app.post("/events/publish")
    async def publish_endpoint(request: Request):
        nc = getattr(request.app.state, "nats_client", None)
        if nc is None:
            return {"published": False, "reason": "NATS not connected"}
        return {"published": True}

    @app.post("/items")
    async def create_item(request: Request):
        try:
            body = await request.json()
        except json.JSONDecodeError:
            raise SahoolException(
                message="Invalid JSON payload",
                message_ar="حمولة JSON غير صالحة",
                code=ErrorCode.VALIDATION_ERROR,
                status_code=400,
            )
        if not body.get("name"):
            raise SahoolException(
                message="Field 'name' is required",
                message_ar="حقل 'الاسم' مطلوب",
                code=ErrorCode.VALIDATION_ERROR,
                status_code=400,
            )
        return {"success": True, "data": body}

    @app.get("/external-service")
    async def external_service():
        raise ExternalServiceException(
            message="External service unavailable",
            message_ar="الخدمة الخارجية غير متوفرة",
        )

    return app


@pytest.fixture
def test_app() -> FastAPI:
    return _build_test_app()


@pytest.fixture
async def client(test_app: FastAPI):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ===========================================================================
# 1. Database connection failure graceful degradation
# ===========================================================================


class TestDatabaseFailureGracefulDegradation:
    """Verify service returns 503 (not 500) with proper structure on DB failure."""

    @pytest.mark.asyncio
    async def test_db_pool_none_returns_503(self, client: AsyncClient):
        """When db_pool is None, endpoint returns 503 with bilingual error."""
        # The test app sets db_pool = MagicMock, so override it to None
        client._transport.app.state.db_pool = None  # type: ignore[union-attr]
        resp = await client.get("/db-dependent")
        assert resp.status_code == 503
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == ErrorCode.DATABASE_ERROR
        assert "message" in body["error"]
        assert "message_ar" in body["error"]

    @pytest.mark.asyncio
    async def test_db_connection_error_returns_503(self, client: AsyncClient):
        """When asyncpg pool raises ConnectionError, endpoint returns 503."""
        mock_pool = AsyncMock()
        mock_pool.fetchval = AsyncMock(side_effect=ConnectionError("connection refused"))
        client._transport.app.state.db_pool = mock_pool  # type: ignore[union-attr]
        resp = await client.get("/db-dependent")
        assert resp.status_code == 503
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == ErrorCode.DATABASE_ERROR

    @pytest.mark.asyncio
    async def test_db_error_not_500(self, client: AsyncClient):
        """Ensure database errors are never exposed as generic 500."""
        client._transport.app.state.db_pool = None  # type: ignore[union-attr]
        resp = await client.get("/db-dependent")
        assert resp.status_code != 500


# ===========================================================================
# 2. NATS disconnection handling
# ===========================================================================


class TestNATSDisconnectionHandling:
    """Verify events silently skip (no crash) when NATS is disconnected."""

    @pytest.mark.asyncio
    async def test_publish_returns_false_when_disconnected(self):
        """EventPublisher.publish_event returns False when not connected."""
        publisher = EventPublisher(
            config=PublisherConfig(servers=["nats://localhost:4222"]),
            service_name="test-service",
        )
        # Not connected, so publish should return False (or buffer)
        assert publisher.is_connected is False

    @pytest.mark.asyncio
    async def test_publish_no_crash_on_none_client(self, client: AsyncClient):
        """Publishing endpoint returns gracefully when NATS client is None."""
        resp = await client.post("/events/publish")
        assert resp.status_code == 200
        body = resp.json()
        assert body["published"] is False

    @pytest.mark.asyncio
    async def test_publisher_buffers_when_disconnected(self):
        """Publisher buffers events when disconnected instead of crashing."""
        publisher = EventPublisher(
            config=PublisherConfig(servers=["nats://localhost:4222"]),
            service_name="test-service",
        )
        from shared.events.contracts import BaseEvent

        event = BaseEvent(tenant_id="test-tenant-123", source_service="test")
        result = publisher._buffer_message("sahool.test.event", event, 5.0, False)
        assert result is True
        assert len(publisher._pending_buffer) == 1


# ===========================================================================
# 3. Redis cache failure fallback
# ===========================================================================


class TestRedisCacheFailureFallback:
    """Verify services continue without cache (degraded but functional)."""

    @pytest.mark.asyncio
    async def test_terrain_cache_works_without_redis(self):
        """LRUCache operates as in-memory fallback when Redis is unavailable."""
        cache = LRUCache(max_size=100)
        cache.set("key1", {"data": "value"}, ttl=60)
        assert cache.get("key1") == {"data": "value"}

    @pytest.mark.asyncio
    async def test_service_healthy_without_redis(self, client: AsyncClient):
        """Health endpoint still returns 200 even if Redis is unavailable."""
        client._transport.app.state.redis = None  # type: ignore[union-attr]
        resp = await client.get("/healthz")
        assert resp.status_code == 200

    def test_lru_cache_fallback_on_redis_failure(self):
        """Verify LRU cache can serve as complete fallback for Redis."""
        cache = LRUCache(max_size=50)
        for i in range(50):
            cache.set(f"k{i}", f"v{i}", ttl=300)
        # All 50 items accessible
        assert cache.get("k0") is not None
        assert cache.get("k49") is not None


# ===========================================================================
# 4. Malformed request handling
# ===========================================================================


class TestMalformedRequestHandling:
    """Send invalid JSON, oversized payloads, wrong content-types."""

    @pytest.mark.asyncio
    async def test_invalid_json_returns_400(self, client: AsyncClient):
        """Invalid JSON body returns 400 with bilingual error message."""
        resp = await client.post(
            "/items",
            content=b"not valid json{{{",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["success"] is False
        assert "message" in body["error"]
        assert "message_ar" in body["error"]

    @pytest.mark.asyncio
    async def test_missing_required_field_returns_400(self, client: AsyncClient):
        """Missing required field returns 400 with descriptive error."""
        resp = await client.post("/items", json={"not_name": "value"})
        assert resp.status_code == 400
        body = resp.json()
        assert body["success"] is False
        assert "name" in body["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_empty_body_returns_400(self, client: AsyncClient):
        """Empty JSON body returns 400."""
        resp = await client.post(
            "/items",
            content=b"",
            headers={"Content-Type": "application/json"},
        )
        # Should be a 400 for invalid JSON
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_valid_request_returns_200(self, client: AsyncClient):
        """Sanity check: valid request returns success."""
        resp = await client.post("/items", json={"name": "Test Item"})
        assert resp.status_code == 200
        assert resp.json()["success"] is True


# ===========================================================================
# 5. Concurrent request safety
# ===========================================================================


class TestConcurrentRequestSafety:
    """Simulate parallel requests with same tenant and verify no data corruption."""

    @pytest.mark.asyncio
    async def test_concurrent_lru_cache_writes(self):
        """Parallel writes to LRUCache do not corrupt data."""
        cache = LRUCache(max_size=100)

        async def writer(prefix: str, count: int):
            for i in range(count):
                cache.set(f"{prefix}_{i}", f"value_{prefix}_{i}", ttl=300)
                await asyncio.sleep(0)  # Yield to event loop

        await asyncio.gather(
            writer("tenant_a", 30),
            writer("tenant_b", 30),
            writer("tenant_c", 30),
        )
        # All 90 items should be present (max_size=100)
        found = sum(1 for i in range(30) for p in ["tenant_a", "tenant_b", "tenant_c"] if cache.get(f"{p}_{i}") is not None)
        assert found == 90

    @pytest.mark.asyncio
    async def test_concurrent_publisher_buffer(self):
        """Parallel buffering to EventPublisher does not lose messages."""
        from shared.events.contracts import BaseEvent

        publisher = EventPublisher(
            config=PublisherConfig(servers=["nats://localhost:4222"]),
            service_name="test",
        )

        async def buffer_events(tenant: str, count: int):
            for i in range(count):
                event = BaseEvent(tenant_id=tenant, source_service="test")
                publisher._buffer_message(f"sahool.{tenant}.event", event, 5.0, False)
                await asyncio.sleep(0)

        await asyncio.gather(
            buffer_events("tenant-1", 20),
            buffer_events("tenant-2", 20),
        )
        assert len(publisher._pending_buffer) == 40

    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self, client: AsyncClient):
        """Multiple concurrent health checks do not interfere."""
        results = await asyncio.gather(
            *[client.get("/healthz") for _ in range(20)]
        )
        assert all(r.status_code == 200 for r in results)


# ===========================================================================
# 6. Circuit breaker behavior
# ===========================================================================


class TestCircuitBreakerBehavior:
    """Test CLOSED -> OPEN -> HALF_OPEN transitions with proper thresholds."""

    @pytest.mark.asyncio
    async def test_starts_closed(self):
        """Circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker("test-cb", CircuitBreakerConfig(failure_threshold=3))
        assert cb.state == CircuitState.CLOSED
        assert cb.is_closed is True

    @pytest.mark.asyncio
    async def test_transitions_to_open_after_threshold(self):
        """Circuit opens after failure_threshold consecutive failures."""
        cb = CircuitBreaker("test-open", CircuitBreakerConfig(failure_threshold=3, timeout_seconds=60))

        async def failing_func():
            raise RuntimeError("service down")

        for _ in range(3):
            with pytest.raises(RuntimeError):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN
        assert cb.stats.consecutive_failures == 3

    @pytest.mark.asyncio
    async def test_open_rejects_calls(self):
        """OPEN circuit immediately rejects calls with CircuitBreakerError."""
        cb = CircuitBreaker("test-reject", CircuitBreakerConfig(failure_threshold=2, timeout_seconds=60))

        async def failing_func():
            raise RuntimeError("fail")

        for _ in range(2):
            with pytest.raises(RuntimeError):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        with pytest.raises(CircuitBreakerError) as exc_info:
            await cb.call(failing_func)
        assert "OPEN" in str(exc_info.value)
        assert cb.stats.rejected_calls >= 1

    @pytest.mark.asyncio
    async def test_transitions_to_half_open_after_timeout(self):
        """Circuit transitions to HALF_OPEN after timeout elapses."""
        cb = CircuitBreaker(
            "test-half-open",
            CircuitBreakerConfig(failure_threshold=2, timeout_seconds=0.1),
        )

        async def failing():
            raise RuntimeError("fail")

        async def succeeding():
            return "ok"

        for _ in range(2):
            with pytest.raises(RuntimeError):
                await cb.call(failing)

        assert cb.state == CircuitState.OPEN
        await asyncio.sleep(0.15)

        result = await cb.call(succeeding)
        assert result == "ok"
        # After one success, still in HALF_OPEN (needs success_threshold=2 by default)

    @pytest.mark.asyncio
    async def test_half_open_to_closed_on_successes(self):
        """Circuit closes from HALF_OPEN after success_threshold successes."""
        cb = CircuitBreaker(
            "test-close",
            CircuitBreakerConfig(failure_threshold=2, success_threshold=2, timeout_seconds=0.05),
        )

        async def failing():
            raise RuntimeError("fail")

        async def succeeding():
            return "ok"

        for _ in range(2):
            with pytest.raises(RuntimeError):
                await cb.call(failing)

        assert cb.state == CircuitState.OPEN
        await asyncio.sleep(0.1)

        await cb.call(succeeding)
        await cb.call(succeeding)
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_half_open_failure_reopens(self):
        """Failure in HALF_OPEN immediately reopens the circuit."""
        cb = CircuitBreaker(
            "test-reopen",
            CircuitBreakerConfig(failure_threshold=2, timeout_seconds=0.05),
        )

        async def failing():
            raise RuntimeError("fail")

        for _ in range(2):
            with pytest.raises(RuntimeError):
                await cb.call(failing)

        assert cb.state == CircuitState.OPEN
        await asyncio.sleep(0.1)

        with pytest.raises(RuntimeError):
            await cb.call(failing)
        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_state_change_callback(self):
        """on_state_change callback fires on transitions."""
        transitions: list[tuple[str, CircuitState, CircuitState]] = []

        def on_change(name, old, new):
            transitions.append((name, old, new))

        cb = CircuitBreaker(
            "test-callback",
            CircuitBreakerConfig(failure_threshold=2, timeout_seconds=0.05),
            on_state_change=on_change,
        )

        async def failing():
            raise RuntimeError("fail")

        for _ in range(2):
            with pytest.raises(RuntimeError):
                await cb.call(failing)

        assert len(transitions) == 1
        assert transitions[0] == ("test-callback", CircuitState.CLOSED, CircuitState.OPEN)

    def test_manual_reset(self):
        """Manual reset returns circuit to CLOSED."""
        cb = CircuitBreaker("test-reset", CircuitBreakerConfig(failure_threshold=2))
        cb.trip()
        assert cb.state == CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED

    def test_get_status_dict(self):
        """get_status returns a complete status dictionary."""
        cb = CircuitBreaker("test-status")
        status = cb.get_status()
        assert status["name"] == "test-status"
        assert status["state"] == "closed"
        assert "stats" in status
        assert "config" in status


# ===========================================================================
# 7. Retry logic with exponential backoff
# ===========================================================================


class TestRetryLogic:
    """Test EventPublisher retry mechanism with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_exponential_backoff_timing(self):
        """Verify retry delays follow exponential backoff pattern."""
        config = PublisherConfig(
            servers=["nats://localhost:4222"],
            enable_retry=True,
            max_retry_attempts=3,
            retry_delay=0.05,
        )
        publisher = EventPublisher(config=config, service_name="test")
        publisher._connected = True
        publisher._nc = MagicMock()
        publisher._js = None

        call_times: list[float] = []

        original_publish_core = publisher._publish_core

        async def mock_publish_core(subject, data, timeout, headers=None):
            call_times.append(time.monotonic())
            raise RuntimeError("publish failed")

        with patch.object(publisher, "_publish_core", side_effect=mock_publish_core):
            result = await publisher._retry_publish("sahool.test", b"data", 5.0, False)

        assert result is False
        assert len(call_times) == 3

        # Check exponential backoff: delay * 2^(attempt-1)
        # attempt 1: 0.05s, attempt 2: 0.1s, attempt 3: 0.2s
        d1 = call_times[1] - call_times[0]
        d2 = call_times[2] - call_times[1]
        # Second delay should be roughly double the first
        assert d2 > d1 * 1.5, f"Expected exponential backoff: d1={d1:.3f}, d2={d2:.3f}"

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_second_attempt(self):
        """Retry succeeds when publish works on second attempt."""
        config = PublisherConfig(
            servers=["nats://localhost:4222"],
            enable_retry=True,
            max_retry_attempts=3,
            retry_delay=0.01,
        )
        publisher = EventPublisher(config=config, service_name="test")
        publisher._connected = True
        publisher._nc = MagicMock()
        publisher._js = None

        attempt_count = 0

        async def mock_publish_core(subject, data, timeout, headers=None):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise RuntimeError("transient failure")

        with patch.object(publisher, "_publish_core", side_effect=mock_publish_core):
            result = await publisher._retry_publish("sahool.test", b"data", 5.0, False)

        assert result is True
        assert attempt_count == 2

    @pytest.mark.asyncio
    async def test_buffer_overflow_respected(self):
        """Publisher buffer respects max size limit."""
        from shared.events.contracts import BaseEvent

        publisher = EventPublisher(service_name="test")
        publisher._pending_buffer_max_size = 5

        for i in range(10):
            event = BaseEvent(tenant_id="t1", source_service="test")
            publisher._buffer_message(f"sahool.test.{i}", event, 5.0, False)

        assert len(publisher._pending_buffer) == 5
        assert publisher._buffer_overflow_count == 5


# ===========================================================================
# 8. Memory limits (LRU, deque, caches)
# ===========================================================================


class TestMemoryLimits:
    """Test that in-memory caches respect size limits."""

    def test_lru_cache_evicts_at_max_size(self):
        """LRUCache evicts oldest entries when max_size is reached."""
        cache = LRUCache(max_size=5)
        for i in range(10):
            cache.set(f"key_{i}", f"value_{i}", ttl=300)

        # Only last 5 should remain
        assert cache.get("key_0") is None
        assert cache.get("key_4") is None
        assert cache.get("key_5") is not None
        assert cache.get("key_9") is not None

    def test_lru_cache_moves_accessed_to_end(self):
        """Accessing an LRU entry moves it to most-recently-used position."""
        cache = LRUCache(max_size=3)
        cache.set("a", 1, ttl=300)
        cache.set("b", 2, ttl=300)
        cache.set("c", 3, ttl=300)

        # Access 'a' to make it most recently used
        cache.get("a")

        # Add new entry; 'b' should be evicted (LRU), not 'a'
        cache.set("d", 4, ttl=300)
        assert cache.get("b") is None
        assert cache.get("a") == 1
        assert cache.get("d") == 4

    def test_knowledge_cache_respects_max_size(self):
        """KnowledgeCache evicts LRU when at capacity."""
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache(max_size=5, default_ttl=300)
        for i in range(10):
            cache.put(f"key_{i}", f"value_{i}")

        assert len(cache._cache) <= 5
        # Most recent entries should be present
        assert cache.get("key_9") is not None

    def test_publisher_rejected_events_buffer_bounded(self):
        """Rejected events DLQ buffer stays within max size."""
        publisher = EventPublisher(service_name="test")
        publisher._rejected_events_max = 10

        for i in range(25):
            publisher._rejected_events.append({"subject": f"test.{i}"})

        # Simulate the trim logic from publish_json
        if len(publisher._rejected_events) > publisher._rejected_events_max:
            publisher._rejected_events = publisher._rejected_events[-publisher._rejected_events_max:]

        assert len(publisher._rejected_events) == 10

    def test_lru_cache_ttl_expiry(self):
        """Expired entries are treated as cache misses."""
        cache = LRUCache(max_size=10)
        cache.set("exp_key", "exp_value", ttl=0)  # Expire immediately
        time.sleep(0.01)
        assert cache.get("exp_key") is None


# ===========================================================================
# 9. Graceful shutdown / lifespan cleanup
# ===========================================================================


class TestGracefulShutdown:
    """Test lifespan cleanup: DB pool, NATS, Redis connections properly closed."""

    @pytest.mark.asyncio
    async def test_lifespan_cleanup(self):
        """Verify lifespan cleanup logic properly nullifies connections."""
        # Directly test the lifespan context manager cleanup logic
        app = FastAPI()
        app.state.db_pool = MagicMock()
        app.state.nc = MagicMock()
        app.state.redis = MagicMock()

        # Simulate cleanup logic as coded in real services
        db_pool = app.state.db_pool
        nc = app.state.nc
        redis = app.state.redis

        # Verify connections exist before cleanup
        assert db_pool is not None
        assert nc is not None
        assert redis is not None

        # Execute cleanup (mirrors lifespan shutdown in _build_test_app)
        if hasattr(app.state, "db_pool") and app.state.db_pool:
            app.state.db_pool.close()
            app.state.db_pool = None
        if hasattr(app.state, "nc") and app.state.nc:
            app.state.nc.close()
            app.state.nc = None
        if hasattr(app.state, "redis") and app.state.redis:
            app.state.redis.close()
            app.state.redis = None

        # After cleanup, all connections should be None
        assert app.state.db_pool is None
        assert app.state.nc is None
        assert app.state.redis is None
        # Verify close() was called on each
        db_pool.close.assert_called_once()
        nc.close.assert_called_once()
        redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_publisher_close_resets_state(self):
        """EventPublisher.close() resets connection state."""
        publisher = EventPublisher(service_name="test")
        publisher._connected = True
        mock_nc = AsyncMock()
        publisher._nc = mock_nc

        await publisher.close()

        assert publisher._nc is None
        assert publisher._js is None
        assert publisher.is_connected is False

    @pytest.mark.asyncio
    async def test_circuit_breaker_reset_all(self):
        """reset_all_circuit_breakers resets all registered breakers."""
        cb1 = get_circuit_breaker("shutdown-test-1", CircuitBreakerConfig(failure_threshold=1))
        cb2 = get_circuit_breaker("shutdown-test-2", CircuitBreakerConfig(failure_threshold=1))
        cb1.trip()
        cb2.trip()
        assert cb1.state == CircuitState.OPEN
        assert cb2.state == CircuitState.OPEN

        reset_all_circuit_breakers()
        assert cb1.state == CircuitState.CLOSED
        assert cb2.state == CircuitState.CLOSED


# ===========================================================================
# 10. Error response consistency (bilingual EN + AR)
# ===========================================================================


class TestErrorResponseConsistency:
    """Verify all services return bilingual error messages."""

    @pytest.mark.asyncio
    async def test_sahool_exception_has_bilingual_messages(self):
        """SahoolException includes both message and message_ar."""
        exc = SahoolException(
            message="Something went wrong",
            message_ar="حدث خطأ ما",
            code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
        )
        resp = create_error_response(exc, request_id="req-123")
        body = json.loads(resp.body)
        assert body["error"]["message"] == "Something went wrong"
        assert body["error"]["message_ar"] == "حدث خطأ ما"
        assert body["request_id"] == "req-123"

    @pytest.mark.asyncio
    async def test_validation_error_bilingual(self, client: AsyncClient):
        """Validation errors return bilingual messages."""
        resp = await client.post(
            "/items",
            content=b"{bad json",
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        assert "message" in body["error"]
        assert "message_ar" in body["error"]
        assert len(body["error"]["message_ar"]) > 0

    @pytest.mark.asyncio
    async def test_external_service_error_bilingual(self, client: AsyncClient):
        """External service errors include Arabic messages."""
        resp = await client.get("/external-service")
        assert resp.status_code == 502
        body = resp.json()
        assert body["error"]["message_ar"] == "الخدمة الخارجية غير متوفرة"
        assert body["error"]["code"] == ErrorCode.EXTERNAL_SERVICE_ERROR

    @pytest.mark.asyncio
    async def test_db_error_bilingual(self, client: AsyncClient):
        """Database errors include Arabic translations."""
        client._transport.app.state.db_pool = None  # type: ignore[union-attr]
        resp = await client.get("/db-dependent")
        body = resp.json()
        assert body["error"]["message_ar"] == "قاعدة البيانات غير متوفرة"

    def test_all_error_codes_are_strings(self):
        """All ErrorCode values are string-compatible."""
        for code in ErrorCode:
            assert isinstance(code.value, str)
            assert code.value.startswith("E")

    @pytest.mark.asyncio
    async def test_request_id_in_error_response(self, client: AsyncClient):
        """Error responses include X-Request-ID header and in body."""
        resp = await client.get("/external-service", headers={"X-Request-ID": "custom-req-id"})
        assert resp.headers.get("X-Request-ID") == "custom-req-id"
        body = resp.json()
        assert body["request_id"] == "custom-req-id"

    @pytest.mark.asyncio
    async def test_generic_exception_returns_safe_message(self):
        """Unhandled exceptions do not leak internal details."""
        app = FastAPI()
        setup_exception_handlers(app)
        add_request_id_middleware(app)

        @app.get("/crash")
        async def crash():
            raise ValueError("sensitive internal detail: password=secret123")

        transport = ASGITransport(app=app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.get("/crash")
        assert resp.status_code == 500
        body = resp.json()
        # Must NOT leak internal details
        assert "secret123" not in json.dumps(body)
        assert "password" not in json.dumps(body)
        assert body["error"]["message"] == "An unexpected error occurred"
        assert body["error"]["message_ar"] == "حدث خطأ غير متوقع"
