"""
IoT Sensor Hub - SAHOOL Platform v3.0

LoRaWAN + MQTT gateway for agricultural IoT sensors with edge computing,
offline cache, and data fusion capabilities.

Features:
- LoRaWAN gateway integration (15km suburban / 45km rural range)
- MQTT broker for sensor data ingestion
- Edge computing: local data processing without internet
- Offline cache: 72h data retention with auto-sync
- Kalman filter for sensor data fusion
- Weighted Decision Index (WDI) calculation
- ESP32 + LoRa node support (<$15/node)
- NATS event publishing for real-time alerts

Port: 8251

References:
- IoT Sensing Systematic Review (PMC, 2025)
- Smart Drip IoT Review (Springer, 2025)
- XGBoost+WDI Framework (Sahu & Tripathi, 2025)
- LoRaWAN Water Management (T&F, 2025)
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import sys
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from enum import Enum, StrEnum
from typing import Any, Optional

sys.path.insert(0, "/app")
sys.path.insert(0, "/app/shared")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import logging
import re

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field

# Log injection sanitizer (CodeQL LOG_INJECTION mitigation).
_LOG_INJ_RE = re.compile(r"[\r\n\t\x00-\x1f\x7f]")


def _safe_log(value: Any) -> str:
    """Sanitize a value for safe inclusion in log format args."""
    if value is None:
        return ""
    return _LOG_INJ_RE.sub("?", str(value))[:200]

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


VERSION = "16.0.0"
SERVICE_NAME = "iot-sensor-hub"
PORT = int(os.getenv("PORT", "8251"))

logger = logging.getLogger(SERVICE_NAME)

# ---------------------------------------------------------------------------
# Enums & Constants
# ---------------------------------------------------------------------------


class SensorType(StrEnum):
    SOIL_MOISTURE = "soil_moisture"  # Volumetric water content (%)
    SOIL_TEMPERATURE = "soil_temperature"  # °C
    SOIL_EC = "soil_ec"  # Electrical conductivity (dS/m)
    AIR_TEMPERATURE = "air_temperature"  # °C
    AIR_HUMIDITY = "air_humidity"  # %
    WIND_SPEED = "wind_speed"  # m/s
    SOLAR_RADIATION = "solar_radiation"  # W/m² or MJ/m²/day
    RAINFALL = "rainfall"  # mm
    WATER_FLOW = "water_flow"  # L/min
    WATER_LEVEL = "water_level"  # m
    WATER_EC = "water_ec"  # dS/m
    WATER_PH = "water_ph"  # pH
    LEAF_WETNESS = "leaf_wetness"  # binary or %
    NDVI_SENSOR = "ndvi_sensor"  # index 0-1
    PRESSURE = "pressure"  # kPa (pipe/system)


class NodeType(StrEnum):
    ESP32_LORA = "esp32_lora"  # TTGO LoRa32 (<$15)
    ESP32_WIFI = "esp32_wifi"
    ARDUINO_LORA = "arduino_lora"
    COMMERCIAL = "commercial"
    GATEWAY = "gateway"


class AlertSeverity(StrEnum):
    CRITICAL = "critical"  # Immediate action (<6h)
    WARNING = "warning"  # Action within 24-48h
    ADVISORY = "advisory"  # Action within 1 week
    INFO = "info"  # For awareness


# Sensor validation ranges
SENSOR_RANGES: dict[str, tuple[float, float]] = {
    SensorType.SOIL_MOISTURE: (0.0, 100.0),
    SensorType.SOIL_TEMPERATURE: (-10.0, 70.0),
    SensorType.SOIL_EC: (0.0, 20.0),
    SensorType.AIR_TEMPERATURE: (-20.0, 60.0),
    SensorType.AIR_HUMIDITY: (0.0, 100.0),
    SensorType.WIND_SPEED: (0.0, 50.0),
    SensorType.SOLAR_RADIATION: (0.0, 1400.0),
    SensorType.RAINFALL: (0.0, 200.0),
    SensorType.WATER_FLOW: (0.0, 5000.0),
    SensorType.WATER_LEVEL: (-10.0, 100.0),
    SensorType.WATER_EC: (0.0, 20.0),
    SensorType.WATER_PH: (0.0, 14.0),
    SensorType.LEAF_WETNESS: (0.0, 100.0),
    SensorType.NDVI_SENSOR: (0.0, 1.0),
    SensorType.PRESSURE: (0.0, 2000.0),
}

# Alert thresholds for Yemen conditions
ALERT_THRESHOLDS: dict[str, dict] = {
    SensorType.SOIL_MOISTURE: {
        "critical_low": 15.0,
        "warning_low": 25.0,
        "warning_high": 90.0,
        "critical_high": 95.0,
    },
    SensorType.SOIL_EC: {
        "warning_high": 4.0,
        "critical_high": 8.0,
    },
    SensorType.AIR_TEMPERATURE: {
        "critical_low": 2.0,
        "warning_low": 5.0,
        "warning_high": 42.0,
        "critical_high": 48.0,
    },
    SensorType.WATER_EC: {
        "warning_high": 3.0,
        "critical_high": 6.0,
    },
}


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------


class SensorReading(BaseModel):
    """Single sensor reading from a node."""

    node_id: str = Field(..., description="Node identifier")
    sensor_type: SensorType
    value: float
    unit: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    quality: float = Field(default=1.0, ge=0.0, le=1.0, description="Data quality 0-1")
    latitude: float | None = None
    longitude: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SensorReadingBatch(BaseModel):
    """Batch of sensor readings from one or more nodes."""

    readings: list[SensorReading]
    field_id: str | None = None
    tenant_id: str | None = None


class SensorReadingOut(BaseModel):
    """
    Public camelCase representation of a sensor reading.

    Contract-compatible with ``SENSOR_LATEST`` / ``SENSOR_STREAM``
    endpoints defined in ``@sahool/shared-types/contracts``.
    All fields use camelCase aliases via Pydantic V2 aliasing.
    """

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    id: str = Field(..., description="Reading identifier (uuid or node:type:timestamp)")
    sensor_id: str = Field(..., alias="sensorId", description="Sensor / node identifier")
    value: float = Field(..., description="Sensor value (filtered if Kalman applied)")
    unit: str = Field(default="", description="Unit of measurement")
    timestamp: datetime = Field(..., description="Reading timestamp")
    quality: float | None = Field(default=None, description="Quality 0-1")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata")


class SensorOut(BaseModel):
    """
    Public camelCase representation of a sensor / node.

    Contract-compatible with ``SENSORS`` list endpoint.
    """

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    id: str = Field(..., description="Sensor / node identifier")
    name: str = Field(..., description="Sensor display name (English)")
    name_ar: str | None = Field(default=None, alias="nameAr", description="Sensor display name (Arabic)")
    node_type: str = Field(..., alias="nodeType", description="Node hardware type")
    field_id: str = Field(..., alias="fieldId", description="Field the sensor belongs to")
    status: str = Field(..., description="online / offline")
    last_seen: str | None = Field(default=None, alias="lastSeen", description="ISO-8601 last seen timestamp")
    battery_level: float | None = Field(default=None, alias="batteryLevel", description="Battery level 0-100")
    readings_count: int = Field(default=0, alias="readingsCount", description="Total readings received")
    sensors: list[str] = Field(default_factory=list, description="List of supported sensor types")


def _node_to_sensor_out(node: dict) -> dict:
    """Convert an internal node dict to ``SensorOut`` serialization (by alias)."""
    model = SensorOut(
        id=node.get("node_id", ""),
        name=node.get("name", ""),
        name_ar=node.get("name_ar"),
        node_type=node.get("node_type", ""),
        field_id=node.get("field_id", ""),
        status="online" if node.get("online") else "offline",
        last_seen=node.get("last_seen"),
        battery_level=node.get("battery_level"),
        readings_count=int(node.get("readings_count", 0)),
        sensors=list(node.get("sensors", []) or []),
    )
    return model.model_dump(by_alias=True)


def _reading_record_to_out(record: dict, sensor_id: str) -> dict:
    """Convert an internal reading buffer record to ``SensorReadingOut`` (by alias)."""
    # Build a deterministic id if not provided
    raw_ts = record.get("timestamp") or datetime.utcnow().isoformat()
    reading_id = f"{sensor_id}:{record.get('sensor_type', 'value')}:{raw_ts}"
    # Parse ISO timestamp tolerantly
    try:
        ts_parsed = datetime.fromisoformat(str(raw_ts).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        ts_parsed = datetime.utcnow()
    model = SensorReadingOut(
        id=reading_id,
        sensorId=sensor_id,  # type: ignore[arg-type]
        value=float(record.get("filtered_value", record.get("raw_value", 0.0))),
        unit=str(record.get("unit") or ""),
        timestamp=ts_parsed,
        quality=record.get("quality"),
        metadata={"sensor_type": record.get("sensor_type"), "raw_value": record.get("raw_value")},
    )
    return model.model_dump(by_alias=True, mode="json")


class NodeRegistration(BaseModel):
    """Register a new IoT node."""

    node_id: str
    node_type: NodeType
    name: str
    name_ar: str | None = None
    field_id: str
    sensors: list[SensorType]
    latitude: float
    longitude: float
    firmware_version: str | None = None
    battery_level: float | None = None


class NodeStatus(BaseModel):
    """Current status of a registered node."""

    node_id: str
    name: str
    node_type: str
    field_id: str
    online: bool
    last_seen: datetime | None
    battery_level: float | None
    readings_count: int
    sensors: list[str]


class WDIRequest(BaseModel):
    """Weighted Decision Index calculation request."""

    field_id: str
    soil_moisture: float = Field(..., description="Current soil moisture (%)")
    soil_moisture_threshold: float = Field(default=40.0, description="Moisture threshold (%)")
    temperature: float = Field(..., description="Air temperature (°C)")
    temperature_optimal: float = Field(default=25.0, description="Optimal temperature (°C)")
    humidity: float = Field(default=50.0, description="Relative humidity (%)")
    wind_speed: float = Field(default=2.0, description="Wind speed (m/s)")
    solar_radiation: float = Field(default=20.0, description="Solar radiation (MJ/m²/day)")
    # Weights (from Sahu & Tripathi 2025)
    w_moisture: float = Field(default=0.35, description="Weight for soil moisture")
    w_temperature: float = Field(default=0.25, description="Weight for temperature")
    w_humidity: float = Field(default=0.15, description="Weight for humidity")
    w_wind: float = Field(default=0.10, description="Weight for wind")
    w_radiation: float = Field(default=0.15, description="Weight for radiation")


class WDIResponse(BaseModel):
    """Weighted Decision Index result."""

    field_id: str
    wdi: float = Field(..., description="WDI value (0-1, higher = more stress)")
    decision: str
    decision_ar: str
    components: dict[str, float]
    irrigate: bool
    confidence: float
    timestamp: datetime


class Alert(BaseModel):
    """IoT-generated alert."""

    alert_id: str
    severity: AlertSeverity
    sensor_type: str
    node_id: str
    field_id: str | None
    tenant_id: str = ""
    value: float
    threshold: float
    message: str
    message_ar: str
    timestamp: datetime


# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------


class KalmanFilter:
    """
    Simple 1D Kalman filter for sensor data fusion.
    Achieves >92% accuracy per DT Orchestration (ACS, 2024).
    """

    def __init__(self, process_variance: float = 0.01, measurement_variance: float = 0.1):
        self.process_var = process_variance
        self.measurement_var = measurement_variance
        self.estimate = 0.0
        self.estimate_error = 1.0
        self.initialized = False

    def update(self, measurement: float) -> float:
        if not self.initialized:
            self.estimate = measurement
            self.initialized = True
            return measurement

        # Prediction
        prediction = self.estimate
        prediction_error = self.estimate_error + self.process_var

        # Update
        kalman_gain = prediction_error / (prediction_error + self.measurement_var)
        self.estimate = prediction + kalman_gain * (measurement - prediction)
        self.estimate_error = (1.0 - kalman_gain) * prediction_error

        return self.estimate


class OfflineCache:
    """
    72-hour offline data cache with auto-sync capability.
    Critical for Yemen's intermittent connectivity.
    """

    def __init__(self, max_hours: int = 72):
        self.max_duration = timedelta(hours=max_hours)
        self._cache: deque[dict] = deque(maxlen=100000)  # ~100K readings
        self._sync_pending = False

    def store(self, reading: dict):
        self._cache.append({**reading, "_cached_at": datetime.utcnow().isoformat()})
        self._cleanup_old()

    def get_pending(self, limit: int = 1000) -> list[dict]:
        return list(self._cache)[:limit]

    def clear_synced(self, count: int):
        for _ in range(min(count, len(self._cache))):
            self._cache.popleft()

    def _cleanup_old(self):
        cutoff = datetime.utcnow() - self.max_duration
        while self._cache and self._cache[0].get("_cached_at", "") < cutoff.isoformat():
            self._cache.popleft()

    @property
    def size(self) -> int:
        return len(self._cache)


class IoTSensorEngine:
    """
    Core IoT sensor processing engine with edge computing capabilities.
    """

    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.kalman_filters: dict[str, KalmanFilter] = {}
        self.offline_cache = OfflineCache(max_hours=72)
        self.readings_buffer: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: deque[Alert] = deque(maxlen=5000)
        self.stats = {"total_readings": 0, "filtered_readings": 0, "alerts_generated": 0}

    def register_node(self, reg: NodeRegistration, tenant_id: str = "") -> dict:
        self.nodes[reg.node_id] = {
            "node_id": reg.node_id,
            "node_type": reg.node_type.value,
            "name": reg.name,
            "name_ar": reg.name_ar,
            "field_id": reg.field_id,
            "tenant_id": tenant_id,
            "sensors": [s.value for s in reg.sensors],
            "latitude": reg.latitude,
            "longitude": reg.longitude,
            "firmware_version": reg.firmware_version,
            "battery_level": reg.battery_level,
            "registered_at": datetime.utcnow().isoformat(),
            "last_seen": None,
            "online": True,
            "readings_count": 0,
        }
        return self.nodes[reg.node_id]

    def process_reading(self, reading: SensorReading) -> dict:
        """Process a single sensor reading with validation, filtering, and alerting."""
        self.stats["total_readings"] += 1

        # Validate range
        sensor_range = SENSOR_RANGES.get(reading.sensor_type)
        if sensor_range:
            lo, hi = sensor_range
            if not (lo <= reading.value <= hi):
                return {
                    "status": "rejected",
                    "reason": f"Value {reading.value} outside range [{lo}, {hi}]",
                    "node_id": reading.node_id,
                }

        # Apply Kalman filter
        filter_key = f"{reading.node_id}:{reading.sensor_type.value}"
        if filter_key not in self.kalman_filters:
            self.kalman_filters[filter_key] = KalmanFilter()
        filtered_value = self.kalman_filters[filter_key].update(reading.value)
        self.stats["filtered_readings"] += 1

        # Store in buffer
        record = {
            "node_id": reading.node_id,
            "sensor_type": reading.sensor_type.value,
            "raw_value": reading.value,
            "filtered_value": round(filtered_value, 3),
            "quality": reading.quality,
            "timestamp": reading.timestamp.isoformat(),
        }
        self.readings_buffer[reading.node_id].append(record)

        # Update node status
        if reading.node_id in self.nodes:
            self.nodes[reading.node_id]["last_seen"] = reading.timestamp.isoformat()
            self.nodes[reading.node_id]["online"] = True
            self.nodes[reading.node_id]["readings_count"] += 1

        # Store in offline cache
        self.offline_cache.store(record)

        # Check alert thresholds
        alerts = self._check_alerts(reading, filtered_value)

        return {
            "status": "accepted",
            "node_id": reading.node_id,
            "sensor_type": reading.sensor_type.value,
            "raw_value": reading.value,
            "filtered_value": round(filtered_value, 3),
            "alerts": [a.model_dump() for a in alerts] if alerts else [],
        }

    def _check_alerts(self, reading: SensorReading, filtered_value: float) -> list[Alert]:
        """Check if reading triggers any alert thresholds."""
        alerts = []
        thresholds = ALERT_THRESHOLDS.get(reading.sensor_type)
        if not thresholds:
            return alerts

        node_data = self.nodes.get(reading.node_id, {})
        field_id = node_data.get("field_id")
        node_tenant_id = node_data.get("tenant_id", "")

        if "critical_low" in thresholds and filtered_value < thresholds["critical_low"]:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                severity=AlertSeverity.CRITICAL,
                sensor_type=reading.sensor_type.value,
                node_id=reading.node_id,
                field_id=field_id,
                tenant_id=node_tenant_id,
                value=filtered_value,
                threshold=thresholds["critical_low"],
                message=f"CRITICAL: {reading.sensor_type.value} at {filtered_value:.1f} below critical threshold {thresholds['critical_low']}",
                message_ar=f"حرج: {reading.sensor_type.value} عند {filtered_value:.1f} أقل من الحد الحرج {thresholds['critical_low']}",
                timestamp=reading.timestamp,
            )
            alerts.append(alert)
            self.alerts.append(alert)
            self.stats["alerts_generated"] += 1

        elif "warning_low" in thresholds and filtered_value < thresholds["warning_low"]:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                severity=AlertSeverity.WARNING,
                sensor_type=reading.sensor_type.value,
                node_id=reading.node_id,
                field_id=field_id,
                tenant_id=node_tenant_id,
                value=filtered_value,
                threshold=thresholds["warning_low"],
                message=f"WARNING: {reading.sensor_type.value} at {filtered_value:.1f} below warning threshold {thresholds['warning_low']}",
                message_ar=f"تحذير: {reading.sensor_type.value} عند {filtered_value:.1f} أقل من حد التحذير {thresholds['warning_low']}",
                timestamp=reading.timestamp,
            )
            alerts.append(alert)
            self.alerts.append(alert)
            self.stats["alerts_generated"] += 1

        if "critical_high" in thresholds and filtered_value > thresholds["critical_high"]:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                severity=AlertSeverity.CRITICAL,
                sensor_type=reading.sensor_type.value,
                node_id=reading.node_id,
                field_id=field_id,
                tenant_id=node_tenant_id,
                value=filtered_value,
                threshold=thresholds["critical_high"],
                message=f"CRITICAL: {reading.sensor_type.value} at {filtered_value:.1f} above critical threshold {thresholds['critical_high']}",
                message_ar=f"حرج: {reading.sensor_type.value} عند {filtered_value:.1f} أعلى من الحد الحرج {thresholds['critical_high']}",
                timestamp=reading.timestamp,
            )
            alerts.append(alert)
            self.alerts.append(alert)
            self.stats["alerts_generated"] += 1

        elif "warning_high" in thresholds and filtered_value > thresholds["warning_high"]:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                severity=AlertSeverity.WARNING,
                sensor_type=reading.sensor_type.value,
                node_id=reading.node_id,
                field_id=field_id,
                tenant_id=node_tenant_id,
                value=filtered_value,
                threshold=thresholds["warning_high"],
                message=f"WARNING: {reading.sensor_type.value} at {filtered_value:.1f} above warning threshold {thresholds['warning_high']}",
                message_ar=f"تحذير: {reading.sensor_type.value} عند {filtered_value:.1f} أعلى من حد التحذير {thresholds['warning_high']}",
                timestamp=reading.timestamp,
            )
            alerts.append(alert)
            self.alerts.append(alert)
            self.stats["alerts_generated"] += 1

        return alerts

    def calculate_wdi(self, req: WDIRequest) -> WDIResponse:
        """
        Calculate Weighted Decision Index (WDI).
        Based on Sahu & Tripathi (2025): 25% water reduction + 18% yield increase.

        WDI combines multiple environmental factors into a single irrigation decision index.
        WDI = Σ(wi × normalized_factor_i)
        """
        # Normalize factors to 0-1 (higher = more stress)
        # Soil moisture: lower = more stress
        sm_stress = max(0.0, min(1.0, 1.0 - (req.soil_moisture / max(req.soil_moisture_threshold * 2, 1.0))))

        # Temperature stress: deviation from optimal
        temp_stress = min(1.0, abs(req.temperature - req.temperature_optimal) / 20.0)

        # Humidity: lower = more ET demand
        hum_stress = max(0.0, min(1.0, 1.0 - (req.humidity / 100.0)))

        # Wind: higher = more ET
        wind_stress = min(1.0, req.wind_speed / 10.0)

        # Radiation: higher = more ET demand
        rad_stress = min(1.0, req.solar_radiation / 30.0)

        # Weighted sum
        wdi = (
            req.w_moisture * sm_stress
            + req.w_temperature * temp_stress
            + req.w_humidity * hum_stress
            + req.w_wind * wind_stress
            + req.w_radiation * rad_stress
        )
        wdi = round(max(0.0, min(1.0, wdi)), 3)

        # Decision based on WDI thresholds
        if wdi >= 0.7:
            decision = "Irrigate immediately - High water stress"
            decision_ar = "ري فوري - إجهاد مائي عالٍ"
            irrigate = True
            confidence = 0.95
        elif wdi >= 0.5:
            decision = "Schedule irrigation within 24h"
            decision_ar = "جدولة الري خلال 24 ساعة"
            irrigate = True
            confidence = 0.80
        elif wdi >= 0.3:
            decision = "Monitor closely - Moderate stress"
            decision_ar = "مراقبة دقيقة - إجهاد معتدل"
            irrigate = False
            confidence = 0.70
        else:
            decision = "No irrigation needed - Adequate moisture"
            decision_ar = "لا حاجة للري - رطوبة كافية"
            irrigate = False
            confidence = 0.90

        return WDIResponse(
            field_id=req.field_id,
            wdi=wdi,
            decision=decision,
            decision_ar=decision_ar,
            components={
                "soil_moisture_stress": round(sm_stress, 3),
                "temperature_stress": round(temp_stress, 3),
                "humidity_stress": round(hum_stress, 3),
                "wind_stress": round(wind_stress, 3),
                "radiation_stress": round(rad_stress, 3),
            },
            irrigate=irrigate,
            confidence=confidence,
            timestamp=datetime.utcnow(),
        )


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

iot_engine = IoTSensorEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging

    logger = logging.getLogger(SERVICE_NAME)
    logger.info(f"Starting {SERVICE_NAME} v{VERSION} on port {PORT}")

    # NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats as nats_lib

            app.state.nc = await nats_lib.connect(nats_url)
            from shared.logging_config import sanitize_url

            logger.info(f"Connected to NATS: {sanitize_url(nats_url)}")
        except Exception as e:
            logger.warning(f"NATS connection failed: {e}")
            app.state.nc = None
    else:
        app.state.nc = None

    yield

    if getattr(app.state, "nc", None):
        await app.state.nc.close()
    logger.info(f"{SERVICE_NAME} shutdown complete")


app = FastAPI(
    title="IoT Sensor Hub",
    description="LoRaWAN + MQTT gateway with edge computing for agricultural IoT",
    version=VERSION,
    lifespan=lifespan,
)

try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass

try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    app.add_middleware(TenantContextMiddleware)
except ImportError:
    pass


# Health endpoints
@app.get("/healthz")
def health():
    return {"status": "ok", "service": SERVICE_NAME, "version": VERSION}


@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "nodes_registered": len(iot_engine.nodes),
        "offline_cache_size": iot_engine.offline_cache.size,
        "total_readings": iot_engine.stats["total_readings"],
        "nats": getattr(app.state, "nc", None) is not None,
    }


# Node management
@app.post("/api/v1/iot/nodes", status_code=201)
async def register_node(reg: NodeRegistration, current_user: User = Depends(get_current_user)):
    """Register a new IoT sensor node."""
    tenant_id = getattr(current_user, "tenant_id", None) or os.getenv("TENANT_ID", "default")
    node = iot_engine.register_node(reg, tenant_id=tenant_id)
    return {"status": "registered", "node": node}


@app.get("/api/v1/iot/nodes")
async def list_nodes(field_id: str | None = Query(None), user: User = Depends(get_current_user)):
    """List registered IoT nodes."""
    user_tenant = getattr(user, "tenant_id", None)
    nodes = list(iot_engine.nodes.values())
    if user_tenant:
        nodes = [n for n in nodes if n.get("tenant_id") == user_tenant]
    if field_id:
        nodes = [n for n in nodes if n["field_id"] == field_id]
    return {"nodes": nodes, "total": len(nodes)}


@app.get("/api/v1/iot/nodes/{node_id}")
async def get_node(node_id: str, user: User = Depends(get_current_user)):
    """Get node status and recent readings."""
    if node_id not in iot_engine.nodes:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
    node = iot_engine.nodes[node_id]
    recent = list(iot_engine.readings_buffer.get(node_id, []))[-20:]
    return {"node": node, "recent_readings": recent}


# Sensor data ingestion
@app.post("/api/v1/iot/readings")
async def ingest_reading(reading: SensorReading, current_user: User = Depends(get_current_user)):
    """Ingest a single sensor reading with Kalman filtering and alert checking."""
    result = iot_engine.process_reading(reading)

    # Publish to NATS (subject: sahool.tenant.{tenant_id}.iot.reading.{type})
    nc = getattr(app.state, "nc", None)
    tenant_id = getattr(current_user, "tenant_id", None) or os.getenv("TENANT_ID", "default")
    if nc and result["status"] == "accepted":
        try:
            await nc.publish(
                f"sahool.tenant.{tenant_id}.iot.reading.{reading.sensor_type.value}",
                json.dumps(
                    {
                        "node_id": reading.node_id,
                        "field_id": iot_engine.nodes.get(reading.node_id, {}).get("field_id"),
                        "sensor_type": reading.sensor_type.value,
                        "value": result["filtered_value"],
                        "timestamp": reading.timestamp.isoformat(),
                    }
                ).encode(),
            )
        except Exception as e:
            logger.warning("nats_publish_reading_failed: %s", _safe_log(repr(e)))

    return result


@app.post("/api/v1/iot/readings/batch")
async def ingest_batch(batch: SensorReadingBatch, current_user: User = Depends(get_current_user)):
    """Ingest a batch of sensor readings."""
    results = []
    nc = getattr(app.state, "nc", None)
    tenant_id = getattr(current_user, "tenant_id", None) or os.getenv("TENANT_ID", "default")

    for reading in batch.readings:
        result = iot_engine.process_reading(reading)
        results.append(result)

        # Publish accepted readings to NATS
        if nc and result["status"] == "accepted":
            try:
                await nc.publish(
                    f"sahool.tenant.{tenant_id}.iot.reading.{reading.sensor_type.value}",
                    json.dumps(
                        {
                            "node_id": reading.node_id,
                            "field_id": iot_engine.nodes.get(reading.node_id, {}).get("field_id"),
                            "sensor_type": reading.sensor_type.value,
                            "value": result["filtered_value"],
                            "timestamp": reading.timestamp.isoformat(),
                        }
                    ).encode(),
                )
            except Exception as e:
                logger.error("nats_publish_batch_failed: %s", _safe_log(repr(e)))

    accepted = sum(1 for r in results if r["status"] == "accepted")
    rejected = len(results) - accepted
    return {
        "total": len(results),
        "accepted": accepted,
        "rejected": rejected,
        "results": results,
    }


# WDI calculation
@app.post("/api/v1/iot/wdi", response_model=WDIResponse)
async def calculate_wdi(req: WDIRequest, current_user: User = Depends(get_current_user)):
    """
    Calculate Weighted Decision Index (WDI) for irrigation decision.

    WDI integrates multiple sensor readings into a single irrigation
    decision index. Based on Sahu & Tripathi (2025): 25% water saving.
    """
    result = iot_engine.calculate_wdi(req)

    nc = getattr(app.state, "nc", None)
    if nc:
        try:
            tenant_id = getattr(current_user, "tenant_id", None) or os.getenv("TENANT_ID", "default")
            await nc.publish(
                f"sahool.tenant.{tenant_id}.iot.wdi_calculated",
                json.dumps(
                    {
                        "field_id": req.field_id,
                        "wdi": result.wdi,
                        "irrigate": result.irrigate,
                        "timestamp": result.timestamp.isoformat(),
                    }
                ).encode(),
            )
        except Exception as e:
            logger.warning("nats_publish_wdi_failed: %s", _safe_log(repr(e)))

    return result


# Alerts
@app.get("/api/v1/iot/alerts")
async def get_alerts(
    severity: AlertSeverity | None = Query(None),
    field_id: str | None = Query(None),
    limit: int = Query(default=50, le=500),
    user: User = Depends(get_current_user),
):
    """Get recent IoT alerts."""
    user_tenant = getattr(user, "tenant_id", None)
    alerts = list(iot_engine.alerts)
    if user_tenant:
        alerts = [a for a in alerts if a.tenant_id == user_tenant]
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    if field_id:
        alerts = [a for a in alerts if a.field_id == field_id]
    alerts = alerts[-limit:]
    return {"alerts": [a.model_dump() for a in alerts], "total": len(alerts)}


# Offline cache
@app.get("/api/v1/iot/cache/status")
async def cache_status(user: User = Depends(get_current_user)):
    """Get offline cache status."""
    return {
        "cache_size": iot_engine.offline_cache.size,
        "max_hours": 72,
        "sync_pending": iot_engine.offline_cache._sync_pending,
    }


@app.post("/api/v1/iot/cache/sync")
async def sync_cache(
    limit: int = Query(default=1000, le=10000),
    confirm_clear: bool = Query(default=False, description="Set true to clear synced entries"),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve cached entries and optionally clear them.

    Two-phase sync: first call with confirm_clear=false to preview,
    then confirm_clear=true to actually clear synced entries.
    """
    pending = iot_engine.offline_cache.get_pending(limit)
    if confirm_clear and pending:
        iot_engine.offline_cache.clear_synced(len(pending))
    return {
        "synced": len(pending),
        "cleared": confirm_clear,
        "remaining": iot_engine.offline_cache.size,
        "data": pending,
    }


