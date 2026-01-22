"""
Geofencing Models - نماذج السياج الجغرافي
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class GeofenceType(str, Enum):
    """Type of geofence zone"""
    ALLOWED = "allowed"  # منطقة مسموح بها
    RESTRICTED = "restricted"  # منطقة مقيدة
    SENSITIVE = "sensitive"  # منطقة حساسة (مثل مصادر المياه)
    PARKING = "parking"  # منطقة وقوف
    FIELD = "field"  # حقل زراعي
    FARM_BOUNDARY = "farm_boundary"  # حدود المزرعة


class AlertType(str, Enum):
    """Type of geofence alert"""
    EXIT = "exit"  # خروج من المنطقة
    ENTRY = "entry"  # دخول للمنطقة
    SPEEDING = "speeding"  # سرعة زائدة
    THEFT = "theft"  # اشتباه سرقة
    IDLE = "idle"  # توقف طويل
    UNAUTHORIZED_MOVE = "unauthorized_move"  # حركة غير مصرح بها


class AlertSeverity(str, Enum):
    """Alert severity level"""
    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # مرتفع
    CRITICAL = "critical"  # حرج


class ZoneStatus(str, Enum):
    """Equipment status relative to a zone"""
    INSIDE = "inside"  # داخل المنطقة
    OUTSIDE = "outside"  # خارج المنطقة
    APPROACHING = "approaching"  # يقترب
    LEAVING = "leaving"  # يغادر


@dataclass
class LatLng:
    """Geographic coordinate"""
    lat: float
    lng: float

    def to_tuple(self) -> tuple[float, float]:
        return (self.lat, self.lng)

    def to_dict(self) -> dict:
        return {"lat": self.lat, "lng": self.lng}


@dataclass
class Geofence:
    """
    Geofence definition - تعريف السياج الجغرافي

    Supports both circular and polygon geofences
    """
    id: str
    tenant_id: str
    name: str
    name_ar: str

    # Type
    geofence_type: GeofenceType

    # Geometry - either circle or polygon
    center: Optional[LatLng] = None  # For circular geofence
    radius_m: Optional[float] = None  # For circular geofence (meters)
    boundary: Optional[list[LatLng]] = None  # For polygon geofence

    # Alert settings
    alert_on_exit: bool = True  # تنبيه عند الخروج
    alert_on_entry: bool = False  # تنبيه عند الدخول
    alert_channels: list[str] = field(default_factory=lambda: ["push", "sms"])

    # Speed limits (for speeding alerts)
    max_speed_kmh: Optional[float] = None

    # Operating hours (optional)
    operating_hours_start: Optional[str] = None  # e.g., "06:00"
    operating_hours_end: Optional[str] = None  # e.g., "18:00"
    alert_outside_hours: bool = False

    # Buffer zone for approaching alerts
    buffer_distance_m: float = 50  # مسافة منطقة الحماية

    # Associated equipment
    equipment_ids: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "geofence_type": self.geofence_type.value,
            "center": self.center.to_dict() if self.center else None,
            "radius_m": self.radius_m,
            "boundary": [p.to_dict() for p in self.boundary] if self.boundary else None,
            "alert_on_exit": self.alert_on_exit,
            "alert_on_entry": self.alert_on_entry,
            "alert_channels": self.alert_channels,
            "max_speed_kmh": self.max_speed_kmh,
            "buffer_distance_m": self.buffer_distance_m,
            "equipment_ids": self.equipment_ids,
            "is_active": self.is_active,
        }


@dataclass
class PositionUpdate:
    """Equipment position update - تحديث موقع المعدة"""
    equipment_id: str
    tenant_id: str
    timestamp: datetime

    # Position
    lat: float
    lng: float
    accuracy_m: Optional[float] = None

    # Speed and heading
    speed_kmh: Optional[float] = None
    heading_degrees: Optional[float] = None

    # Engine status
    engine_on: Optional[bool] = None
    fuel_percent: Optional[float] = None

    # Previous position (for movement detection)
    prev_lat: Optional[float] = None
    prev_lng: Optional[float] = None
    prev_timestamp: Optional[datetime] = None


@dataclass
class GeofenceAlert:
    """
    Geofence alert - تنبيه السياج الجغرافي
    """
    alert_id: str
    tenant_id: str
    equipment_id: str
    equipment_name: str
    equipment_name_ar: str

    # Alert details
    alert_type: AlertType
    severity: AlertSeverity
    timestamp: datetime

    # Geofence info
    geofence_id: str
    geofence_name: str
    geofence_name_ar: str

    # Position
    lat: float
    lng: float
    speed_kmh: Optional[float] = None

    # Distance info
    distance_to_boundary_m: Optional[float] = None

    # Messages
    title_en: str = ""
    title_ar: str = ""
    message_en: str = ""
    message_ar: str = ""

    # Alert channels
    channels: list[str] = field(default_factory=lambda: ["push", "sms"])

    # Acknowledgment
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

    # Actions taken
    actions_taken: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for NATS publishing"""
        return {
            "alert_id": self.alert_id,
            "tenant_id": self.tenant_id,
            "equipment_id": self.equipment_id,
            "equipment_name": self.equipment_name,
            "equipment_name_ar": self.equipment_name_ar,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "geofence_id": self.geofence_id,
            "geofence_name": self.geofence_name,
            "geofence_name_ar": self.geofence_name_ar,
            "position": {"lat": self.lat, "lng": self.lng},
            "speed_kmh": self.speed_kmh,
            "distance_to_boundary_m": self.distance_to_boundary_m,
            "title_en": self.title_en,
            "title_ar": self.title_ar,
            "message_en": self.message_en,
            "message_ar": self.message_ar,
            "channels": self.channels,
            "acknowledged": self.acknowledged,
        }


@dataclass
class EquipmentZoneStatus:
    """
    Equipment's current status relative to all geofences
    حالة المعدة بالنسبة لجميع السياجات الجغرافية
    """
    equipment_id: str
    equipment_name: str
    timestamp: datetime

    # Current position
    lat: float
    lng: float

    # Zone statuses
    zones: list[dict] = field(default_factory=list)
    # Each zone: {geofence_id, geofence_name, status: ZoneStatus, distance_m}

    # Overall status
    is_within_allowed_zones: bool = True
    is_in_restricted_zone: bool = False
    nearest_boundary_distance_m: Optional[float] = None

    # Alerts
    active_alerts: list[str] = field(default_factory=list)  # Alert IDs
