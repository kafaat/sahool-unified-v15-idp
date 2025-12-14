"""
Device Registry - SAHOOL IoT Gateway
Lightweight device management and status tracking
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


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
    last_seen: Optional[str] = None
    last_reading: Optional[dict] = None
    firmware_version: Optional[str] = None
    battery_level: Optional[float] = None
    signal_strength: Optional[int] = None  # RSSI in dBm
    location: Optional[dict] = None  # {"lat": ..., "lng": ...}
    metadata: dict = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return asdict(self)

    def is_online(self, timeout_minutes: int = 15) -> bool:
        """Check if device is online based on last_seen"""
        if not self.last_seen:
            return False
        try:
            last = datetime.fromisoformat(self.last_seen.replace("Z", "+00:00"))
            threshold = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
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
        now = datetime.now(timezone.utc).isoformat()

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

    def get(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self._devices.get(device_id)

    def get_by_field(self, field_id: str) -> list[Device]:
        """Get all devices for a field"""
        return [d for d in self._devices.values() if d.field_id == field_id]

    def get_by_tenant(self, tenant_id: str) -> list[Device]:
        """Get all devices for a tenant"""
        return [d for d in self._devices.values() if d.tenant_id == tenant_id]

    def get_by_type(self, device_type: str) -> list[Device]:
        """Get all devices of a specific type"""
        return [d for d in self._devices.values() if d.device_type == device_type]

    def update_status(
        self,
        device_id: str,
        status: DeviceStatus = None,
        last_reading: dict = None,
        battery_level: float = None,
        signal_strength: int = None,
    ) -> Optional[Device]:
        """Update device status after receiving data"""
        device = self._devices.get(device_id)
        if not device:
            return None

        now = datetime.now(timezone.utc).isoformat()
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


# Global registry instance
_registry: Optional[DeviceRegistry] = None


def get_registry() -> DeviceRegistry:
    """Get or create global registry instance"""
    global _registry
    if _registry is None:
        _registry = DeviceRegistry()
    return _registry
