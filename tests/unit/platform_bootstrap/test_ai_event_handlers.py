"""
Tests for AI Advisor event handlers.

يغطي هذه الاختبارات:
- معالجة JSON مشوه (ACK بدون crash)
- توليد yield prediction عند NDVI منخفض
- عدم توليد prediction عند NDVI عالي
- توصية ري عند رطوبة منخفضة
- تأخير ري عند هطول مطر غزير
- تنبيه موجة حر
- التحقق من prediction_type (subject injection)
- حدود cache (max size + TTL)
- فشل publish لا يمنع ACK
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.event_handlers import (
    AIEventHandlers,
    _ALLOWED_PREDICTION_TYPES,
    _CACHE_MAX_SIZE,
    _CACHE_TTL_SECONDS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_msg(data: dict) -> MagicMock:
    msg = MagicMock()
    msg.data = json.dumps(data).encode()
    msg.ack = AsyncMock()
    return msg


def _make_event(data: dict, tenant_id: str = "t-1") -> dict:
    return {"data": data, "tenant_id": tenant_id}


@pytest.fixture()
def handlers():
    h = AIEventHandlers()
    h.bus = AsyncMock()
    return h


# ===========================================================================
# JSON error handling — all handlers must ACK malformed messages
# ===========================================================================


class TestJsonErrorHandling:
    @pytest.mark.asyncio
    async def test_ndvi_bad_json_acks(self, handlers):
        msg = MagicMock()
        msg.data = b"NOT JSON"
        msg.ack = AsyncMock()
        await handlers.on_ndvi_update(msg)
        msg.ack.assert_awaited_once()
        handlers.bus.publish_event.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_sensor_bad_json_acks(self, handlers):
        msg = MagicMock()
        msg.data = b"{broken"
        msg.ack = AsyncMock()
        await handlers.on_sensor_data(msg)
        msg.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_weather_bad_json_acks(self, handlers):
        msg = MagicMock()
        msg.data = b""
        msg.ack = AsyncMock()
        await handlers.on_weather_update(msg)
        msg.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_prediction_bad_json_acks(self, handlers):
        msg = MagicMock()
        msg.data = None  # TypeError path
        msg.ack = AsyncMock()
        await handlers.on_prediction_request(msg)
        msg.ack.assert_awaited_once()


# ===========================================================================
# NDVI handler
# ===========================================================================


class TestNDVIHandler:
    @pytest.mark.asyncio
    async def test_low_ndvi_triggers_prediction(self, handlers):
        event = _make_event({"field_id": "f-1", "ndvi_index": 0.2})
        msg = _make_msg(event)
        await handlers.on_ndvi_update(msg)
        handlers.bus.publish_event.assert_awaited_once()
        call_kwargs = handlers.bus.publish_event.call_args[1]
        assert call_kwargs["domain"] == "ai"
        assert call_kwargs["action"] == "yield-prediction.updated"
        assert call_kwargs["tenant_id"] == "t-1"
        assert call_kwargs["data"]["predicted_yield_tons"] <= 15.0
        msg.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_high_ndvi_does_not_publish(self, handlers):
        event = _make_event({"field_id": "f-1", "ndvi_index": 0.7})
        msg = _make_msg(event)
        await handlers.on_ndvi_update(msg)
        handlers.bus.publish_event.assert_not_awaited()
        msg.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_ndvi_caches_value(self, handlers):
        event = _make_event({"field_id": "f-99", "ndvi_index": 0.65})
        msg = _make_msg(event)
        await handlers.on_ndvi_update(msg)
        cached = handlers._cache_get(handlers.ndvi_cache, "f-99")
        assert cached is not None
        assert cached["value"] == 0.65

    @pytest.mark.asyncio
    async def test_yield_capped_at_15(self, handlers):
        """Even with ndvi=0.29 (below 0.3 threshold), yield must not exceed 15."""
        event = _make_event({"field_id": "f-1", "ndvi_index": 0.29})
        msg = _make_msg(event)
        await handlers.on_ndvi_update(msg)
        yield_val = handlers.bus.publish_event.call_args[1]["data"]["predicted_yield_tons"]
        assert yield_val <= 15.0


# ===========================================================================
# Sensor data handler
# ===========================================================================


class TestSensorHandler:
    @pytest.mark.asyncio
    async def test_low_moisture_triggers_irrigation(self, handlers):
        event = _make_event({"field_id": "f-1", "moisture_level": 20})
        msg = _make_msg(event)
        await handlers.on_sensor_data(msg)
        handlers.bus.publish_event.assert_awaited_once()
        data = handlers.bus.publish_event.call_args[1]["data"]
        assert data["trigger"] == "low_moisture"
        assert data["current_moisture"] == 20

    @pytest.mark.asyncio
    async def test_normal_moisture_no_action(self, handlers):
        event = _make_event({"field_id": "f-1", "moisture_level": 50})
        msg = _make_msg(event)
        await handlers.on_sensor_data(msg)
        handlers.bus.publish_event.assert_not_awaited()
        msg.ack.assert_awaited_once()


# ===========================================================================
# Weather handler
# ===========================================================================


class TestWeatherHandler:
    @pytest.mark.asyncio
    async def test_heavy_rain_delays_irrigation(self, handlers):
        event = _make_event({"region": "tihama", "rainfall_mm": 80, "temperature_c": 25})
        msg = _make_msg(event)
        await handlers.on_weather_update(msg)
        call_kwargs = handlers.bus.publish_event.call_args[1]
        assert call_kwargs["action"] == "irrigation.adjusted"
        assert call_kwargs["data"]["adjustment"] == "delay_48h"

    @pytest.mark.asyncio
    async def test_heat_wave_alert(self, handlers):
        event = _make_event({"region": "riyadh", "rainfall_mm": 0, "temperature_c": 45})
        msg = _make_msg(event)
        await handlers.on_weather_update(msg)
        call_kwargs = handlers.bus.publish_event.call_args[1]
        assert call_kwargs["action"] == "heat-wave.alert"
        assert call_kwargs["data"]["temperature_c"] == 45

    @pytest.mark.asyncio
    async def test_normal_weather_no_action(self, handlers):
        event = _make_event({"region": "jeddah", "rainfall_mm": 5, "temperature_c": 30})
        msg = _make_msg(event)
        await handlers.on_weather_update(msg)
        handlers.bus.publish_event.assert_not_awaited()


# ===========================================================================
# Prediction request handler
# ===========================================================================


class TestPredictionRequest:
    @pytest.mark.asyncio
    async def test_yield_prediction_uses_cache(self, handlers):
        handlers._cache_put(handlers.ndvi_cache, "f-1", {"value": 0.6})
        event = _make_event({"field_id": "f-1", "type": "yield"})
        msg = _make_msg(event)
        result = await handlers.on_prediction_request(msg)
        assert result["type"] == "yield"
        assert result["predicted_yield_tons"] == min(round(2.5 * 0.6 * 100, 2), 15.0)

    @pytest.mark.asyncio
    async def test_disease_prediction(self, handlers):
        event = _make_event({"field_id": "f-1", "type": "disease"})
        msg = _make_msg(event)
        result = await handlers.on_prediction_request(msg)
        assert result["type"] == "disease"
        assert result["risk_level"] == "low"

    @pytest.mark.asyncio
    async def test_unknown_type_returns_error(self, handlers):
        event = _make_event({"field_id": "f-1", "type": "magic"})
        msg = _make_msg(event)
        result = await handlers.on_prediction_request(msg)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_invalid_prediction_type_sanitized(self, handlers):
        """prediction_type with special chars must be sanitized to 'unknown'."""
        event = _make_event({"field_id": "f-1", "type": "../../../etc/passwd"})
        msg = _make_msg(event)
        await handlers.on_prediction_request(msg)
        action = handlers.bus.publish_event.call_args[1]["action"]
        assert "prediction.unknown.completed" == action

    @pytest.mark.asyncio
    async def test_valid_unknown_type_kept_as_is(self, handlers):
        """A safe but unknown type (lowercase alphanumeric) is kept."""
        event = _make_event({"field_id": "f-1", "type": "custom-model"})
        msg = _make_msg(event)
        await handlers.on_prediction_request(msg)
        action = handlers.bus.publish_event.call_args[1]["action"]
        assert action == "prediction.custom-model.completed"


# ===========================================================================
# Publish failure resilience
# ===========================================================================


class TestPublishFailure:
    @pytest.mark.asyncio
    async def test_ndvi_publish_failure_still_acks(self, handlers):
        handlers.bus.publish_event.side_effect = Exception("NATS down")
        event = _make_event({"field_id": "f-1", "ndvi_index": 0.1})
        msg = _make_msg(event)
        await handlers.on_ndvi_update(msg)
        msg.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sensor_publish_failure_still_acks(self, handlers):
        handlers.bus.publish_event.side_effect = Exception("NATS down")
        event = _make_event({"field_id": "f-1", "moisture_level": 10})
        msg = _make_msg(event)
        await handlers.on_sensor_data(msg)
        msg.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_prediction_publish_failure_still_acks(self, handlers):
        handlers.bus.publish_event.side_effect = Exception("timeout")
        event = _make_event({"field_id": "f-1", "type": "yield"})
        msg = _make_msg(event)
        await handlers.on_prediction_request(msg)
        msg.ack.assert_awaited_once()


# ===========================================================================
# Cache behaviour
# ===========================================================================


class TestCache:
    def test_cache_put_and_get(self, handlers):
        handlers._cache_put(handlers.ndvi_cache, "f-1", {"value": 0.5})
        entry = handlers._cache_get(handlers.ndvi_cache, "f-1")
        assert entry is not None
        assert entry["value"] == 0.5

    def test_cache_get_missing_key(self, handlers):
        assert handlers._cache_get(handlers.ndvi_cache, "missing") is None

    def test_cache_evicts_oldest_when_full(self, handlers):
        for i in range(_CACHE_MAX_SIZE + 5):
            handlers._cache_put(handlers.ndvi_cache, f"f-{i}", {"value": i})
        assert len(handlers.ndvi_cache) == _CACHE_MAX_SIZE

    def test_cache_ttl_expiry(self, handlers):
        handlers.ndvi_cache["f-old"] = {
            "value": 0.3,
            "cached_at": "2020-01-01T00:00:00+00:00",  # Long expired
        }
        assert handlers._cache_get(handlers.ndvi_cache, "f-old") is None
        assert "f-old" not in handlers.ndvi_cache  # evicted
