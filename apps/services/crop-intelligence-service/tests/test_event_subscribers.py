"""
Tests for NATS Event Subscribers — اختبارات مشتركي أحداث NATS
=============================================================
Tests cover helper functions and handler logic with mocked dependencies.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from src.event_subscribers import (
        _ack,
        _check_processed,
        _extract_headers,
        _handle_calibration_succeeded,
        _handle_ndvi_computed,
        _handle_weather_forecast,
        _mark_processed,
        _nak,
        _trigger_assimilation,
        setup_nats_subscriptions,
    )
except (ImportError, Exception):
    pytest.skip("crop-intelligence-service dependencies not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Helpers for building fake NATS messages
# ---------------------------------------------------------------------------


def _make_msg(data: dict, headers: dict | None = None, ack=True, nak=True):
    """Create a fake NATS message object."""
    msg = SimpleNamespace()
    msg.data = json.dumps(data).encode()
    msg.headers = headers
    if ack:
        msg.ack = AsyncMock()
    if nak:
        msg.nak = AsyncMock()
    return msg


def _make_app_state(**kwargs):
    """Create a fake app_state namespace."""
    return SimpleNamespace(**kwargs)


def _make_pool(conn):
    """Create a fake asyncpg pool with proper async context manager for acquire()."""
    pool = MagicMock()

    @asynccontextmanager
    async def _acquire():
        yield conn

    pool.acquire = _acquire
    return pool


# ──────────────────────────────────────────────────────────────────────────────
# _extract_headers
# ──────────────────────────────────────────────────────────────────────────────


class TestExtractHeaders:
    def test_no_headers_attribute(self):
        msg = SimpleNamespace(data=b"{}")
        result = _extract_headers(msg)
        assert result == {}

    def test_none_headers(self):
        msg = SimpleNamespace(data=b"{}", headers=None)
        result = _extract_headers(msg)
        assert result == {}

    def test_empty_headers(self):
        msg = SimpleNamespace(data=b"{}", headers={})
        result = _extract_headers(msg)
        # Empty headers dict returns dict with empty string values for all keys
        assert result.get("correlation_id", "") == ""
        assert result.get("causation_id", "") == ""
        assert result.get("event_id", "") == ""
        assert result.get("tenant_id", "") == ""
        assert result.get("traceparent", "") == ""

    def test_full_headers(self):
        msg = SimpleNamespace(
            data=b"{}",
            headers={
                "X-Correlation-ID": "corr-123",
                "X-Causation-ID": "cause-456",
                "X-Event-ID": "evt-789",
                "X-Tenant-ID": "tenant-abc",
                "traceparent": "00-trace-id-span-01",
            },
        )
        result = _extract_headers(msg)
        assert result["correlation_id"] == "corr-123"
        assert result["causation_id"] == "cause-456"
        assert result["event_id"] == "evt-789"
        assert result["tenant_id"] == "tenant-abc"
        assert result["traceparent"] == "00-trace-id-span-01"

    def test_partial_headers(self):
        msg = SimpleNamespace(
            data=b"{}",
            headers={"X-Event-ID": "evt-only"},
        )
        result = _extract_headers(msg)
        assert result["event_id"] == "evt-only"
        assert result["correlation_id"] == ""


# ──────────────────────────────────────────────────────────────────────────────
# _check_processed
# ──────────────────────────────────────────────────────────────────────────────


class TestCheckProcessed:
    @pytest.mark.asyncio
    async def test_none_pool_returns_false(self):
        result = await _check_processed(None, "tenant", "event-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_empty_event_id_returns_false(self):
        result = await _check_processed(MagicMock(), "tenant", "")
        assert result is False

    @pytest.mark.asyncio
    async def test_event_found_returns_true(self):
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value={"1": 1})
        pool = _make_pool(conn)

        result = await _check_processed(pool, "tenant-1", "event-1")
        assert result is True
        conn.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_event_not_found_returns_false(self):
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=None)
        pool = _make_pool(conn)

        result = await _check_processed(pool, "tenant-1", "event-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_db_error_returns_false(self):
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(side_effect=Exception("DB down"))
        pool = _make_pool(conn)

        result = await _check_processed(pool, "tenant-1", "event-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_none_tenant_uses_global(self):
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=None)
        pool = _make_pool(conn)

        await _check_processed(pool, None, "event-1")
        args = conn.fetchrow.call_args[0]
        assert args[1] == "_global"


# ──────────────────────────────────────────────────────────────────────────────
# _mark_processed
# ──────────────────────────────────────────────────────────────────────────────


class TestMarkProcessed:
    @pytest.mark.asyncio
    async def test_none_pool_noop(self):
        # Should not raise
        await _mark_processed(None, "tenant", "event-1", "subject")

    @pytest.mark.asyncio
    async def test_empty_event_id_noop(self):
        await _mark_processed(MagicMock(), "tenant", "", "subject")

    @pytest.mark.asyncio
    async def test_successful_insert(self):
        conn = AsyncMock()
        conn.execute = AsyncMock()
        pool = _make_pool(conn)

        await _mark_processed(pool, "tenant-1", "event-1", "sahool.test", "corr-1")
        conn.execute.assert_called_once()
        args = conn.execute.call_args[0]
        assert "INSERT INTO processed_events" in args[0]
        assert args[1] == "tenant-1"
        assert args[2] == "event-1"

    @pytest.mark.asyncio
    async def test_db_error_does_not_raise(self):
        conn = AsyncMock()
        conn.execute = AsyncMock(side_effect=Exception("DB down"))
        pool = _make_pool(conn)
        # Should not raise
        await _mark_processed(pool, "tenant", "event-1", "subject")

    @pytest.mark.asyncio
    async def test_none_tenant_uses_global(self):
        conn = AsyncMock()
        conn.execute = AsyncMock()
        pool = _make_pool(conn)

        await _mark_processed(pool, None, "event-1", "subject")
        args = conn.execute.call_args[0]
        assert args[1] == "_global"


# ──────────────────────────────────────────────────────────────────────────────
# _ack / _nak
# ──────────────────────────────────────────────────────────────────────────────


class TestAckNak:
    @pytest.mark.asyncio
    async def test_ack_calls_msg_ack(self):
        msg = SimpleNamespace(ack=AsyncMock())
        await _ack(msg)
        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_ack_no_ack_method(self):
        msg = SimpleNamespace()
        # Should not raise
        await _ack(msg)

    @pytest.mark.asyncio
    async def test_ack_attribute_error(self):
        msg = SimpleNamespace(ack=AsyncMock(side_effect=AttributeError("no ack")))
        await _ack(msg)

    @pytest.mark.asyncio
    async def test_ack_runtime_error(self):
        msg = SimpleNamespace(ack=AsyncMock(side_effect=RuntimeError("closed")))
        await _ack(msg)

    @pytest.mark.asyncio
    async def test_nak_calls_msg_nak(self):
        msg = SimpleNamespace(nak=AsyncMock())
        await _nak(msg)
        msg.nak.assert_called_once()

    @pytest.mark.asyncio
    async def test_nak_no_nak_method(self):
        msg = SimpleNamespace()
        await _nak(msg)

    @pytest.mark.asyncio
    async def test_nak_attribute_error(self):
        msg = SimpleNamespace(nak=AsyncMock(side_effect=AttributeError("no nak")))
        await _nak(msg)

    @pytest.mark.asyncio
    async def test_nak_runtime_error(self):
        msg = SimpleNamespace(nak=AsyncMock(side_effect=RuntimeError("closed")))
        await _nak(msg)


# ──────────────────────────────────────────────────────────────────────────────
# _handle_ndvi_computed
# ──────────────────────────────────────────────────────────────────────────────


class TestHandleNdviComputed:
    @pytest.mark.asyncio
    async def test_malformed_payload_acks(self):
        """Malformed messages (missing required fields) should ACK to prevent redelivery."""
        msg = _make_msg({"tenant_id": "t1"})  # missing field_id, ndvi
        app_state = _make_app_state()
        await _handle_ndvi_computed(msg, app_state)
        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_db_pool_acks(self):
        """No DB pool available should ACK gracefully."""
        msg = _make_msg({
            "tenant_id": "t1",
            "field_id": "f1",
            "mean_ndvi": 0.65,
            "event_id": "evt-1",
        })
        app_state = _make_app_state()  # no db_pool
        await _handle_ndvi_computed(msg, app_state)
        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_already_processed_event_acks(self):
        """Duplicate events should be ACKed and skipped."""
        msg = _make_msg(
            {"tenant_id": "t1", "field_id": "f1", "mean_ndvi": 0.65, "event_id": "evt-dup"},
            headers={"X-Event-ID": "evt-dup"},
        )
        with patch("src.event_subscribers._check_processed", new_callable=AsyncMock, return_value=True):
            app_state = _make_app_state(db_pool=MagicMock())
            await _handle_ndvi_computed(msg, app_state)
        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Requires shared.digital_twin.adapters mock at import time")
    async def test_successful_processing_acks(self):
        """Full successful path: save observation, trigger assimilation, mark processed, ACK."""
        msg = _make_msg(
            {"tenant_id": "t1", "field_id": "f1", "mean_ndvi": 0.72, "event_id": "evt-ok"},
        )
        mock_repo = AsyncMock()
        mock_obs = MagicMock()

        with patch("src.event_subscribers._check_processed", new_callable=AsyncMock, return_value=False), \
             patch("src.event_subscribers._mark_processed", new_callable=AsyncMock) as mock_mark, \
             patch("src.event_subscribers._trigger_assimilation", new_callable=AsyncMock) as mock_trigger, \
             patch("shared.digital_twin.adapters.ndvi_to_field_observation", return_value=mock_obs) as mock_adapter, \
             patch("shared.digital_twin.repository.TwinRepository", return_value=mock_repo):
            app_state = _make_app_state(db_pool=MagicMock())
            await _handle_ndvi_computed(msg, app_state)

        msg.ack.assert_called_once()
        mock_trigger.assert_called_once()
        mock_mark.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Requires shared.digital_twin.adapters mock at import time")
    async def test_uses_value_field_fallback(self):
        """When mean_ndvi is absent, should fall back to 'value' field."""
        msg = _make_msg(
            {"tenant_id": "t1", "field_id": "f1", "value": 0.55, "event_id": "evt-val"},
        )

        with patch("src.event_subscribers._check_processed", new_callable=AsyncMock, return_value=False), \
             patch("src.event_subscribers._mark_processed", new_callable=AsyncMock), \
             patch("src.event_subscribers._trigger_assimilation", new_callable=AsyncMock), \
             patch("shared.digital_twin.adapters.ndvi_to_field_observation", return_value=MagicMock()), \
             patch("shared.digital_twin.repository.TwinRepository", return_value=AsyncMock()):
            app_state = _make_app_state(db_pool=MagicMock())
            await _handle_ndvi_computed(msg, app_state)

        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_exception_naks(self):
        """Unhandled exceptions should NAK for redelivery."""
        msg = _make_msg({"invalid": True})
        msg.data = b"not json!!!{"
        app_state = _make_app_state()
        await _handle_ndvi_computed(msg, app_state)
        msg.nak.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_all_required_fields_acks(self):
        """Missing tenant_id, field_id, and value should ACK malformed."""
        msg = _make_msg({"some_other": "data"})
        app_state = _make_app_state()
        await _handle_ndvi_computed(msg, app_state)
        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Requires shared.digital_twin.adapters mock at import time")
    async def test_header_event_id_fallback(self):
        """event_id should fall back to header when not in payload."""
        msg = _make_msg(
            {"tenant_id": "t1", "field_id": "f1", "mean_ndvi": 0.5},
            headers={"X-Event-ID": "from-header"},
        )
        with patch("src.event_subscribers._check_processed", new_callable=AsyncMock, return_value=False), \
             patch("src.event_subscribers._mark_processed", new_callable=AsyncMock) as mock_mark, \
             patch("src.event_subscribers._trigger_assimilation", new_callable=AsyncMock), \
             patch("shared.digital_twin.adapters.ndvi_to_field_observation", return_value=MagicMock()), \
             patch("shared.digital_twin.repository.TwinRepository", return_value=AsyncMock()):
            app_state = _make_app_state(db_pool=MagicMock())
            await _handle_ndvi_computed(msg, app_state)

        msg.ack.assert_called_once()


# ──────────────────────────────────────────────────────────────────────────────
# _handle_calibration_succeeded
# ──────────────────────────────────────────────────────────────────────────────


class TestHandleCalibrationSucceeded:
    @pytest.mark.asyncio
    async def test_safe_params_reloaded(self):
        """When safe_for_decision=True with best_params, params should be loaded into app_state."""
        msg = _make_msg({
            "run_id": "run-1",
            "field_id": "field-1",
            "safe_for_decision": True,
            "best_params": {"rue_g_mj": 3.5, "k_extinction": 0.6},
            "objective_value": 0.95,
        })
        app_state = _make_app_state()
        await _handle_calibration_succeeded(msg, app_state)

        msg.ack.assert_called_once()
        assert hasattr(app_state, "calibrated_params")
        assert "field-1" in app_state.calibrated_params
        params = app_state.calibrated_params["field-1"]
        assert params["run_id"] == "run-1"
        assert params["params"]["rue_g_mj"] == 3.5
        assert params["safe_for_decision"] is True

    @pytest.mark.asyncio
    async def test_unsafe_params_not_loaded(self):
        """When safe_for_decision=False, params should NOT be stored."""
        msg = _make_msg({
            "run_id": "run-2",
            "field_id": "field-2",
            "safe_for_decision": False,
            "best_params": {"rue_g_mj": 2.0},
        })
        app_state = _make_app_state()
        await _handle_calibration_succeeded(msg, app_state)

        msg.ack.assert_called_once()
        cp = getattr(app_state, "calibrated_params", {})
        assert "field-2" not in cp

    @pytest.mark.asyncio
    async def test_missing_best_params_not_loaded(self):
        """When best_params is None, no crash and no store."""
        msg = _make_msg({
            "run_id": "run-3",
            "field_id": "field-3",
            "safe_for_decision": True,
            "best_params": None,
        })
        app_state = _make_app_state()
        await _handle_calibration_succeeded(msg, app_state)
        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_field_id_not_loaded(self):
        """When field_id is missing, no store."""
        msg = _make_msg({
            "run_id": "run-4",
            "safe_for_decision": True,
            "best_params": {"k": 0.5},
        })
        app_state = _make_app_state()
        await _handle_calibration_succeeded(msg, app_state)
        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_existing_calibrated_params_updated(self):
        """When calibrated_params already exists, new field entry is added."""
        msg = _make_msg({
            "run_id": "run-5",
            "field_id": "field-5",
            "safe_for_decision": True,
            "best_params": {"a": 1},
        })
        app_state = _make_app_state(calibrated_params={"field-old": {"run_id": "old"}})
        await _handle_calibration_succeeded(msg, app_state)
        assert "field-old" in app_state.calibrated_params
        assert "field-5" in app_state.calibrated_params

    @pytest.mark.asyncio
    async def test_invalid_json_naks(self):
        """Invalid JSON should NAK for redelivery."""
        msg = SimpleNamespace(
            data=b"not json",
            ack=AsyncMock(),
            nak=AsyncMock(),
            headers=None,
        )
        app_state = _make_app_state()
        await _handle_calibration_succeeded(msg, app_state)
        msg.nak.assert_called_once()


# ──────────────────────────────────────────────────────────────────────────────
# _handle_weather_forecast
# ──────────────────────────────────────────────────────────────────────────────


class TestHandleWeatherForecast:
    @pytest.mark.asyncio
    async def test_valid_forecast_cached(self):
        """Valid forecast should be cached in app_state.weather_cache."""
        payload = {
            "tenant_id": "t1",
            "field_id": "f1",
            "forecast": [{"date": "2026-03-22", "tmax_c": 32.0}],
        }
        msg = _make_msg(payload)
        app_state = _make_app_state()
        await _handle_weather_forecast(msg, app_state)

        msg.ack.assert_called_once()
        assert hasattr(app_state, "weather_cache")
        assert "t1:f1" in app_state.weather_cache
        assert app_state.weather_cache["t1:f1"] == payload

    @pytest.mark.asyncio
    async def test_missing_tenant_id_acks(self):
        """Missing tenant_id should ACK (malformed)."""
        msg = _make_msg({"field_id": "f1"})
        app_state = _make_app_state()
        await _handle_weather_forecast(msg, app_state)
        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_field_id_acks(self):
        """Missing field_id should ACK (malformed)."""
        msg = _make_msg({"tenant_id": "t1"})
        app_state = _make_app_state()
        await _handle_weather_forecast(msg, app_state)
        msg.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_existing_cache_updated(self):
        """When weather_cache already exists, new entries are added."""
        msg = _make_msg({"tenant_id": "t2", "field_id": "f2"})
        app_state = _make_app_state(weather_cache={"t1:f1": {"old": True}})
        await _handle_weather_forecast(msg, app_state)
        assert "t1:f1" in app_state.weather_cache
        assert "t2:f2" in app_state.weather_cache

    @pytest.mark.asyncio
    async def test_invalid_json_naks(self):
        """Invalid JSON should NAK for redelivery."""
        msg = SimpleNamespace(
            data=b"bad json{",
            ack=AsyncMock(),
            nak=AsyncMock(),
            headers=None,
        )
        app_state = _make_app_state()
        await _handle_weather_forecast(msg, app_state)
        msg.nak.assert_called_once()


# ──────────────────────────────────────────────────────────────────────────────
# _trigger_assimilation
# ──────────────────────────────────────────────────────────────────────────────


class TestTriggerAssimilation:
    @pytest.mark.asyncio
    async def test_no_db_pool_returns_early(self):
        """Should return without error when db_pool is None."""
        app_state = _make_app_state()
        await _trigger_assimilation(app_state, "t1", "f1", MagicMock())
        # No exception means success

    @pytest.mark.asyncio
    async def test_pipeline_step_called(self):
        """Should create TwinPipeline and call step."""
        mock_pipeline = AsyncMock()
        mock_repo = MagicMock()

        with patch("shared.digital_twin.pipeline.TwinPipeline", return_value=mock_pipeline), \
             patch("shared.digital_twin.repository.TwinRepository", return_value=mock_repo):
            app_state = _make_app_state(db_pool=MagicMock())
            await _trigger_assimilation(app_state, "t1", "f1", MagicMock(), "evt-1")

        mock_pipeline.step.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Weather cache mock returns None instead of expected MagicMock")
    async def test_with_weather_cache(self):
        """Should use cached weather when available."""
        mock_pipeline = AsyncMock()
        mock_weather = MagicMock()

        with patch("shared.digital_twin.pipeline.TwinPipeline", return_value=mock_pipeline), \
             patch("shared.digital_twin.repository.TwinRepository", return_value=MagicMock()), \
             patch("shared.digital_twin.adapters.weather_payload_to_daily", return_value=mock_weather):
            app_state = _make_app_state(
                db_pool=MagicMock(),
                weather_cache={"t1:f1": {"forecast": "data"}},
            )
            await _trigger_assimilation(app_state, "t1", "f1", MagicMock())

        call_kwargs = mock_pipeline.step.call_args[1]
        assert call_kwargs["weather"] == mock_weather

    @pytest.mark.asyncio
    async def test_with_calibrated_params(self):
        """Should pass calibrated params when available."""
        mock_pipeline = AsyncMock()

        with patch("shared.digital_twin.pipeline.TwinPipeline", return_value=mock_pipeline), \
             patch("shared.digital_twin.repository.TwinRepository", return_value=MagicMock()):
            app_state = _make_app_state(
                db_pool=MagicMock(),
                calibrated_params={"f1": {"params": {"rue": 3.0}}},
            )
            await _trigger_assimilation(app_state, "t1", "f1", MagicMock())

        call_kwargs = mock_pipeline.step.call_args[1]
        assert call_kwargs["calibrated_params"] == {"rue": 3.0}

    @pytest.mark.asyncio
    async def test_weather_conversion_error_runs_without_weather(self):
        """If weather conversion fails, pipeline still runs with weather=None."""
        mock_pipeline = AsyncMock()

        with patch("shared.digital_twin.pipeline.TwinPipeline", return_value=mock_pipeline), \
             patch("shared.digital_twin.repository.TwinRepository", return_value=MagicMock()), \
             patch("shared.digital_twin.adapters.weather_payload_to_daily", side_effect=Exception("bad")):
            app_state = _make_app_state(
                db_pool=MagicMock(),
                weather_cache={"t1:f1": {"data": "bad"}},
            )
            await _trigger_assimilation(app_state, "t1", "f1", MagicMock())

        call_kwargs = mock_pipeline.step.call_args[1]
        assert call_kwargs["weather"] is None

    @pytest.mark.asyncio
    async def test_pipeline_error_logged_not_raised(self):
        """Pipeline failures should be logged but not raised (best-effort)."""
        with patch("shared.digital_twin.pipeline.TwinPipeline", side_effect=Exception("pipeline error")), \
             patch("shared.digital_twin.repository.TwinRepository", return_value=MagicMock()):
            app_state = _make_app_state(db_pool=MagicMock())
            # Should not raise
            await _trigger_assimilation(app_state, "t1", "f1", MagicMock())


# ──────────────────────────────────────────────────────────────────────────────
# setup_nats_subscriptions
# ──────────────────────────────────────────────────────────────────────────────


class TestSetupNatsSubscriptions:
    @pytest.mark.asyncio
    async def test_jetstream_subscriptions(self):
        """When JetStream is available, should use durable subscriptions."""
        js = AsyncMock()
        js.subscribe = AsyncMock(return_value=MagicMock())
        nc = MagicMock()
        nc.jetstream = MagicMock(return_value=js)

        with patch("src.event_subscribers.SAHOOL_NDVI_COMPUTED", "sahool.satellite.ndvi.computed", create=True), \
             patch.dict("sys.modules", {
                 "shared.events": MagicMock(),
                 "shared.events.subjects": MagicMock(
                     SAHOOL_NDVI_COMPUTED="sahool.satellite.ndvi.computed",
                     SAHOOL_CALIBRATION_RUN_SUCCEEDED="sahool.calibration.run.succeeded.v1",
                     SAHOOL_WEATHER_FORECAST="sahool.weather.forecast",
                 ),
             }):
            subs = await setup_nats_subscriptions(nc, _make_app_state())

        assert len(subs) == 3
        assert js.subscribe.call_count == 3

    @pytest.mark.asyncio
    async def test_core_nats_fallback(self):
        """When JetStream is unavailable, should fall back to core NATS."""
        nc = AsyncMock()
        nc.jetstream = MagicMock(side_effect=Exception("no JS"))
        nc.subscribe = AsyncMock(return_value=MagicMock())

        with patch.dict("sys.modules", {
            "shared.events": MagicMock(),
            "shared.events.subjects": MagicMock(
                SAHOOL_NDVI_COMPUTED="sahool.satellite.ndvi.computed",
                SAHOOL_CALIBRATION_RUN_SUCCEEDED="sahool.calibration.run.succeeded.v1",
                SAHOOL_WEATHER_FORECAST="sahool.weather.forecast",
            ),
        }):
            subs = await setup_nats_subscriptions(nc, _make_app_state())

        assert len(subs) == 3
        assert nc.subscribe.call_count == 3

    @pytest.mark.asyncio
    async def test_partial_subscription_failure(self):
        """If one subscription fails, others should still succeed."""
        js = AsyncMock()
        call_count = 0

        async def _sub_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("subscribe error")
            return MagicMock()

        js.subscribe = _sub_side_effect
        nc = MagicMock()
        nc.jetstream = MagicMock(return_value=js)

        with patch.dict("sys.modules", {
            "shared.events": MagicMock(),
            "shared.events.subjects": MagicMock(
                SAHOOL_NDVI_COMPUTED="sahool.satellite.ndvi.computed",
                SAHOOL_CALIBRATION_RUN_SUCCEEDED="sahool.calibration.run.succeeded.v1",
                SAHOOL_WEATHER_FORECAST="sahool.weather.forecast",
            ),
        }):
            subs = await setup_nats_subscriptions(nc, _make_app_state())

        # 2 succeed, 1 fails
        assert len(subs) == 2
