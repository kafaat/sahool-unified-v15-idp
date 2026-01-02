"""
SAHOOL IoT Gateway - Main API Service
MQTT → NATS bridge for sensor data ingestion
Port: 8106
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field, validator

from .events import IoTPublisher, get_publisher
from .mqtt_client import MqttClient, MqttMessage
from .normalizer import normalize
from .registry import DeviceRegistry, DeviceStatus, get_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("iot-gateway")

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sahool/sensors/#")
# Support both MQTT_USER (docker-compose) and MQTT_USERNAME (legacy) env vars
MQTT_USER = os.getenv("MQTT_USER", os.getenv("MQTT_USERNAME", ""))
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
DEFAULT_TENANT = os.getenv("DEFAULT_TENANT", "default")


# Global state
mqtt_client: Optional[MqttClient] = None
publisher: Optional[IoTPublisher] = None
registry: Optional[DeviceRegistry] = None
mqtt_task: Optional[asyncio.Task] = None


async def handle_mqtt_message(msg: MqttMessage):
    """
    Process incoming MQTT message

    Security features:
    - Validates device is registered before accepting data
    - Validates sensor value ranges
    - Auto-registers only if explicitly allowed (for backward compatibility)
    - Logs all operations for audit trail
    """
    global publisher, registry

    try:
        # Normalize the reading
        reading = normalize(msg.payload, msg.topic)

        # Check if device is registered
        device = registry.get(reading.device_id)

        if not device:
            # Auto-register device if enabled (for backward compatibility)
            # In production, devices should be pre-registered
            auto_register_enabled = (
                os.getenv("IOT_AUTO_REGISTER", "false").lower() == "true"
            )

            if auto_register_enabled:
                logger.warning(
                    f"Auto-registering device {reading.device_id} from MQTT. "
                    f"This should be disabled in production."
                )
                registry.auto_register(
                    device_id=reading.device_id,
                    tenant_id=DEFAULT_TENANT,
                    field_id=reading.field_id,
                    sensor_type=reading.sensor_type,
                )
            else:
                logger.error(
                    f"MQTT message rejected: Device {reading.device_id} not registered. "
                    f"Topic: {msg.topic}"
                )
                return

        # Validate sensor value range
        sensor_type_lower = reading.sensor_type.lower()
        if sensor_type_lower in SENSOR_RANGES:
            range_config = SENSOR_RANGES[sensor_type_lower]
            if (
                reading.value < range_config["min"]
                or reading.value > range_config["max"]
            ):
                logger.error(
                    f"MQTT message rejected: Value {reading.value} out of range "
                    f"for {reading.sensor_type}. Device: {reading.device_id}, "
                    f"Expected {range_config['min']} to {range_config['max']}"
                )
                return

        # Update device status
        registry.update_status(
            device_id=reading.device_id,
            last_reading=reading.to_dict(),
            battery_level=reading.metadata.get("battery") if reading.metadata else None,
            signal_strength=reading.metadata.get("rssi") if reading.metadata else None,
        )

        # Publish to NATS
        await publisher.publish_sensor_reading(
            tenant_id=DEFAULT_TENANT,
            field_id=reading.field_id,
            device_id=reading.device_id,
            sensor_type=reading.sensor_type,
            value=reading.value,
            unit=reading.unit,
            timestamp=reading.timestamp,
            metadata=reading.metadata,
        )

        logger.debug(
            f"MQTT message processed. Device: {reading.device_id}, "
            f"Type: {reading.sensor_type}, Value: {reading.value}"
        )

    except Exception as e:
        logger.error(
            f"Error processing MQTT message: {e}. "
            f"Topic: {msg.topic}, Payload: {msg.payload[:200]}..."
        )


async def check_offline_devices():
    """Periodic task to check for offline devices"""
    global registry, publisher

    while True:
        await asyncio.sleep(60)  # Check every minute

        try:
            offline = registry.check_offline_devices()
            for device in offline:
                await publisher.publish_device_status(
                    tenant_id=DEFAULT_TENANT,
                    device_id=device.device_id,
                    field_id=device.field_id,
                    status=DeviceStatus.OFFLINE.value,
                    last_seen=device.last_seen
                    or datetime.now(timezone.utc).isoformat(),
                )

                # Also publish alert
                await publisher.publish_device_alert(
                    tenant_id=DEFAULT_TENANT,
                    device_id=device.device_id,
                    field_id=device.field_id,
                    alert_type="device_offline",
                    message_ar=f"الجهاز {device.device_id} غير متصل",
                    message_en=f"Device {device.device_id} is offline",
                    severity="warning",
                )
        except Exception as e:
            print(f"❌ Error checking offline devices: {e}")


async def start_mqtt_listener():
    """Start MQTT subscription"""
    global mqtt_client

    mqtt_client = MqttClient(
        broker=MQTT_BROKER,
        port=MQTT_PORT,
        username=MQTT_USER if MQTT_USER else None,
        password=MQTT_PASSWORD if MQTT_PASSWORD else None,
    )

    print(f"🔌 Starting MQTT listener on {MQTT_BROKER}:{MQTT_PORT}")
    if MQTT_USER:
        print(f"🔐 MQTT authentication enabled for user: {MQTT_USER}")
    print(f"📥 Subscribing to: {MQTT_TOPIC}")

    await mqtt_client.subscribe(MQTT_TOPIC, handle_mqtt_message)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    global publisher, registry, mqtt_task

    # Startup
    print("🌐 Starting IoT Gateway Service...")

    # Initialize registry
    registry = get_registry()

    # Initialize publisher
    try:
        publisher = await get_publisher()
        print("✅ Connected to NATS")
    except Exception as e:
        print(f"⚠️ NATS connection failed: {e}")
        publisher = None

    # Start MQTT listener in background
    mqtt_task = asyncio.create_task(start_mqtt_listener())

    # Start offline device checker
    asyncio.create_task(check_offline_devices())

    print("✅ IoT Gateway ready on port 8106")

    yield

    # Shutdown
    if mqtt_client:
        mqtt_client.stop()
    if mqtt_task:
        mqtt_task.cancel()
    if publisher:
        await publisher.close()

    print("👋 IoT Gateway shutting down")


app = FastAPI(
    title="SAHOOL IoT Gateway",
    description="MQTT to NATS bridge for sensor data ingestion",
    version="15.3.3",
    lifespan=lifespan,
)


# ============== Health Check ==============


@app.get("/healthz")
def health():
    stats = publisher.get_stats() if publisher else {}
    registry_stats = registry.get_stats() if registry else {}

    return {
        "status": "healthy",
        "service": "iot-gateway",
        "version": "15.3.3",
        "mqtt": {
            "broker": MQTT_BROKER,
            "topic": MQTT_TOPIC,
            "connected": mqtt_client._running if mqtt_client else False,
        },
        "nats": stats,
        "devices": registry_stats,
    }


# ============== Request/Response Models ==============

# Sensor value ranges for validation
SENSOR_RANGES = {
    "temperature": {"min": -50.0, "max": 80.0},  # °C
    "humidity": {"min": 0.0, "max": 100.0},  # %
    "soil_moisture": {"min": 0.0, "max": 100.0},  # %
    "soil_temperature": {"min": -20.0, "max": 60.0},  # °C
    "ph": {"min": 0.0, "max": 14.0},  # pH scale
    "ec": {"min": 0.0, "max": 10.0},  # dS/m
    "nitrogen": {"min": 0.0, "max": 1000.0},  # ppm
    "phosphorus": {"min": 0.0, "max": 1000.0},  # ppm
    "potassium": {"min": 0.0, "max": 1000.0},  # ppm
    "light": {"min": 0.0, "max": 200000.0},  # lux
    "rainfall": {"min": 0.0, "max": 500.0},  # mm
    "wind_speed": {"min": 0.0, "max": 150.0},  # km/h
    "pressure": {"min": 800.0, "max": 1200.0},  # hPa
    "battery": {"min": 0.0, "max": 100.0},  # %
}


class SensorReadingRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=100)
    tenant_id: str = Field(..., min_length=1, max_length=100)
    field_id: str = Field(..., min_length=1, max_length=100)
    sensor_type: str = Field(..., min_length=1, max_length=50)
    value: float
    unit: str = Field("", max_length=20)
    timestamp: Optional[str] = None
    metadata: Optional[dict] = None

    @validator("sensor_type")
    def validate_sensor_type(cls, v):
        """Validate sensor type is known"""
        v = v.lower()
        if v not in SENSOR_RANGES and not v.startswith("custom_"):
            logger.warning(f"Unknown sensor type: {v}")
        return v

    @validator("value")
    def validate_value_range(cls, v, values):
        """Validate sensor value is within expected range"""
        if "sensor_type" in values:
            sensor_type = values["sensor_type"].lower()
            if sensor_type in SENSOR_RANGES:
                range_config = SENSOR_RANGES[sensor_type]
                if v < range_config["min"] or v > range_config["max"]:
                    raise ValueError(
                        f"Value {v} out of range for {sensor_type}. "
                        f"Expected {range_config['min']} to {range_config['max']}"
                    )
        return v


class BatchReadingRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=100)
    tenant_id: str = Field(..., min_length=1, max_length=100)
    field_id: str = Field(..., min_length=1, max_length=100)
    readings: list[dict] = Field(..., min_items=1, max_items=100)


class DeviceRegisterRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=100)
    tenant_id: str = Field(..., min_length=1, max_length=100)
    field_id: str = Field(..., min_length=1, max_length=100)
    device_type: str = Field(..., min_length=1, max_length=50)
    name_ar: str = Field(..., min_length=1, max_length=200)
    name_en: str = Field(..., min_length=1, max_length=200)
    location: Optional[dict] = None
    metadata: Optional[dict] = None


# ============== Authorization & Validation Functions ==============


def validate_device_authorization(
    device_id: str, tenant_id: str, field_id: str
) -> bool:
    """
    Validate that device is authorized for the tenant and field
    """
    device = registry.get(device_id)

    if not device:
        logger.error(
            f"Device authorization failed: Device not found. "
            f"Device: {device_id}, Tenant: {tenant_id}, Field: {field_id}"
        )
        return False

    # Check tenant isolation
    if device.tenant_id != tenant_id:
        logger.error(
            f"Tenant isolation violation. "
            f"Device: {device_id}, Device tenant: {device.tenant_id}, "
            f"Requested tenant: {tenant_id}"
        )
        return False

    # Check field association
    if device.field_id != field_id:
        logger.error(
            f"Field mismatch. "
            f"Device: {device_id}, Device field: {device.field_id}, "
            f"Requested field: {field_id}"
        )
        return False

    return True


def validate_sensor_reading(
    device_id: str, tenant_id: str, field_id: str, sensor_type: str, value: float
) -> None:
    """
    Comprehensive validation for sensor reading
    Raises HTTPException if validation fails
    """
    # 1. Check device exists
    device = registry.get(device_id)
    if not device:
        logger.error(f"Sensor reading rejected: Device {device_id} not registered")
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not registered. Please register device first.",
        )

    # 2. Validate device authorization
    if not validate_device_authorization(device_id, tenant_id, field_id):
        raise HTTPException(
            status_code=403, detail="Device not authorized for this tenant or field"
        )

    # 3. Value range already validated by Pydantic model
    logger.info(
        f"Sensor reading validated. "
        f"Device: {device_id}, Tenant: {tenant_id}, Type: {sensor_type}, Value: {value}"
    )


# ============== Sensor Endpoints ==============


@app.post("/sensor/reading")
async def post_sensor_reading(req: SensorReadingRequest):
    """
    HTTP endpoint to submit sensor reading

    Security features:
    - Requires device to be registered first
    - Validates tenant isolation
    - Validates field association
    - Validates sensor value ranges
    - Logs all operations for audit trail

    Alternative to MQTT for devices that support HTTP
    """
    if not publisher:
        logger.error("Sensor reading rejected: Publisher not available")
        raise HTTPException(status_code=503, detail="Publisher not available")

    # Validate device authorization and sensor reading
    validate_sensor_reading(
        req.device_id, req.tenant_id, req.field_id, req.sensor_type, req.value
    )

    timestamp = req.timestamp or datetime.now(timezone.utc).isoformat()

    # Update device status
    registry.update_status(
        device_id=req.device_id,
        last_reading={
            "sensor_type": req.sensor_type,
            "value": req.value,
            "unit": req.unit,
        },
    )

    # Publish to event system
    event_id = await publisher.publish_sensor_reading(
        tenant_id=req.tenant_id,
        field_id=req.field_id,
        device_id=req.device_id,
        sensor_type=req.sensor_type,
        value=req.value,
        unit=req.unit,
        timestamp=timestamp,
        metadata=req.metadata,
    )

    logger.info(
        f"Sensor reading published. "
        f"Event: {event_id}, Device: {req.device_id}, Type: {req.sensor_type}"
    )

    return {
        "status": "ok",
        "event_id": event_id,
        "device_id": req.device_id,
        "sensor_type": req.sensor_type,
        "value": req.value,
    }


@app.post("/sensor/batch")
async def post_batch_readings(req: BatchReadingRequest):
    """
    Submit multiple sensor readings at once

    Security features:
    - Validates device exists and is registered
    - Validates tenant isolation
    - Validates field association
    - Validates each sensor value range
    - Rejects entire batch if any validation fails
    """
    if not publisher:
        logger.error("Batch reading rejected: Publisher not available")
        raise HTTPException(status_code=503, detail="Publisher not available")

    # First, validate device exists and authorization (once for all readings)
    device = registry.get(req.device_id)
    if not device:
        logger.error(f"Batch reading rejected: Device {req.device_id} not registered")
        raise HTTPException(
            status_code=404,
            detail=f"Device {req.device_id} not registered. Please register device first.",
        )

    if not validate_device_authorization(req.device_id, req.tenant_id, req.field_id):
        raise HTTPException(
            status_code=403, detail="Device not authorized for this tenant or field"
        )

    event_ids = []
    validated_count = 0

    for idx, reading in enumerate(req.readings):
        try:
            sensor_type = reading.get("type") or reading.get("sensor_type")
            value = reading.get("value") or reading.get("v")
            unit = reading.get("unit") or reading.get("u") or ""

            if not sensor_type or value is None:
                logger.warning(
                    f"Skipping reading {idx}: missing sensor_type or value. "
                    f"Device: {req.device_id}"
                )
                continue

            # Validate value range
            sensor_type_lower = sensor_type.lower()
            if sensor_type_lower in SENSOR_RANGES:
                range_config = SENSOR_RANGES[sensor_type_lower]
                value_float = float(value)
                if (
                    value_float < range_config["min"]
                    or value_float > range_config["max"]
                ):
                    logger.error(
                        f"Batch reading {idx} rejected: Value {value_float} out of range "
                        f"for {sensor_type}. Expected {range_config['min']} to {range_config['max']}"
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Reading {idx}: Value {value_float} out of range for {sensor_type}",
                    )

            event_id = await publisher.publish_sensor_reading(
                tenant_id=req.tenant_id,
                field_id=req.field_id,
                device_id=req.device_id,
                sensor_type=sensor_type,
                value=float(value),
                unit=unit,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            event_ids.append(event_id)
            validated_count += 1

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(
                f"Error processing batch reading {idx} for device {req.device_id}: {e}"
            )
            raise HTTPException(
                status_code=400, detail=f"Error processing reading {idx}: {str(e)}"
            )

    # Update device status
    registry.update_status(device_id=req.device_id)

    logger.info(
        f"Batch reading published. "
        f"Device: {req.device_id}, Count: {validated_count}, Events: {len(event_ids)}"
    )

    return {
        "status": "ok",
        "count": len(event_ids),
        "validated_count": validated_count,
        "event_ids": event_ids,
    }


# ============== Device Endpoints ==============


@app.post("/device/register")
async def register_device(req: DeviceRegisterRequest):
    """Register a new device"""
    device = registry.register(
        device_id=req.device_id,
        tenant_id=req.tenant_id,
        field_id=req.field_id,
        device_type=req.device_type,
        name_ar=req.name_ar,
        name_en=req.name_en,
        location=req.location,
        metadata=req.metadata or {},
    )

    # Publish registration event
    if publisher:
        await publisher.publish_device_registered(
            tenant_id=req.tenant_id,
            device_id=req.device_id,
            field_id=req.field_id,
            device_type=req.device_type,
            name_ar=req.name_ar,
            name_en=req.name_en,
        )

    return {
        "status": "ok",
        "device": device.to_dict(),
    }


@app.get("/device/{device_id}")
def get_device(device_id: str):
    """Get device information"""
    device = registry.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return device.to_dict()


@app.get("/device/{device_id}/status")
def get_device_status(device_id: str):
    """Get device status"""
    device = registry.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "device_id": device_id,
        "status": device.status,
        "is_online": device.is_online(),
        "last_seen": device.last_seen,
        "last_reading": device.last_reading,
        "battery_level": device.battery_level,
        "signal_strength": device.signal_strength,
    }


@app.get("/devices")
def list_devices(field_id: str = None, device_type: str = None):
    """List registered devices"""
    if field_id:
        devices = registry.get_by_field(field_id)
    elif device_type:
        devices = registry.get_by_type(device_type)
    else:
        devices = registry.list_all()

    return {
        "devices": [d.to_dict() for d in devices],
        "count": len(devices),
    }


@app.delete("/device/{device_id}")
def delete_device(device_id: str):
    """Remove device from registry"""
    if not registry.delete(device_id):
        raise HTTPException(status_code=404, detail="Device not found")

    return {"status": "ok", "device_id": device_id}


# ============== Field Endpoints ==============


@app.get("/field/{field_id}/devices")
def get_field_devices(field_id: str):
    """Get all devices for a field"""
    devices = registry.get_by_field(field_id)
    return {
        "field_id": field_id,
        "devices": [d.to_dict() for d in devices],
        "count": len(devices),
    }


@app.get("/field/{field_id}/latest")
def get_field_latest_readings(field_id: str):
    """Get latest readings from all devices in a field"""
    devices = registry.get_by_field(field_id)

    readings = []
    for device in devices:
        if device.last_reading:
            readings.append(
                {
                    "device_id": device.device_id,
                    "device_type": device.device_type,
                    **device.last_reading,
                    "last_seen": device.last_seen,
                }
            )

    return {
        "field_id": field_id,
        "readings": readings,
        "count": len(readings),
    }


# ============== Stats ==============


@app.get("/stats")
def get_stats():
    """Get gateway statistics"""
    pub_stats = publisher.get_stats() if publisher else {}
    reg_stats = registry.get_stats() if registry else {}

    return {
        "publisher": pub_stats,
        "registry": reg_stats,
        "mqtt": {
            "broker": MQTT_BROKER,
            "topic": MQTT_TOPIC,
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8106))
    uvicorn.run(app, host="0.0.0.0", port=port)