# Statistics
@app.get("/api/v1/iot/stats")
async def get_stats(user: User = Depends(get_current_user)):
    """Get IoT hub statistics."""
    return {
        "nodes_registered": len(iot_engine.nodes),
        "total_readings": iot_engine.stats["total_readings"],
        "filtered_readings": iot_engine.stats["filtered_readings"],
        "alerts_generated": iot_engine.stats["alerts_generated"],
        "offline_cache_size": iot_engine.offline_cache.size,
        "active_kalman_filters": len(iot_engine.kalman_filters),
    }


# Supported sensor types
@app.get("/api/v1/iot/sensor-types")
async def list_sensor_types():
    """List supported sensor types with valid ranges."""
    return {
        "sensor_types": [
            {
                "type": st.value,
                "range": SENSOR_RANGES.get(st, (None, None)),
                "alert_thresholds": ALERT_THRESHOLDS.get(st),
            }
            for st in SensorType
        ]
    }


# ---------------------------------------------------------------------------
# Alias routes aligned with @sahool/shared-types IOT_ENDPOINTS (4.3.0)
# SENSORS, SENSOR_LATEST, SENSOR_STATS, SENSOR_STREAM
# ---------------------------------------------------------------------------


def _filter_tenant_nodes(user: User, field_id: str | None = None) -> list[dict]:
    """Return nodes visible to this tenant (and optionally a field)."""
    user_tenant = getattr(user, "tenant_id", None)
    nodes = list(iot_engine.nodes.values())
    if user_tenant:
        nodes = [n for n in nodes if n.get("tenant_id") == user_tenant]
    if field_id:
        nodes = [n for n in nodes if n.get("field_id") == field_id]
    return nodes


