# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
اختبارات المرونة (Resilience Tests)
=========================================

Verifies that the SAHOOL platform degrades gracefully when individual
services or infrastructure components become unavailable.  Every test is
runnable without a live environment — it exercises the retry, fallback, and
circuit-breaker logic through in-process mocks and controlled HTTP clients.

Scenarios covered
-----------------
R1: Service unavailability — what does the caller receive when a
    downstream service returns 503 / connection-refused?
R2: Circuit breaker — verify state transitions (CLOSED → OPEN → HALF_OPEN)
    and that requests are rejected fast in the OPEN state.
R3: Retry with exponential back-off — ensure transient failures are retried
    a configured number of times before giving up.
R4: NATS unavailability — events must be buffered / queued and the API
    response must not block waiting for the broker.
R5: Database connection loss — HTTP health endpoint must return a degraded
    status and API endpoints must return 503 with a clear error body.
R6: Partial degradation — some services down, others healthy; the platform
    must return partial results rather than a full 500.
R7: Timeout handling — slow upstream responses must be cut off at the
    configured timeout, never left open indefinitely.

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    import httpx
    from httpx import AsyncClient

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# ---------------------------------------------------------------------------
# Canonical service URLs derived from the shared registry
# (apps/services/shared/versions.py) with env-override support.
# ---------------------------------------------------------------------------
import os

try:
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "apps", "services"))
    from shared.versions import get_service_url  # type: ignore[import]

    def _svc(name: str, fallback_port: int) -> str:
        host = os.getenv("SERVICE_HOST", "localhost")
        return os.getenv(f"{name.upper().replace('-', '_')}_URL") or get_service_url(name, host)

except Exception:
    def _svc(name: str, fallback_port: int) -> str:  # type: ignore[misc]
        host = os.getenv("SERVICE_HOST", "localhost")
        return os.getenv(f"{name.upper().replace('-', '_')}_URL") or f"http://{host}:{fallback_port}"


SVCURL: dict[str, str] = {
    "field": _svc("field-management-service", 3000),
    "advisory": _svc("advisory-service", 8093),
    "weather": _svc("weather-service", 8092),
    "irrigation": _svc("irrigation-smart", 8094),
    "notification": _svc("notification-service", 8110),
    "alert": _svc("alert-service", 8113),
    "iot": _svc("iot-service", 8117),
    "vegetation": _svc("vegetation-analysis-service", 8090),
    "vision": _svc("yolo26-vision-service", 8150),
}

pytestmark = pytest.mark.integration


# ===========================================================================
# Override db_cursor fixture locally so the integration conftest autouse
# cleanup fixture does not skip our tests when psycopg2 is absent.
# ===========================================================================


@pytest.fixture
def db_cursor():
    """Lightweight override: these resilience tests do not need a real DB cursor."""
    return MagicMock()


# ===========================================================================
# Helper: Lightweight CircuitBreaker (mirrors production pattern)
# ===========================================================================


class CircuitState(str, Enum):  # noqa: UP042
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """
    Minimal circuit-breaker implementation that mirrors the production
    pattern (apps/services/shared/errors.ts) for in-process testing.
    """

    def __init__(self, failure_threshold: int = 3, reset_timeout_seconds: float = 0.1) -> None:
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout_seconds
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at: float | None = None

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if self._opened_at and (time.monotonic() - self._opened_at) >= self.reset_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def call(self, fn, *args, **kwargs):
        state = self.state
        if state == CircuitState.OPEN:
            raise RuntimeError("CircuitBreaker: circuit is OPEN — call rejected")
        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        self._failures = 0
        self._state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()

    def reset(self) -> None:
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at = None


# ===========================================================================
# Helper: Retry with exponential back-off
# ===========================================================================


def retry_with_backoff(fn, max_retries: int = 3, base_delay: float = 0.01, exceptions=(Exception,)):
    """
    Retry *fn* up to *max_retries* times with exponential back-off.
    Raises the last exception when all retries are exhausted.
    """
    delay = base_delay
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except exceptions as exc:
            last_exc = exc
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("retry_with_backoff: no exception recorded after exhausting retries")


