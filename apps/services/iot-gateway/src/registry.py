"""
Device Registry - SAHOOL IoT Gateway
Lightweight device management and status tracking

Supports both in-memory and Redis-backed storage for persistence.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis

logger = logging.getLogger("iot-gateway.registry")

# Redis key prefixes
DEVICE_PREFIX = "iot:device:"
DEVICE_INDEX = "iot:devices"
DEVICE_FIELD_INDEX = "iot:field:"
DEVICE_TENANT_INDEX = "iot:tenant:"
DEVICE_TYPE_INDEX = "iot:type:"


class DeviceStatus(Enum):
    """Device status states"""

    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


class DeviceType(Enum):
    """Device types"""

    SOIL_SENSOR = "soil_sensor"
    WEATHER_STATION = "weather_station"
    WATER_SENSOR = "water_sensor"
    FLOW_METER = "flow_meter"
    VALVE_CONTROLLER = "valve_controller"
    GATEWAY = "gateway"
    CAMERA = "camera"
    UNKNOWN = "unknown"


@dataclass
class Device:
    """Device registration record"""

    device_id: str
    tenant_id: str
    field_id: str
    device_type: str
    name_ar: str
    name_en: str
    status: str = DeviceStatus.UNKNOWN.value
    last_seen: str | None = None
    last_reading: dict | None = None
    firmware_version: str | None = None
    battery_level: float | None = None
    signal_strength: int | None = None  # RSSI in dBm
    location: dict | None = None  # {"lat": ..., "lng": ...}
    metadata: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def is_online(self, timeout_minutes: int = 15) -> bool:
        """Check if device is online based on last_seen"""
        if not self.last_seen:
            return False
        try:
            last = datetime.fromisoformat(self.last_seen.replace("Z", "+00:00"))
            threshold = datetime.now(UTC) - timedelta(minutes=timeout_minutes)
            return last > threshold
        except (ValueError, TypeError):
            return False


class DeviceRegistry:
    """
    In-memory device registry with optional persistence

    For production, replace with database-backed implementation
    """

    def __init__(self):
        self._devices: dict[str, Device] = {}
        self._offline_threshold_minutes = 15

    def register(
        self,
        device_id: str,
        tenant_id: str,
        field_id: str,
        device_type: str,
        name_ar: str,
        name_en: str,
        **kwargs,
    ) -> Device:
        """Register a new device or update existing"""
        now = datetime.now(UTC).isoformat()

        if device_id in self._devices:
            # Update existing
            device = self._devices[device_id]
            device.tenant_id = tenant_id
            device.field_id = field_id
            device.device_type = device_type
            device.name_ar = name_ar
            device.name_en = name_en
            device.updated_at = now
            for k, v in kwargs.items():
                if hasattr(device, k):
                    setattr(device, k, v)
        else:
            # Create new
            device = Device(
                device_id=device_id,
                tenant_id=tenant_id,
                field_id=field_id,
                device_type=device_type,
                name_ar=name_ar,
                name_en=name_en,
                **kwargs,
            )
            self._devices[device_id] = device

        print(f"📝 Registered device: {device_id} ({device_type})")
        return device

    def get(self, device_id: str) -> Device | None:
        """Get device by ID"""
        return self._devices.get(device_id)

    def get_by_field(self, field_id: str, tenant_id: str = "") -> list[Device]:
        """Get all devices for a field, optionally filtered by tenant"""
        return [
            d for d in self._devices.values()
            if d.field_id == field_id and (not tenant_id or d.tenant_id == tenant_id)
        ]

    def get_by_tenant(self, tenant_id: str) -> list[Device]:
        """Get all devices for a tenant"""
        return [d for d in self._devices.values() if d.tenant_id == tenant_id]

    def get_by_type(self, device_type: str, tenant_id: str = "") -> list[Device]:
        """Get all devices of a specific type, optionally filtered by tenant"""
        return [
            d for d in self._devices.values()
            if d.device_type == device_type and (not tenant_id or d.tenant_id == tenant_id)
        ]

    def update_status(
        self,
        device_id: str,
        status: DeviceStatus = None,
        last_reading: dict = None,
        battery_level: float = None,
        signal_strength: int = None,
    ) -> Device | None:
        """Update device status after receiving data"""
        device = self._devices.get(device_id)
        if not device:
            return None

        now = datetime.now(UTC).isoformat()
        device.last_seen = now
        device.updated_at = now

        if status:
            device.status = status.value
        else:
            device.status = DeviceStatus.ONLINE.value

        if last_reading:
            device.last_reading = last_reading

        if battery_level is not None:
            device.battery_level = battery_level
            # Set warning if battery low
            if battery_level < 20:
                device.status = DeviceStatus.WARNING.value

        if signal_strength is not None:
            device.signal_strength = signal_strength

        return device

    def check_offline_devices(self) -> list[Device]:
        """Check for devices that have gone offline"""
        offline = []

        for device in self._devices.values():
            if device.status == DeviceStatus.OFFLINE.value:
                continue

            if not device.is_online(self._offline_threshold_minutes):
                device.status = DeviceStatus.OFFLINE.value
                offline.append(device)
                print(f"⚠️ Device offline: {device.device_id}")

        return offline

    def delete(self, device_id: str) -> bool:
        """Remove device from registry"""
        if device_id in self._devices:
            del self._devices[device_id]
            print(f"🗑️ Deleted device: {device_id}")
            return True
        return False

    def list_all(self) -> list[Device]:
        """List all registered devices"""
        return list(self._devices.values())

    def get_stats(self) -> dict:
        """Get registry statistics"""
        devices = list(self._devices.values())
        online = sum(1 for d in devices if d.status == DeviceStatus.ONLINE.value)
        offline = sum(1 for d in devices if d.status == DeviceStatus.OFFLINE.value)
        warning = sum(1 for d in devices if d.status == DeviceStatus.WARNING.value)

        by_type = {}
        for d in devices:
            by_type[d.device_type] = by_type.get(d.device_type, 0) + 1

        return {
            "total": len(devices),
            "online": online,
            "offline": offline,
            "warning": warning,
            "by_type": by_type,
        }

    def auto_register(
        self,
        device_id: str,
        tenant_id: str,
        field_id: str,
        sensor_type: str,
    ) -> Device:
        """
        Auto-register device on first reading

        Creates a minimal registration that can be updated later
        """
        if device_id in self._devices:
            return self._devices[device_id]

        # Infer device type from sensor type
        device_type = self._infer_device_type(sensor_type)

        return self.register(
            device_id=device_id,
            tenant_id=tenant_id,
            field_id=field_id,
            device_type=device_type,
            name_ar=f"جهاز {device_id}",
            name_en=f"Device {device_id}",
        )

    def _infer_device_type(self, sensor_type: str) -> str:
        """Infer device type from sensor type"""
        MAPPINGS = {
            "soil_moisture": DeviceType.SOIL_SENSOR.value,
            "soil_temperature": DeviceType.SOIL_SENSOR.value,
            "soil_ec": DeviceType.SOIL_SENSOR.value,
            "soil_ph": DeviceType.SOIL_SENSOR.value,
            "air_temperature": DeviceType.WEATHER_STATION.value,
            "air_humidity": DeviceType.WEATHER_STATION.value,
            "wind_speed": DeviceType.WEATHER_STATION.value,
            "rainfall": DeviceType.WEATHER_STATION.value,
            "water_level": DeviceType.WATER_SENSOR.value,
            "water_flow": DeviceType.FLOW_METER.value,
        }
        return MAPPINGS.get(sensor_type, DeviceType.UNKNOWN.value)


class RedisDeviceRegistry(DeviceRegistry):
    """
    Redis-backed device registry with persistence

    Extends DeviceRegistry with Redis storage for persistence across restarts.
    Falls back to in-memory storage if Redis is unavailable.
    """

    def __init__(self, redis_client: "Redis"):
        super().__init__()
        self._redis = redis_client
        self._sync_complete = False
        logger.info("Redis-backed device registry initialized")

    async def _sync_from_redis(self) -> None:
        """Load all devices from Redis into memory on startup"""
        if self._sync_complete:
            return

        try:
            device_ids = await self._redis.smembers(DEVICE_INDEX)
            for device_id_bytes in device_ids:
                device_id = device_id_bytes.decode() if isinstance(device_id_bytes, bytes) else device_id_bytes
                data = await self._redis.hgetall(f"{DEVICE_PREFIX}{device_id}")
                if data:
                    device = self._deserialize_device(device_id, data)
                    if device:
                        self._devices[device_id] = device

            self._sync_complete = True
            logger.info(f"Synced {len(self._devices)} devices from Redis")
        except Exception as e:
            logger.error(f"Failed to sync from Redis: {e}")

    def _serialize_device(self, device: Device) -> dict:
        """Serialize device to Redis hash format"""
        data = device.to_dict()
        # Convert nested dicts to JSON strings
        for key in ["last_reading", "location", "metadata"]:
            if data.get(key) is not None:
                data[key] = json.dumps(data[key])
            else:
                data[key] = ""
        return {k: str(v) if v is not None else "" for k, v in data.items()}

    def _deserialize_device(self, device_id: str, data: dict) -> Device | None:
        """Deserialize device from Redis hash format"""
        try:
            # Decode bytes if needed
            decoded = {}
            for k, v in data.items():
                key = k.decode() if isinstance(k, bytes) else k
                val = v.decode() if isinstance(v, bytes) else v
                decoded[key] = val

            # Parse JSON fields
            for key in ["last_reading", "location", "metadata"]:
                if decoded.get(key) and decoded[key] != "":
                    try:
                        decoded[key] = json.loads(decoded[key])
                    except json.JSONDecodeError:
                        decoded[key] = None if key != "metadata" else {}
                else:
                    decoded[key] = None if key != "metadata" else {}

            # Convert numeric fields
            if decoded.get("battery_level") and decoded["battery_level"] != "None":
                try:
                    decoded["battery_level"] = float(decoded["battery_level"])
                except (ValueError, TypeError):
                    decoded["battery_level"] = None
            else:
                decoded["battery_level"] = None

            if decoded.get("signal_strength") and decoded["signal_strength"] != "None":
                try:
                    decoded["signal_strength"] = int(decoded["signal_strength"])
                except (ValueError, TypeError):
                    decoded["signal_strength"] = None
            else:
                decoded["signal_strength"] = None

            # Handle None string values
            for key in ["last_seen", "firmware_version"]:
                if decoded.get(key) in ("None", "", None):
                    decoded[key] = None

            return Device(
                device_id=decoded.get("device_id", device_id),
                tenant_id=decoded.get("tenant_id", ""),
                field_id=decoded.get("field_id", ""),
                device_type=decoded.get("device_type", "unknown"),
                name_ar=decoded.get("name_ar", ""),
                name_en=decoded.get("name_en", ""),
                status=decoded.get("status", DeviceStatus.UNKNOWN.value),
                last_seen=decoded.get("last_seen"),
                last_reading=decoded.get("last_reading"),
                firmware_version=decoded.get("firmware_version"),
                battery_level=decoded.get("battery_level"),
                signal_strength=decoded.get("signal_strength"),
                location=decoded.get("location"),
                metadata=decoded.get("metadata", {}),
                created_at=decoded.get("created_at", datetime.now(UTC).isoformat()),
                updated_at=decoded.get("updated_at", datetime.now(UTC).isoformat()),
            )
        except Exception as e:
            logger.error(f"Failed to deserialize device {device_id}: {e}")
            return None

    async def _save_to_redis(self, device: Device) -> None:
        """Save device to Redis"""
        try:
            device_data = self._serialize_device(device)
            await self._redis.hset(f"{DEVICE_PREFIX}{device.device_id}", mapping=device_data)
            await self._redis.sadd(DEVICE_INDEX, device.device_id)
            await self._redis.sadd(f"{DEVICE_FIELD_INDEX}{device.field_id}", device.device_id)
            await self._redis.sadd(f"{DEVICE_TENANT_INDEX}{device.tenant_id}", device.device_id)
            await self._redis.sadd(f"{DEVICE_TYPE_INDEX}{device.device_type}", device.device_id)
            logger.debug(f"Saved device {device.device_id} to Redis")
        except Exception as e:
            logger.error(f"Failed to save device {device.device_id} to Redis: {e}")

    async def _delete_from_redis(self, device: Device) -> None:
        """Delete device from Redis"""
        try:
            await self._redis.delete(f"{DEVICE_PREFIX}{device.device_id}")
            await self._redis.srem(DEVICE_INDEX, device.device_id)
            await self._redis.srem(f"{DEVICE_FIELD_INDEX}{device.field_id}", device.device_id)
            await self._redis.srem(f"{DEVICE_TENANT_INDEX}{device.tenant_id}", device.device_id)
            await self._redis.srem(f"{DEVICE_TYPE_INDEX}{device.device_type}", device.device_id)
            logger.debug(f"Deleted device {device.device_id} from Redis")
        except Exception as e:
            logger.error(f"Failed to delete device {device.device_id} from Redis: {e}")

    async def register_async(
        self,
        device_id: str,
        tenant_id: str,
        field_id: str,
        device_type: str,
        name_ar: str,
        name_en: str,
        **kwargs,
    ) -> Device:
        """Register a new device with Redis persistence"""
        device = self.register(device_id, tenant_id, field_id, device_type, name_ar, name_en, **kwargs)
        await self._save_to_redis(device)
        return device

    async def update_status_async(
        self,
        device_id: str,
        status: DeviceStatus = None,
        last_reading: dict = None,
        battery_level: float = None,
        signal_strength: int = None,
    ) -> Device | None:
        """Update device status with Redis persistence"""
        device = self.update_status(device_id, status, last_reading, battery_level, signal_strength)
        if device:
            await self._save_to_redis(device)
        return device

    async def delete_async(self, device_id: str) -> bool:
        """Remove device with Redis persistence"""
        device = self.get(device_id)
        if device:
            await self._delete_from_redis(device)
        return self.delete(device_id)

    async def auto_register_async(
        self,
        device_id: str,
        tenant_id: str,
        field_id: str,
        sensor_type: str,
    ) -> Device:
        """Auto-register device with Redis persistence"""
        if device_id in self._devices:
            return self._devices[device_id]

        device_type = self._infer_device_type(sensor_type)
        return await self.register_async(
            device_id=device_id,
            tenant_id=tenant_id,
            field_id=field_id,
            device_type=device_type,
            name_ar=f"جهاز {device_id}",
            name_en=f"Device {device_id}",
        )

    async def get_by_field_async(self, field_id: str) -> list[Device]:
        """Get all devices for a field using Redis index"""
        try:
            device_ids = await self._redis.smembers(f"{DEVICE_FIELD_INDEX}{field_id}")
            devices = []
            for device_id_bytes in device_ids:
                device_id = device_id_bytes.decode() if isinstance(device_id_bytes, bytes) else device_id_bytes
                device = self.get(device_id)
                if device:
                    devices.append(device)
            return devices
        except Exception as e:
            logger.error(f"Failed to get devices by field from Redis: {e}")
            return self.get_by_field(field_id)

    async def get_by_tenant_async(self, tenant_id: str) -> list[Device]:
        """Get all devices for a tenant using Redis index"""
        try:
            device_ids = await self._redis.smembers(f"{DEVICE_TENANT_INDEX}{tenant_id}")
            devices = []
            for device_id_bytes in device_ids:
                device_id = device_id_bytes.decode() if isinstance(device_id_bytes, bytes) else device_id_bytes
                device = self.get(device_id)
                if device:
                    devices.append(device)
            return devices
        except Exception as e:
            logger.error(f"Failed to get devices by tenant from Redis: {e}")
            return self.get_by_tenant(tenant_id)

    async def get_by_type_async(self, device_type: str) -> list[Device]:
        """Get all devices of a specific type using Redis index"""
        try:
            device_ids = await self._redis.smembers(f"{DEVICE_TYPE_INDEX}{device_type}")
            devices = []
            for device_id_bytes in device_ids:
                device_id = device_id_bytes.decode() if isinstance(device_id_bytes, bytes) else device_id_bytes
                device = self.get(device_id)
                if device:
                    devices.append(device)
            return devices
        except Exception as e:
            logger.error(f"Failed to get devices by type from Redis: {e}")
            return self.get_by_type(device_type)


# Global registry instance
_registry: DeviceRegistry | None = None
_redis_client: "Redis | None" = None


def get_registry() -> DeviceRegistry:
    """Get or create global registry instance"""
    global _registry
    if _registry is None:
        _registry = DeviceRegistry()
    return _registry


async def get_redis_registry(redis_client: "Redis") -> RedisDeviceRegistry:
    """Get or create Redis-backed registry instance"""
    global _registry, _redis_client

    if _registry is not None and isinstance(_registry, RedisDeviceRegistry):
        return _registry

    _redis_client = redis_client
    _registry = RedisDeviceRegistry(redis_client)
    await _registry._sync_from_redis()
    return _registry


def set_registry(registry: DeviceRegistry) -> None:
    """Set the global registry instance (for testing or custom implementations)"""
    global _registry
    _registry = registry