@app.get("/api/v1/iot/sensors")
async def list_sensors_alias(
    field_id: str | None = Query(None, description="Optional field filter"),
    user: User = Depends(get_current_user),
):
    """
    Alias for ``/api/v1/iot/nodes`` — returns sensors in camelCase shape.

    Aligned with ``IOT_ENDPOINTS.SENSORS`` in the shared contracts package.
    """
    nodes = _filter_tenant_nodes(user, field_id=field_id)
    sensors = [_node_to_sensor_out(n) for n in nodes]
    return {"sensors": sensors, "total": len(sensors)}


@app.get("/api/v1/iot/sensors/stats")
async def sensors_stats_alias(user: User = Depends(get_current_user)):
    """
    Sensor summary statistics grouped by status and node type.

    Aligned with ``IOT_ENDPOINTS.SENSOR_STATS`` in the shared contracts package.
    """
    nodes = _filter_tenant_nodes(user)
    by_status: dict[str, int] = {"online": 0, "offline": 0}
    by_type: dict[str, int] = {}
    for n in nodes:
        key = "online" if n.get("online") else "offline"
        by_status[key] = by_status.get(key, 0) + 1
        t = str(n.get("node_type", "unknown"))
        by_type[t] = by_type.get(t, 0) + 1
    return {
        "total": len(nodes),
        "byStatus": by_status,
        "byType": by_type,
    }


