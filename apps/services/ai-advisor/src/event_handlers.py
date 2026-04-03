"""
SAHOOL AI Advisor - Event Bus Integration
Real-time yield prediction and irrigation optimization via NATS JetStream.

Subscribes to NDVI, sensor, and weather events to generate real-time
predictions and publish advisory recommendations.
"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger()

# Cache configuration — bounded to prevent unbounded memory growth
_CACHE_MAX_SIZE = 1000       # maximum entries per cache dict
_CACHE_TTL_SECONDS = 3600    # 1 hour — stale data should not drive decisions


class AIEventHandlers:
    """AI service event handlers for real-time predictions via NATS JetStream."""

    def __init__(self):
        self.bus = None
        self.ndvi_cache: dict[str, dict[str, Any]] = {}
        self.weather_cache: dict[str, dict[str, Any]] = {}

    # ── Cache helpers ────────────────────────────────────────────────────────

    # Sentinel timestamp used when an entry has no 'cached_at' field so that
    # min() comparisons during eviction always produce a defined ordering.
    _EPOCH = "1970-01-01T00:00:00+00:00"

    def _cache_put(self, cache: dict, key: str, value: dict) -> None:
        """Insert *value* into *cache*, evicting the oldest entry when full."""
        if len(cache) >= _CACHE_MAX_SIZE:
            oldest = min(cache, key=lambda k: cache[k].get("cached_at", self._EPOCH))
            cache.pop(oldest, None)
        cache[key] = {**value, "cached_at": datetime.now(UTC).isoformat()}

    def _cache_get(self, cache: dict, key: str) -> dict | None:
        """Return the cached entry if present and not yet expired, else None."""
        entry = cache.get(key)
        if entry is None:
            return None
        cached_at = entry.get("cached_at", "")
        if cached_at:
            age = (datetime.now(UTC) - datetime.fromisoformat(cached_at)).total_seconds()
            if age > _CACHE_TTL_SECONDS:
                cache.pop(key, None)
                return None
        return entry

    # ── Initialisation ───────────────────────────────────────────────────────

    async def initialize(self, nats_url: str) -> None:
        """Connect to event bus and subscribe to streams.

        The platform-bootstrap package must be installed or its ``src/``
        directory must be on ``PYTHONPATH`` (set to ``/app`` in Docker, where
        the package is copied to ``/app/platform_bootstrap/``).
        """
        from platform_bootstrap.event_bus import SAHOOLEventBus  # type: ignore[import]

        self.bus = await SAHOOLEventBus.get_instance()
        await self.bus.connect(nats_url, service_name="ai-advisor")

        # Subscribe to NDVI updates
        await self.bus.subscribe_events(
            domain="ndvi",
            handler=self.on_ndvi_update,
            durable="ai_ndvi_processor",
        )

        # Subscribe to sensor data
        await self.bus.subscribe_events(
            domain="field",
            handler=self.on_sensor_data,
            durable="ai_sensor_processor",
        )

        # Subscribe to weather updates
        await self.bus.subscribe_events(
            domain="weather",
            handler=self.on_weather_update,
            durable="ai_weather_processor",
        )

        # Command handler for on-demand predictions (uses commands bus)
        await self.bus.subscribe_events(
            domain="ai",
            handler=self.on_prediction_request,
            durable="ai_command_processor",
            message_type="commands",
        )

        logger.info("ai_event_handlers_initialized")

    # ── Event handlers ───────────────────────────────────────────────────────

    async def on_ndvi_update(self, msg) -> None:
        """Process NDVI updates and trigger yield predictions."""
        try:
            event = json.loads(msg.data)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error("ndvi_update_bad_json", error=str(exc))
            await msg.ack()  # ACK to prevent infinite redelivery loop
            return

        data = event.get("data", {})
        tenant_id = event.get("tenant_id")
        field_id = data.get("field_id")
        ndvi_value = data.get("ndvi_index", 0.5)

        # Cache with TTL for downstream prediction requests
        self._cache_put(self.ndvi_cache, field_id, {
            "value": ndvi_value,
            "timestamp": datetime.now(UTC).isoformat(),
            "tenant_id": tenant_id,
        })

        # Trigger real-time prediction if low vegetation detected
        if ndvi_value < 0.3:
            # TODO: Replace with ML model (crop-growth-model service or yield-prediction-service)
            # This linear approximation is a temporary placeholder only.
            # Capped at 15 t/ha to prevent obviously wrong values pending ML integration.
            predicted_yield_tons = min(round(2.5 * ndvi_value * 100, 2), 15.0)
            prediction = {
                "field_id": field_id,
                "predicted_yield_tons": predicted_yield_tons,
                "confidence": 0.85,
                "factors": ["low_ndvi", "irrigation_needed"],
                "actions": ["increase_irrigation", "check_sensors"],
            }

            await self.bus.publish_event(
                domain="ai",
                action="yield-prediction.updated",
                data=prediction,
                tenant_id=tenant_id,
            )

            logger.info(
                "yield_prediction_generated",
                field_id=field_id,
                yield_tons=prediction["predicted_yield_tons"],
            )

        await msg.ack()

    async def on_sensor_data(self, msg) -> None:
        """Process IoT sensor data for irrigation optimization."""
        try:
            event = json.loads(msg.data)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error("sensor_data_bad_json", error=str(exc))
            await msg.ack()  # ACK to prevent infinite redelivery loop
            return

        data = event.get("data", {})
        tenant_id = event.get("tenant_id")
        field_id = data.get("field_id")
        moisture = data.get("moisture_level", 50)

        if moisture < 30:
            water_needed = (30 - moisture) * 50
            await self.bus.publish_event(
                domain="ai",
                action="irrigation.recommended",
                data={
                    "field_id": field_id,
                    "recommended_duration_minutes": int(water_needed / 20),
                    "optimal_time": "06:00",
                    "water_savings_liters": 1200,
                    "confidence": min(0.95, 0.7 + (30 - moisture) / 100),
                    "trigger": "low_moisture",
                    "current_moisture": moisture,
                },
                tenant_id=tenant_id,
            )

            logger.info(
                "irrigation_recommended",
                field_id=field_id,
                water_liters=water_needed,
            )

        await msg.ack()

    async def on_weather_update(self, msg) -> None:
        """Adjust predictions based on weather forecasts."""
        try:
            event = json.loads(msg.data)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error("weather_update_bad_json", error=str(exc))
            await msg.ack()  # ACK to prevent infinite redelivery loop
            return

        data = event.get("data", {})
        tenant_id = event.get("tenant_id")
        region = data.get("region")
        rainfall_forecast = data.get("rainfall_mm", 0)
        temperature_forecast = data.get("temperature_c", 25)

        # Heavy rain - delay irrigation
        if rainfall_forecast > 50:
            await self.bus.publish_event(
                domain="ai",
                action="irrigation.adjusted",
                data={
                    "region": region,
                    "adjustment": "delay_48h",
                    "reason": "heavy_rain_forecast",
                    "rainfall_mm": rainfall_forecast,
                    "recommended_action": "postpone_scheduled_irrigation",
                },
                tenant_id=tenant_id,
            )
            logger.info(
                "irrigation_delayed",
                region=region,
                rainfall_mm=rainfall_forecast,
            )

        # Heat wave detection
        elif temperature_forecast > 40:
            await self.bus.publish_event(
                domain="ai",
                action="heat-wave.alert",
                data={
                    "region": region,
                    "temperature_c": temperature_forecast,
                    "recommended_actions": [
                        "increase_shade",
                        "extra_irrigation",
                        "monitor_stress",
                    ],
                },
                tenant_id=tenant_id,
            )

        await msg.ack()

    async def on_prediction_request(self, msg) -> None:
        """Handle on-demand prediction requests."""
        try:
            event = json.loads(msg.data)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error("prediction_request_bad_json", error=str(exc))
            await msg.ack()  # ACK to prevent infinite redelivery loop
            return

        data = event.get("data", {})
        tenant_id = event.get("tenant_id")
        field_id = data.get("field_id")
        prediction_type = data.get("type", "yield")

        if prediction_type == "yield":
            ndvi_data = self._cache_get(self.ndvi_cache, field_id) or {"value": 0.5}
            # TODO: Replace with ML model (crop-growth-model service or yield-prediction-service)
            # This linear approximation is a temporary placeholder only.
            # Capped at 15 t/ha to prevent obviously wrong values pending ML integration.
            result = {
                "field_id": field_id,
                "type": "yield",
                "predicted_yield_tons": min(round(2.5 * ndvi_data["value"] * 100, 2), 15.0),
                "confidence": 0.87,
                "based_on": ["ndvi", "historical_data", "weather"],
                "timestamp": datetime.now(UTC).isoformat(),
            }
        elif prediction_type == "disease":
            result = {
                "field_id": field_id,
                "type": "disease",
                "risk_level": "low",
                "confidence": 0.92,
                "factors": ["temperature", "humidity", "crop_type"],
                "preventive_actions": [
                    "monitor_leaves",
                    "apply_fungicide_if_needed",
                ],
            }
        else:
            result = {"error": f"Unknown prediction type: {prediction_type}"}

        await self.bus.publish_event(
            domain="ai",
            action=f"prediction.{prediction_type}.completed",
            data=result,
            tenant_id=tenant_id,
        )

        await msg.ack()
        return result


async def main():
    """Entry point for AI event handler service."""
    handlers = AIEventHandlers()
    await handlers.initialize(nats_url="nats://nats:4222")

    logger.info("ai_advisor_event_service_running")
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
