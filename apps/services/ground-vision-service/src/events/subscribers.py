"""
NATS Event Subscribers - مستقبلو أحداث NATS
Based on: SAHOOL 4-Layer Event Architecture

This module subscribes to events from other services to correlate
ground vision data with satellite imagery, weather, and field updates.
"""

import json
import logging
from datetime import datetime, timezone, UTC
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class GroundVisionSubscriber:
    """
    Subscribe to relevant events from other SAHOOL services.

    Subscribed events:
    - sahool.*.satellite.ndvi_computed - Correlate with satellite NDVI
    - sahool.*.weather.forecast_updated - Adjust detection thresholds
    - sahool.*.fields.boundary_updated - Update camera-field mapping
    """

    # Subscription subjects
    SUBJECT_NDVI_COMPUTED = "sahool.*.satellite.ndvi_computed"
    SUBJECT_WEATHER_UPDATED = "sahool.*.weather.forecast_updated"
    SUBJECT_FIELD_BOUNDARY = "sahool.*.fields.boundary_updated"
    SUBJECT_FIELD_CREATED = "sahool.*.fields.created"
    SUBJECT_IOT_READING = "sahool.*.iot.sensor_reading"

    def __init__(self, nc=None):
        """
        Initialize subscriber.

        Args:
            nc: NATS connection (async)
        """
        self.nc = nc
        self.subscriptions = []

        # Callback handlers
        self._ndvi_handlers: list[Callable] = []
        self._weather_handlers: list[Callable] = []
        self._field_handlers: list[Callable] = []
        self._iot_handlers: list[Callable] = []

    def set_connection(self, nc):
        """Set NATS connection after initialization."""
        self.nc = nc

    def on_ndvi_computed(self, handler: Callable):
        """Register handler for NDVI computed events."""
        self._ndvi_handlers.append(handler)

    def on_weather_updated(self, handler: Callable):
        """Register handler for weather forecast events."""
        self._weather_handlers.append(handler)

    def on_field_updated(self, handler: Callable):
        """Register handler for field boundary events."""
        self._field_handlers.append(handler)

    def on_iot_reading(self, handler: Callable):
        """Register handler for IoT sensor readings."""
        self._iot_handlers.append(handler)

    async def start(self):
        """Start all subscriptions."""
        if self.nc is None:
            logger.warning("NATS not connected, skipping subscriptions")
            return

        try:
            # Subscribe to NDVI events
            sub = await self.nc.subscribe(
                self.SUBJECT_NDVI_COMPUTED,
                cb=self._handle_ndvi_event,
            )
            self.subscriptions.append(sub)
            logger.info(f"Subscribed to {self.SUBJECT_NDVI_COMPUTED}")

            # Subscribe to weather events
            sub = await self.nc.subscribe(
                self.SUBJECT_WEATHER_UPDATED,
                cb=self._handle_weather_event,
            )
            self.subscriptions.append(sub)
            logger.info(f"Subscribed to {self.SUBJECT_WEATHER_UPDATED}")

            # Subscribe to field boundary events
            sub = await self.nc.subscribe(
                self.SUBJECT_FIELD_BOUNDARY,
                cb=self._handle_field_event,
            )
            self.subscriptions.append(sub)

            sub = await self.nc.subscribe(
                self.SUBJECT_FIELD_CREATED,
                cb=self._handle_field_event,
            )
            self.subscriptions.append(sub)
            logger.info("Subscribed to field events")

            # Subscribe to IoT events (for sensor correlation)
            sub = await self.nc.subscribe(
                self.SUBJECT_IOT_READING,
                cb=self._handle_iot_event,
            )
            self.subscriptions.append(sub)
            logger.info(f"Subscribed to {self.SUBJECT_IOT_READING}")

        except Exception as e:
            logger.error(f"Failed to start subscriptions: {e}")
            raise

    async def stop(self):
        """Stop all subscriptions."""
        for sub in self.subscriptions:
            try:
                await sub.unsubscribe()
            except Exception as e:
                logger.warning(f"Error unsubscribing: {e}")

        self.subscriptions.clear()
        logger.info("All subscriptions stopped")

    async def _handle_ndvi_event(self, msg):
        """
        Handle NDVI computed event.

        Uses satellite NDVI to validate ground vision observations.
        """
        try:
            data = json.loads(msg.data.decode())
            logger.debug(f"Received NDVI event: {data.get('event_id', 'unknown')}")

            for handler in self._ndvi_handlers:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"NDVI handler error: {e}")

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid NDVI event JSON: {e}")

    async def _handle_weather_event(self, msg):
        """
        Handle weather forecast updated event.

        Adjusts detection thresholds based on expected conditions:
        - Rain -> Lower change detection sensitivity
        - High wind -> Expect more motion
        - Cloud cover -> Adjust lighting expectations
        """
        try:
            data = json.loads(msg.data.decode())
            logger.debug(f"Received weather event: {data.get('event_id', 'unknown')}")

            for handler in self._weather_handlers:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Weather handler error: {e}")

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid weather event JSON: {e}")

    async def _handle_field_event(self, msg):
        """
        Handle field boundary updated event.

        Updates camera-field mapping when field boundaries change.
        """
        try:
            data = json.loads(msg.data.decode())
            logger.debug(f"Received field event: {data.get('event_id', 'unknown')}")

            for handler in self._field_handlers:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Field handler error: {e}")

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid field event JSON: {e}")

    async def _handle_iot_event(self, msg):
        """
        Handle IoT sensor reading event.

        Correlates ground vision with IoT sensor data:
        - Soil moisture sensors -> Validate water stress detection
        - Weather stations -> Adjust for local conditions
        - Temperature sensors -> Correlate with stress detection
        """
        try:
            data = json.loads(msg.data.decode())
            logger.debug(f"Received IoT event: {data.get('sensor_id', 'unknown')}")

            for handler in self._iot_handlers:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"IoT handler error: {e}")

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid IoT event JSON: {e}")