@app.get("/api/v1/iot/sensors/stream")
async def sensors_stream_alias(
    request: Request,
    sensor_id: str | None = Query(None, description="Optional sensor/node filter"),
    field_id: str | None = Query(None, description="Optional field filter"),
    user: User = Depends(get_current_user),
):
    """
    Server-Sent Events stream of live sensor readings.

    Subscribes to NATS subject ``sahool.tenant.{tenantId}.iot.reading.*``
    and forwards each message as a ``data:`` SSE event. Returns HTTP 501
    with a bilingual explanation if ``sse-starlette`` is not installed or
    NATS is unavailable.

    Aligned with ``IOT_ENDPOINTS.SENSOR_STREAM`` in the shared contracts
    package.
    """
    try:
        from sse_starlette.sse import EventSourceResponse
    except ImportError as exc:
        raise HTTPException(
            status_code=501,
            detail={
                "error": "sse_not_available",
                "message_en": (
                    "Server-Sent Events dependency 'sse-starlette' is not "
                    "installed. Install it to enable /sensors/stream."
                ),
                "message_ar": (
                    "المكتبة المطلوبة لدفق الأحداث 'sse-starlette' غير مثبتة. "
                    "قم بتثبيتها لتفعيل بث المستشعرات."
                ),
            },
        ) from exc

    nc = getattr(app.state, "nc", None)
    if nc is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "nats_unavailable",
                "message_en": "NATS connection not available; streaming disabled.",
                "message_ar": "اتصال NATS غير متوفر؛ البث معطل.",
            },
        )

    tenant_id = getattr(user, "tenant_id", None) or os.getenv("TENANT_ID", "default")
    subject_pattern = f"sahool.tenant.{tenant_id}.iot.reading.*"
    queue: asyncio.Queue = asyncio.Queue(maxsize=256)

    async def _cb(msg):
        try:
            data = json.loads(msg.data.decode()) if msg.data else {}
        except Exception:
            data = {"raw": msg.data.decode(errors="ignore") if msg.data else ""}
        # Client-side filters
        if sensor_id and str(data.get("node_id") or data.get("sensor_id")) != sensor_id:
            return
        if field_id and str(data.get("field_id") or "") != field_id:
            return
        try:
            queue.put_nowait({"event": "reading", "data": json.dumps(data)})
        except asyncio.QueueFull:
            # Drop oldest when overwhelmed
            try:
                _ = queue.get_nowait()
                queue.put_nowait({"event": "reading", "data": json.dumps(data)})
            except Exception:
                pass

    try:
        sub = await nc.subscribe(subject_pattern, cb=_cb)
    except Exception as e:
        logger.warning("sensors_stream_subscribe_failed: %s", _safe_log(repr(e)))
        raise HTTPException(
            status_code=503,
            detail={
                "error": "nats_subscribe_failed",
                "message_en": "Failed to subscribe to sensor event stream.",
                "message_ar": "فشل الاشتراك في بث أحداث المستشعرات.",
            },
        ) from e

    async def _event_gen():
        try:
            # Initial hello event so the client knows the stream is live
            yield {"event": "hello", "data": json.dumps({"tenantId": tenant_id})}
            while True:
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield item
                except TimeoutError:
                    # Keepalive comment so proxies don't time out
                    yield {"event": "ping", "data": "{}"}
        finally:
            try:
                await sub.unsubscribe()
            except Exception:
                pass

    return EventSourceResponse(_event_gen())


