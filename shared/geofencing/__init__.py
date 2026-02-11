"""
SAHOOL Geofencing Module - وحدة السياج الجغرافي
Equipment theft protection and zone management

Features:
- Geofence creation and management - إنشاء وإدارة السياج الجغرافي
- Real-time position monitoring - مراقبة الموقع في الوقت الفعلي
- Alert generation on boundary violations - إنشاء تنبيهات عند انتهاك الحدود
- Multi-zone support (allowed, restricted, sensitive) - دعم متعدد المناطق

Version: 1.0.0
"""

from .alerts import (
    generate_entry_alert,
    generate_exit_alert,
    generate_speed_alert,
    generate_theft_alert,
)
from .engine import (
    GeofenceEngine,
    calculate_distance_to_boundary,
    check_position_in_geofence,
    create_circular_geofence,
    create_polygon_geofence,
)
from .models import (
    AlertSeverity,
    AlertType,
    EquipmentZoneStatus,
    Geofence,
    GeofenceAlert,
    GeofenceType,
    PositionUpdate,
    ZoneStatus,
)

__all__ = [
    # Models
    "Geofence",
    "GeofenceType",
    "GeofenceAlert",
    "AlertType",
    "AlertSeverity",
    "PositionUpdate",
    "ZoneStatus",
    "EquipmentZoneStatus",
    # Engine
    "GeofenceEngine",
    "check_position_in_geofence",
    "calculate_distance_to_boundary",
    "create_circular_geofence",
    "create_polygon_geofence",
    # Alerts
    "generate_exit_alert",
    "generate_entry_alert",
    "generate_speed_alert",
    "generate_theft_alert",
]