class EventCorrelator:
    """
    Correlate events from multiple sources for enhanced detection.
    """

    def __init__(self):
        """Initialize correlator."""
        # Cache of recent events for correlation
        self._ndvi_cache: dict[str, dict] = {}
        self._weather_cache: dict[str, dict] = {}
        self._iot_cache: dict[str, dict] = {}

        # Cache TTL in seconds
        self._cache_ttl = 3600  # 1 hour

    async def store_ndvi(self, field_id: str, ndvi_data: dict):
        """Store NDVI data for correlation."""
        self._ndvi_cache[field_id] = {
            "data": ndvi_data,
            "timestamp": datetime.now(UTC),
        }

    async def store_weather(self, location_key: str, weather_data: dict):
        """Store weather data for correlation."""
        self._weather_cache[location_key] = {
            "data": weather_data,
            "timestamp": datetime.now(UTC),
        }

    async def store_iot(self, sensor_id: str, reading: dict):
        """Store IoT reading for correlation."""
        self._iot_cache[sensor_id] = {
            "data": reading,
            "timestamp": datetime.now(UTC),
        }

    def get_field_context(self, field_id: str) -> dict:
        """
        Get correlated context for a field.

        Returns combined data from NDVI, weather, and IoT sources.
        """
        context = {
            "ndvi": None,
            "weather": None,
            "iot_readings": [],
        }

        # Get NDVI if available
        if field_id in self._ndvi_cache:
            entry = self._ndvi_cache[field_id]
            age = (datetime.now(UTC) - entry["timestamp"]).total_seconds()
            if age < self._cache_ttl:
                context["ndvi"] = entry["data"]

        # Get weather (using field_id as location key for simplicity)
        if field_id in self._weather_cache:
            entry = self._weather_cache[field_id]
            age = (datetime.now(UTC) - entry["timestamp"]).total_seconds()
            if age < self._cache_ttl:
                context["weather"] = entry["data"]

        # Get IoT readings for this field
        for sensor_id, entry in self._iot_cache.items():
            if field_id in sensor_id:  # Simple matching
                age = (datetime.now(UTC) - entry["timestamp"]).total_seconds()
                if age < self._cache_ttl:
                    context["iot_readings"].append(entry["data"])

        return context

    def validate_detection(
        self,
        detection_type: str,
        detection_confidence: float,
        field_context: dict,
    ) -> dict:
        """
        Validate detection against correlated data.

        Returns adjusted confidence and supporting evidence.
        """
        validation = {
            "original_confidence": detection_confidence,
            "adjusted_confidence": detection_confidence,
            "supporting_evidence": [],
            "conflicting_evidence": [],
        }

        # Validate water stress detection against IoT
        if detection_type == "water_stress":
            for reading in field_context.get("iot_readings", []):
                if reading.get("sensor_type") == "soil_moisture":
                    moisture = reading.get("value", 50)
                    if moisture < 30:  # Low moisture confirms stress
                        validation["adjusted_confidence"] = min(
                            0.95,
                            detection_confidence + 0.1
                        )
                        validation["supporting_evidence"].append({
                            "source": "iot_soil_moisture",
                            "value": moisture,
                            "note": "Low soil moisture confirms water stress",
                        })
                    elif moisture > 60:  # High moisture conflicts
                        validation["adjusted_confidence"] = max(
                            0.3,
                            detection_confidence - 0.2
                        )
                        validation["conflicting_evidence"].append({
                            "source": "iot_soil_moisture",
                            "value": moisture,
                            "note": "Adequate soil moisture conflicts with stress detection",
                        })

        # Validate crop health against NDVI
        if detection_type in ["nutrient_deficiency", "disease_outbreak"]:
            ndvi = field_context.get("ndvi")
            if ndvi and "value" in ndvi:
                ndvi_value = ndvi["value"]
                if ndvi_value < 0.4:  # Low NDVI confirms issues
                    validation["adjusted_confidence"] = min(
                        0.95,
                        detection_confidence + 0.1
                    )
                    validation["supporting_evidence"].append({
                        "source": "satellite_ndvi",
                        "value": ndvi_value,
                        "note": "Low NDVI supports health issue detection",
                    })

        return validation

    def cleanup_expired(self):
        """Remove expired cache entries."""
        now = datetime.now(UTC)

        for cache in [self._ndvi_cache, self._weather_cache, self._iot_cache]:
            expired_keys = [
                k for k, v in cache.items()
                if (now - v["timestamp"]).total_seconds() > self._cache_ttl
            ]
            for k in expired_keys:
                del cache[k]
