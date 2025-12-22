"""
SAHOOL IoT Gateway - Main API Service
MQTT → NATS bridge for sensor data ingestion
Port: 8096
"""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .events import IoTPublisher, get_publisher
from .mqtt_client import MqttClient, MqttMessage
from .normalizer import normalize
from .registry import DeviceRegistry, DeviceStatus, get_registry

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sahool/sensors/#")
DEFAULT_TENANT = os.getenv("DEFAULT_TENANT", "default")


# Global state
mqtt_client: Optional[MqttClient] = None
publisher: Optional[IoTPublisher] = None
registry: Optional[DeviceRegistry] = None
mqtt_task: Optional[asyncio.Task] = None


async def handle_mqtt_message(msg: MqttMessage):
    """Process incoming MQTT message"""
    global publisher, registry

    try:
        # Normalize the reading
        reading = normalize(msg.payload, msg.topic)

        # Auto-register device if not known
        registry.auto_register(
            device_id=reading.device_id,
            tenant_id=DEFAULT_TENANT,
            field_id=reading.field_id,
            sensor_type=reading.sensor_type,
        )

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

    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")
        print(f"   Topic: {msg.topic}")
        print(f"   Payload: {msg.payload[:200]}...")


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
    )

    print(f"🔌 Starting MQTT listener on {MQTT_BROKER}:{MQTT_PORT}")
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

    print("✅ IoT Gateway ready on port 8096")

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
        "status": "ok",
        "service": "iot_gateway",
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


class SensorReadingRequest(BaseModel):
    device_id: str
    field_id: str
    sensor_type: str
    value: float
    unit: str = ""
    timestamp: Optional[str] = None
    metadata: Optional[dict] = None


class BatchReadingRequest(BaseModel):
    device_id: str
    field_id: str
    readings: list[dict]


class DeviceRegisterRequest(BaseModel):
    device_id: str
    tenant_id: str = DEFAULT_TENANT
    field_id: str
    device_type: str
    name_ar: str
    name_en: str
    location: Optional[dict] = None
    metadata: Optional[dict] = None


# ============== Sensor Endpoints ==============


@app.post("/sensor/reading")
async def post_sensor_reading(req: SensorReadingRequest):
    """
    HTTP endpoint to submit sensor reading

    Alternative to MQTT for devices that support HTTP
    """
    if not publisher:
        raise HTTPException(status_code=503, detail="Publisher not available")

    timestamp = req.timestamp or datetime.now(timezone.utc).isoformat()

    # Auto-register device
    registry.auto_register(
        device_id=req.device_id,
        tenant_id=DEFAULT_TENANT,
        field_id=req.field_id,
        sensor_type=req.sensor_type,
    )

    # Update status
    registry.update_status(
        device_id=req.device_id,
        last_reading={
            "sensor_type": req.sensor_type,
            "value": req.value,
            "unit": req.unit,
        },
    )

    # Publish
    event_id = await publisher.publish_sensor_reading(
        tenant_id=DEFAULT_TENANT,
        field_id=req.field_id,
        device_id=req.device_id,
        sensor_type=req.sensor_type,
        value=req.value,
        unit=req.unit,
        timestamp=timestamp,
        metadata=req.metadata,
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
    """Submit multiple sensor readings at once"""
    if not publisher:
        raise HTTPException(status_code=503, detail="Publisher not available")

    event_ids = []

    for reading in req.readings:
        sensor_type = reading.get("type") or reading.get("sensor_type")
        value = reading.get("value") or reading.get("v")
        unit = reading.get("unit") or reading.get("u") or ""

        if not sensor_type or value is None:
            continue

        event_id = await publisher.publish_sensor_reading(
            tenant_id=DEFAULT_TENANT,
            field_id=req.field_id,
            device_id=req.device_id,
            sensor_type=sensor_type,
            value=float(value),
            unit=unit,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        event_ids.append(event_id)

    # Update device status
    registry.update_status(device_id=req.device_id)

    return {
        "status": "ok",
        "count": len(event_ids),
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

    port = int(os.getenv("PORT", 8096))
    uvicorn.run(app, host="0.0.0.0", port=port)