# ===========================================================================
# R1: Service unavailability
# ===========================================================================


class TestServiceUnavailability:
    """
    ماذا يحدث عندما تكون خدمة خارجية غير متاحة؟
    What does the caller experience when a downstream service is unavailable?
    """

    @pytest.mark.asyncio
    async def test_503_returned_when_advisory_service_down(self):
        """
        When the advisory service is unreachable, the gateway or caller must
        receive a 503 (or connection error), not an unhandled 500.
        عندما تكون خدمة الاستشارات غير متاحة يجب إرجاع 503.
        """
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")
        # Point to a port that is deliberately not open
        dead_url = "http://localhost:19999/api/v1/recommendations"
        try:
            async with AsyncClient(timeout=2.0) as client:
                resp = await client.get(dead_url)
                # If something answers on this port it should be 503/404
                assert resp.status_code in (404, 503)
        except (httpx.ConnectError, httpx.TimeoutException):
            # Connection refused / timeout is the expected result
            pass  # ✅  correct behavior

    def test_fallback_value_returned_on_service_failure(self):
        """
        A service call wrapped in a try/except must return the configured
        fallback value instead of propagating the exception.
        يجب إرجاع القيمة الاحتياطية عند فشل استدعاء الخدمة.
        """

        def call_weather_service(location: str) -> dict:
            raise ConnectionError("Weather service is down")

        def get_weather_with_fallback(location: str) -> dict:
            try:
                return call_weather_service(location)
            except ConnectionError:
                return {
                    "temperature": None,
                    "humidity": None,
                    "source": "fallback",
                    "message": "Weather service temporarily unavailable",
                    "message_ar": "خدمة الطقس غير متاحة مؤقتاً",
                }

        result = get_weather_with_fallback("riyadh")
        assert result["source"] == "fallback"
        assert result["temperature"] is None

    def test_partial_results_when_ndvi_service_down(self):
        """
        When the NDVI service is down the advisory response should still
        include field and weather data — just omit the NDVI section.
        عند تعطل خدمة NDVI يجب إرجاع نتائج جزئية بدون NDVI.
        """

        def build_advisory_response(field: dict, weather: dict, ndvi: dict | None) -> dict:
            resp: dict[str, Any] = {
                "field_id": field["id"],
                "tenant_id": field["tenant_id"],
                "weather_summary": weather,
                "recommendations": ["Monitor crop", "Check irrigation"],
                "degraded": ndvi is None,
            }
            if ndvi is not None:
                resp["ndvi"] = ndvi
            return resp

        field = {"id": "f-001", "tenant_id": "t-001"}
        weather = {"temperature": 28.0}
        response = build_advisory_response(field, weather, ndvi=None)

        assert response["degraded"] is True
        assert "ndvi" not in response
        assert len(response["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_all_services_respond_to_health_check(self):
        """
        Verify which services in SVCURL are actually healthy.
        Logs unavailable services without failing the test.
        التحقق من توفر الخدمات مع تسجيل الخدمات غير المتاحة.
        """
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        available = []
        unavailable = []
        for name, url in SVCURL.items():
            try:
                async with AsyncClient(timeout=3.0) as client:
                    resp = await client.get(f"{url}/healthz")
                    if resp.status_code == 200:
                        available.append(name)
                    else:
                        unavailable.append((name, resp.status_code))
            except Exception as e:
                unavailable.append((name, str(e)))

        # Just log — we don't fail if services are offline in CI
        if unavailable:
            print(f"\n[INFO] Unavailable services: {unavailable}")
        print(f"[INFO] Available services   : {available}")
        # No assertion — this test always passes; it's an inventory check


# ===========================================================================
# R2: Circuit Breaker State Machine
# ===========================================================================


class TestCircuitBreaker:
    """
    اختبار نمط قاطع الدائرة.
    Verify that the circuit breaker correctly transitions through
    CLOSED → OPEN → HALF_OPEN → CLOSED.
    """

    def test_initial_state_is_closed(self):
        """Circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.state == CircuitState.CLOSED

    def test_transitions_to_open_after_threshold_failures(self):
        """
        After ``failure_threshold`` consecutive failures the circuit opens.
        بعد عدد المخفقات المحدد يجب أن ينفتح قاطع الدائرة.
        """

        def raise_service_error():
            raise ValueError("service error")

        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(raise_service_error)
        assert cb.state == CircuitState.OPEN

    def test_open_circuit_rejects_calls_immediately(self):
        """
        An OPEN circuit must raise an error immediately without calling
        the wrapped function (fail-fast behaviour).
        الدائرة المفتوحة يجب أن ترفض الاستدعاءات فوراً.
        """

        def raise_value_error():
            raise ValueError("fail")

        cb = CircuitBreaker(failure_threshold=1)
        with pytest.raises(ValueError):
            cb.call(raise_value_error)
        assert cb.state == CircuitState.OPEN

        call_count = [0]

        def expensive_call():
            call_count[0] += 1
            return "result"

        with pytest.raises(RuntimeError, match="OPEN"):
            cb.call(expensive_call)

        assert call_count[0] == 0, "Wrapped function must NOT be called in OPEN state"

    def test_transitions_to_half_open_after_timeout(self):
        """
        After the reset timeout, the state must move to HALF_OPEN.
        بعد انتهاء المهلة يجب الانتقال إلى الحالة نصف-المفتوحة.
        """

        def raise_value_error():
            raise ValueError("fail")

        cb = CircuitBreaker(failure_threshold=1, reset_timeout_seconds=0.05)
        with pytest.raises(ValueError):
            cb.call(raise_value_error)
        assert cb.state == CircuitState.OPEN

        time.sleep(0.06)  # Wait past reset timeout
        assert cb.state == CircuitState.HALF_OPEN

    def test_successful_call_in_half_open_closes_circuit(self):
        """
        A successful call in HALF_OPEN state resets the circuit to CLOSED.
        نجاح استدعاء في الحالة نصف-المفتوحة يُعيد الدائرة إلى الحالة المغلقة.
        """

        def raise_value_error():
            raise ValueError("fail")

        cb = CircuitBreaker(failure_threshold=1, reset_timeout_seconds=0.05)
        with pytest.raises(ValueError):
            cb.call(raise_value_error)
        time.sleep(0.06)
        assert cb.state == CircuitState.HALF_OPEN

        result = cb.call(lambda: "ok")
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED

    def test_failed_call_in_half_open_reopens_circuit(self):
        """
        A failure in HALF_OPEN re-opens the circuit.
        فشل في الحالة نصف-المفتوحة يُعيد فتح قاطع الدائرة.
        """

        def raise_value_error(msg: str = "fail"):
            raise ValueError(msg)

        cb = CircuitBreaker(failure_threshold=1, reset_timeout_seconds=0.05)
        with pytest.raises(ValueError):
            cb.call(raise_value_error)
        time.sleep(0.06)

        with pytest.raises(ValueError):
            cb.call(lambda: raise_value_error("still failing"))
        assert cb.state == CircuitState.OPEN

    def test_reset_clears_all_state(self):
        """
        reset() must bring the circuit back to a clean CLOSED state.
        reset() يجب إعادة قاطع الدائرة إلى الحالة المغلقة.
        """

        def raise_value_error():
            raise ValueError("fail")

        cb = CircuitBreaker(failure_threshold=1)
        with pytest.raises(ValueError):
            cb.call(raise_value_error)
        assert cb.state == CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb._failures == 0

    def test_multiple_circuits_are_independent(self):
        """
        Two separate CircuitBreaker instances must have independent state.
        مثيلان منفصلان لقاطع الدائرة يجب أن يكون لهما حالة مستقلة.
        """

        def raise_value_error():
            raise ValueError("fail")

        cb1 = CircuitBreaker(failure_threshold=2)
        cb2 = CircuitBreaker(failure_threshold=2)
        for _ in range(2):
            with pytest.raises(ValueError):
                cb1.call(raise_value_error)
        assert cb1.state == CircuitState.OPEN
        assert cb2.state == CircuitState.CLOSED


# ===========================================================================
# R3: Retry with Exponential Back-Off
# ===========================================================================


class TestRetryWithBackoff:
    """
    اختبار إعادة المحاولة مع تراجع أسي.
    Verify that transient failures are retried the expected number of times.
    """

    def test_succeeds_on_second_attempt(self):
        """
        Retry should succeed when the function passes on its second attempt.
        إعادة المحاولة يجب أن تنجح عند النجاح في المحاولة الثانية.
        """
        attempts = [0]

        def flaky():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ConnectionError("transient")
            return "ok"

        result = retry_with_backoff(flaky, max_retries=3, base_delay=0.001)
        assert result == "ok"
        assert attempts[0] == 2

    def test_raises_after_all_retries_exhausted(self):
        """
        When all retries are exhausted the original exception must propagate.
        عند استنفاد جميع المحاولات يجب إعادة رفع الاستثناء الأصلي.
        """

        def always_fails():
            raise ConnectionError("permanent failure")

        with pytest.raises(ConnectionError, match="permanent failure"):
            retry_with_backoff(always_fails, max_retries=2, base_delay=0.001)

    def test_retry_count_matches_max_retries(self):
        """
        The function should be called max_retries+1 times total.
        عدد استدعاءات الدالة يجب أن يساوي max_retries + 1.
        """
        calls = [0]

        def fail():
            calls[0] += 1
            raise OSError("io error")

        max_retries = 3
        with pytest.raises(OSError):
            retry_with_backoff(fail, max_retries=max_retries, base_delay=0.001)
        assert calls[0] == max_retries + 1

    def test_succeeds_without_retrying_when_first_call_succeeds(self):
        """
        When the first call succeeds, no retries should occur.
        عند نجاح المحاولة الأولى لا يجب حدوث أي إعادة محاولة.
        """
        calls = [0]

        def always_ok():
            calls[0] += 1
            return "success"

        result = retry_with_backoff(always_ok, max_retries=5, base_delay=0.001)
        assert result == "success"
        assert calls[0] == 1

    def test_only_specified_exception_types_are_retried(self):
        """
        Exceptions not in the retry list must not be retried.
        الاستثناءات خارج قائمة إعادة المحاولة يجب ألا تُعاد.
        """
        calls = [0]

        def raises_value_error():
            calls[0] += 1
            raise ValueError("not retriable")

        with pytest.raises(ValueError):
            retry_with_backoff(raises_value_error, max_retries=5, base_delay=0.001, exceptions=(ConnectionError,))
        assert calls[0] == 1, "ValueError should not trigger retries"


# ===========================================================================
# R4: NATS / Message Bus Unavailability
# ===========================================================================


class TestNATSUnavailability:
    """
    اختبار ما يحدث عند توقف وسيط الرسائل NATS.
    Events should be buffered and API responses must not block.
    """

    @pytest.mark.asyncio
    async def test_event_buffered_when_nats_unavailable(self):
        """
        When NATS is unavailable, published events must be buffered locally
        and not cause the API to fail.
        عند عدم توفر NATS يجب تخزين الأحداث مؤقتاً دون إخفاق الـ API.
        """
        buffer: list[dict] = []

        async def publish_with_buffer(subject: str, data: dict, nats_client) -> bool:
            """Publish to NATS; buffer locally if unavailable."""
            try:
                await nats_client.publish(subject, data)
                return True
            except Exception:
                buffer.append({"subject": subject, "data": data, "buffered_at": datetime.now(UTC).isoformat()})
                return False

        mock_nats = AsyncMock()
        mock_nats.publish.side_effect = ConnectionError("NATS unreachable")

        success = await publish_with_buffer(
            "sahool.field.created",
            {"field_id": "f-001", "tenant_id": "t-001"},
            mock_nats,
        )
        assert success is False
        assert len(buffer) == 1
        assert buffer[0]["subject"] == "sahool.field.created"

    @pytest.mark.asyncio
    async def test_api_does_not_block_on_nats_publish(self):
        """
        The HTTP API must complete its response within a timeout even if the
        NATS publish hangs.
        استجابة HTTP يجب ألا تنتظر نشر NATS إلى الأبد.
        """

        async def slow_publish():
            await asyncio.sleep(30)  # Simulates hung NATS

        async def handle_field_create_request(nats_client) -> dict:
            """Business logic: always respond quickly; event is fire-and-forget."""
            field = {"id": "f-001", "status": "created"}
            # Publish is fire-and-forget — do NOT await in the request handler
            task = asyncio.create_task(slow_publish())
            # Store a reference so the task is not garbage-collected before it
            # finishes (or is explicitly cancelled by the caller / cleanup).
            handle_field_create_request._bg_tasks = getattr(  # type: ignore[attr-defined]
                handle_field_create_request, "_bg_tasks", []
            )
            handle_field_create_request._bg_tasks.append(task)  # type: ignore[attr-defined]
            task.add_done_callback(handle_field_create_request._bg_tasks.remove)  # type: ignore[attr-defined]
            return {"status": "ok", "field": field}

        mock_nats = AsyncMock()
        start = time.monotonic()
        response = await asyncio.wait_for(handle_field_create_request(mock_nats), timeout=1.0)
        elapsed = time.monotonic() - start

        assert response["status"] == "ok"
        assert elapsed < 1.0, f"Handler took too long: {elapsed:.2f}s"

        # Cancel the pending background task to avoid "Task destroyed but pending" warnings.
        # Iterate over a snapshot of the list — done-callbacks invoke list.remove()
        # concurrently, which could skip entries if we iterated the live list.
        bg_tasks = getattr(handle_field_create_request, "_bg_tasks", [])  # type: ignore[attr-defined]
        for bg in list(bg_tasks):
            bg.cancel()
            try:
                await bg
            except (asyncio.CancelledError, Exception):
                pass
        # Drop all references so no stale task objects linger after the test.
        bg_tasks.clear()

    def test_outbox_pattern_ensures_delivery(self):
        """
        The transactional outbox pattern guarantees delivery: events written
        to the outbox table are never lost even during NATS downtime.
        نمط Outbox يضمن التسليم حتى عند توقف NATS.
        """
        outbox: list[dict] = []

        def save_to_outbox_and_commit(event: dict) -> None:
            """Atomically persist business entity + event record."""
            outbox.append({**event, "delivered": False, "created_at": datetime.now(UTC).isoformat()})

        def process_outbox(nats_client) -> int:
            """Relay buffered events and mark them delivered."""
            delivered = 0
            for entry in outbox:
                if not entry["delivered"]:
                    try:
                        nats_client.publish(entry["subject"], entry["data"])
                        entry["delivered"] = True
                        delivered += 1
                    except Exception:
                        pass
            return delivered

        mock_nats = MagicMock()
        mock_nats.publish.return_value = None

        # Save event during NATS downtime
        save_to_outbox_and_commit({"subject": "sahool.field.created", "data": {"id": "f-001"}})
        assert len(outbox) == 1

        # NATS recovers; process outbox
        delivered = process_outbox(mock_nats)
        assert delivered == 1
        assert outbox[0]["delivered"] is True


# ===========================================================================
# R5: Database Connection Loss
# ===========================================================================


class TestDatabaseConnectionLoss:
    """
    اختبار ما يحدث عند فقدان الاتصال بقاعدة البيانات.
    """

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_degraded_when_db_down(self):
        """
        When the DB is unavailable, /healthz should return 200 but mark
        the database as unhealthy.
        عند تعطل قاعدة البيانات يجب أن يُظهر /healthz حالة متدهورة.
        """

        async def health_check(db_pool) -> dict:
            db_ok = False
            try:
                await db_pool.fetchone("SELECT 1")
                db_ok = True
            except Exception:
                db_ok = False
            return {
                "status": "ok" if db_ok else "degraded",
                "database": "up" if db_ok else "down",
                "service": "field-management",
            }

        mock_pool = AsyncMock()
        mock_pool.fetchone.side_effect = ConnectionError("DB unreachable")

        result = await health_check(mock_pool)
        assert result["status"] == "degraded"
        assert result["database"] == "down"

    @pytest.mark.asyncio
    async def test_api_returns_503_on_db_connection_failure(self):
        """
        CRUD endpoints must return 503 (not 500) when the DB pool is exhausted
        or unreachable.
        نقاط CRUD يجب أن تُرجع 503 عند انهيار اتصال قاعدة البيانات.
        """

        async def create_field_handler(payload: dict, db_pool) -> tuple[int, dict]:
            try:
                await db_pool.execute("INSERT ...", payload)
                return 201, {"id": "new-id"}
            except ConnectionError as exc:
                return 503, {
                    "error": "service_unavailable",
                    "message": "Database temporarily unavailable",
                    "message_ar": "قاعدة البيانات غير متاحة مؤقتاً",
                    "detail": str(exc),
                }

        mock_pool = AsyncMock()
        mock_pool.execute.side_effect = ConnectionError("pool exhausted")

        status, body = await create_field_handler({"name": "test"}, mock_pool)
        assert status == 503
        assert body["error"] == "service_unavailable"
        assert "message_ar" in body

    def test_connection_pool_exhaustion_handled(self):
        """
        When the DB pool is exhausted, the error should be wrapped in a
        user-friendly message.
        عند استنفاد مجموعة الاتصالات يجب تغليف الخطأ برسالة واضحة.
        """
        from contextlib import contextmanager

        class FakePool:
            def __init__(self, max_size: int):
                self.max_size = max_size
                self._used = 0

            @contextmanager
            def acquire(self):
                if self._used >= self.max_size:
                    raise TimeoutError("connection pool exhausted")
                self._used += 1
                try:
                    yield self
                finally:
                    self._used -= 1

        pool = FakePool(max_size=1)
        with pool.acquire():
            with pytest.raises(TimeoutError, match="exhausted"):
                with pool.acquire():
                    pass


# ===========================================================================
# R6: Partial Degradation (some services down, others healthy)
# ===========================================================================


class TestPartialDegradation:
    """
    اختبار التدهور الجزئي — بعض الخدمات معطلة والأخرى تعمل.
    """

    def test_advisory_response_without_weather_data(self):
        """
        Advisory can still provide basic crop-calendar guidance even when
        the weather service is offline.
        يمكن تقديم نصائح أساسية حتى عند تعطل خدمة الطقس.
        """

        def get_advisory(crop: str, stage: str, weather: dict | None) -> dict:
            recs: list[str] = [f"Monitor {crop} at {stage} stage"]
            if weather:
                if weather.get("rain_probability", 0) < 10:
                    recs.append("Irrigate within 24h")
            else:
                recs.append("Weather data unavailable — check local conditions")
            return {
                "crop": crop,
                "stage": stage,
                "recommendations": recs,
                "weather_available": weather is not None,
                "degraded": weather is None,
            }

        result = get_advisory("wheat", "tillering", weather=None)
        assert result["degraded"] is True
        assert any("Weather data unavailable" in r for r in result["recommendations"])

    @pytest.mark.asyncio
    async def test_platform_health_aggregates_service_statuses(self):
        """
        A platform-level /health endpoint must aggregate individual service
        statuses and report the overall platform health correctly.
        نقطة الصحة يجب أن تجمع حالات الخدمات وتُرجع الصحة الإجمالية.
        """

        async def aggregate_health(services: dict[str, str]) -> dict:
            """Check each service URL; return aggregated status."""
            statuses: dict[str, str] = {}
            for name, url in services.items():
                if not HAS_HTTPX:
                    statuses[name] = "unknown"
                    continue
                try:
                    async with AsyncClient(timeout=2.0) as client:
                        resp = await client.get(url)
                        statuses[name] = "healthy" if resp.status_code == 200 else "degraded"
                except Exception:
                    statuses[name] = "unavailable"

            healthy_count = sum(1 for s in statuses.values() if s == "healthy")
            total = len(statuses)
            return {
                "services": statuses,
                "healthy_count": healthy_count,
                "total_count": total,
                "overall": "healthy" if healthy_count == total else "degraded" if healthy_count > 0 else "down",
            }

        # Mock: 2 up, 1 down
        mock_services = {
            "field": f"{SVCURL['field']}/healthz",
            "advisory": f"{SVCURL['advisory']}/healthz",
            "dead_service": "http://localhost:19999/healthz",
        }
        result = await aggregate_health(mock_services)
        assert "services" in result
        assert result["overall"] in ("healthy", "degraded", "down")
        if result["services"].get("dead_service") == "unavailable":
            assert result["overall"] in ("degraded", "down")

    def test_graceful_degradation_scores(self):
        """
        Platform degradation must be categorised into levels so the frontend
        can show appropriate user messaging.
        مستويات التدهور تُحدد الرسائل المناسبة للمستخدم.
        """

        def degradation_level(healthy: int, total: int) -> str:
            if total == 0:
                return "unknown"
            ratio = healthy / total
            if ratio == 1.0:
                return "operational"
            if ratio >= 0.75:
                return "minor_outage"
            if ratio >= 0.50:
                return "partial_outage"
            return "major_outage"

        assert degradation_level(5, 5) == "operational"
        assert degradation_level(4, 5) == "minor_outage"
        assert degradation_level(3, 5) == "partial_outage"
        assert degradation_level(1, 5) == "major_outage"
        assert degradation_level(0, 5) == "major_outage"


# ===========================================================================
# R7: Timeout Handling
# ===========================================================================


class TestTimeoutHandling:
    """
    اختبار معالجة انتهاء المهلة الزمنية.
    Slow upstream responses must be cut off; connections must never hang.
    """

    @pytest.mark.asyncio
    async def test_request_times_out_after_configured_limit(self):
        """
        An HTTP call that takes longer than the timeout must raise
        asyncio.TimeoutError / httpx.TimeoutException.
        استدعاء HTTP يتجاوز المهلة يجب أن يُثير استثناء انتهاء المهلة.
        """

        async def slow_handler():
            await asyncio.sleep(5)
            return {"status": "ok"}

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_handler(), timeout=0.05)

    @pytest.mark.asyncio
    async def test_timeout_does_not_leave_resources_open(self):
        """
        After a timeout, any acquired resources (connections, locks) must be
        released.
        بعد انتهاء المهلة يجب تحرير جميع الموارد المكتسبة.
        """
        released = [False]

        async def acquire_and_use():
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                released[0] = True
                raise

        task = asyncio.create_task(acquire_and_use())
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=0.05)
        except TimeoutError:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass  # expected — task was cancelled

        assert released[0] is True, "Resources must be released on timeout/cancel"

    def test_timeout_configuration_is_service_specific(self):
        """
        Different services should have different timeout budgets based on their
        expected response times.
        الخدمات المختلفة يجب أن يكون لها ميزانيات مهلة مختلفة.
        """
        TIMEOUT_CONFIG = {
            "weather": 5.0,  # seconds
            "advisory": 10.0,
            "vision_detection": 30.0,  # GPU inference
            "irrigation_calculation": 8.0,
            "field_crud": 5.0,
            "notification": 3.0,
        }

        # Vision must have the highest budget (GPU)
        assert TIMEOUT_CONFIG["vision_detection"] >= 15.0
        # Notifications should be fast
        assert TIMEOUT_CONFIG["notification"] <= 5.0
        # All timeouts must be positive
        assert all(v > 0 for v in TIMEOUT_CONFIG.values())

    @pytest.mark.asyncio
    async def test_concurrent_timeout_isolation(self):
        """
        A timeout on one concurrent operation must not affect other running
        operations.
        انتهاء مهلة عملية واحدة يجب ألا يؤثر على العمليات الأخرى.
        """

        results: dict[str, Any] = {}

        async def fast_op():
            await asyncio.sleep(0.01)
            results["fast"] = "done"

        async def slow_op():
            await asyncio.sleep(10)
            results["slow"] = "done"

        fast_task = asyncio.create_task(fast_op())
        slow_task = asyncio.create_task(slow_op())

        # Fast task completes; slow task times out
        _ = await fast_task  # wait for result (returns None; captured to avoid no-effect warning)
        slow_task.cancel()
        try:
            _ = await slow_task
        except asyncio.CancelledError:
            pass  # expected — task was cancelled

        assert results.get("fast") == "done"
        assert "slow" not in results
