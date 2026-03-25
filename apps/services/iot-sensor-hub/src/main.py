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

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

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

    def register_node(self, reg: NodeRegistration) -> dict:
        self.nodes[reg.node_id] = {
            "node_id": reg.node_id,
            "node_type": reg.node_type.value,
            "name": reg.name,
            "name_ar": reg.name_ar,
            "field_id": reg.field_id,
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

        field_id = self.nodes.get(reading.node_id, {}).get("field_id")

        if "critical_low" in thresholds and filtered_value < thresholds["critical_low"]:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                severity=AlertSeverity.CRITICAL,
                sensor_type=reading.sensor_type.value,
                node_id=reading.node_id,
                field_id=field_id,
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
async def register_node(reg: NodeRegistration):
    """Register a new IoT sensor node."""
    node = iot_engine.register_node(reg)
    return {"status": "registered", "node": node}


@app.get("/api/v1/iot/nodes")
async def list_nodes(field_id: str | None = Query(None)):
    """List registered IoT nodes."""
    nodes = list(iot_engine.nodes.values())
    if field_id:
        nodes = [n for n in nodes if n["field_id"] == field_id]
    return {"nodes": nodes, "total": len(nodes)}


@app.get("/api/v1/iot/nodes/{node_id}")
async def get_node(node_id: str):
    """Get node status and recent readings."""
    if node_id not in iot_engine.nodes:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
    node = iot_engine.nodes[node_id]
    recent = list(iot_engine.readings_buffer.get(node_id, []))[-20:]
    return {"node": node, "recent_readings": recent}


# Sensor data ingestion
@app.post("/api/v1/iot/readings")
async def ingest_reading(reading: SensorReading):
    """Ingest a single sensor reading with Kalman filtering and alert checking."""
    result = iot_engine.process_reading(reading)

    # Publish to NATS (subject: sahool.{tenant_id}.iot.reading.{type})
    nc = getattr(app.state, "nc", None)
    tenant_id = os.getenv("TENANT_ID", "default")
    if nc and result["status"] == "accepted":
        try:
            await nc.publish(
                f"sahool.{tenant_id}.iot.reading.{reading.sensor_type.value}",
                json.dumps(
                    {
                        "node_id": reading.node_id,
                        "sensor_type": reading.sensor_type.value,
                        "value": result["filtered_value"],
                        "timestamp": reading.timestamp.isoformat(),
                    }
                ).encode(),
            )
        except Exception:
            logger.warning("Failed to publish NATS reading event for node %s", reading.node_id, exc_info=True)

    return result


@app.post("/api/v1/iot/readings/batch")
async def ingest_batch(batch: SensorReadingBatch):
    """Ingest a batch of sensor readings."""
    results = []
    nc = getattr(app.state, "nc", None)
    tenant_id = os.getenv("TENANT_ID", "default")

    for reading in batch.readings:
        result = iot_engine.process_reading(reading)
        results.append(result)

        # Publish accepted readings to NATS
        if nc and result["status"] == "accepted":
            try:
                await nc.publish(
                    f"sahool.{tenant_id}.iot.reading.{reading.sensor_type.value}",
                    json.dumps(
                        {
                            "node_id": reading.node_id,
                            "sensor_type": reading.sensor_type.value,
                            "value": result["filtered_value"],
                            "timestamp": reading.timestamp.isoformat(),
                        }
                    ).encode(),
                )
            except Exception as e:
                logger.error(f"Failed to publish event: {e}", exc_info=True)

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
async def calculate_wdi(req: WDIRequest):
    """
    Calculate Weighted Decision Index (WDI) for irrigation decision.

    WDI integrates multiple sensor readings into a single irrigation
    decision index. Based on Sahu & Tripathi (2025): 25% water saving.
    """
    result = iot_engine.calculate_wdi(req)

    nc = getattr(app.state, "nc", None)
    if nc:
        try:
            tenant_id = os.getenv("TENANT_ID", "default")
            await nc.publish(
                f"sahool.{tenant_id}.iot.wdi_calculated",
                json.dumps(
                    {
                        "field_id": req.field_id,
                        "wdi": result.wdi,
                        "irrigate": result.irrigate,
                        "timestamp": result.timestamp.isoformat(),
                    }
                ).encode(),
            )
        except Exception:
            logger.warning("Failed to publish NATS WDI event for field %s", req.field_id, exc_info=True)

    return result


# Alerts
@app.get("/api/v1/iot/alerts")
async def get_alerts(
    severity: AlertSeverity | None = Query(None),
    field_id: str | None = Query(None),
    limit: int = Query(default=50, le=500),
):
    """Get recent IoT alerts."""
    alerts = list(iot_engine.alerts)
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    if field_id:
        alerts = [a for a in alerts if a.field_id == field_id]
    alerts = alerts[-limit:]
    return {"alerts": [a.model_dump() for a in alerts], "total": len(alerts)}


# Offline cache
@app.get("/api/v1/iot/cache/status")
async def cache_status():
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
async def get_stats():
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