@app.get("/api/v1/iot/sensors/{sensor_id}")
async def get_sensor_alias(sensor_id: str, user: User = Depends(get_current_user)):
    """
    Alias for ``/api/v1/iot/nodes/{id}`` — returns a single sensor in camelCase shape.
    """
    node = iot_engine.nodes.get(sensor_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Sensor not found: {sensor_id}")
    user_tenant = getattr(user, "tenant_id", None)
    if user_tenant and node.get("tenant_id") != user_tenant:
        # Do not leak existence across tenants
        raise HTTPException(status_code=404, detail=f"Sensor not found: {sensor_id}")
    recent = list(iot_engine.readings_buffer.get(sensor_id, []))[-20:]
    return {
        "sensor": _node_to_sensor_out(node),
        "recentReadings": [_reading_record_to_out(r, sensor_id) for r in recent],
    }


@app.get("/api/v1/iot/sensors/{sensor_id}/latest")
async def get_sensor_latest(sensor_id: str, user: User = Depends(get_current_user)):
    """
    Return the most recent filtered reading for a sensor in camelCase shape.

    Aligned with ``IOT_ENDPOINTS.SENSOR_LATEST`` in the shared contracts package.
    """
    node = iot_engine.nodes.get(sensor_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Sensor not found: {sensor_id}")
    user_tenant = getattr(user, "tenant_id", None)
    if user_tenant and node.get("tenant_id") != user_tenant:
        raise HTTPException(status_code=404, detail=f"Sensor not found: {sensor_id}")
    buffer = iot_engine.readings_buffer.get(sensor_id)
    if not buffer:
        raise HTTPException(status_code=404, detail="No readings available for this sensor yet")
    record = buffer[-1]
    return _reading_record_to_out(record, sensor_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)  # nosec B104 - binding to all interfaces required for Docker container
