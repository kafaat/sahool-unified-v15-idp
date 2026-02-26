# Geofencing Module - وحدة السياج الجغرافي

Real-time geofence monitoring for agricultural equipment on the SAHOOL platform. Provides zone creation, live position tracking, boundary violation detection, speed enforcement, and theft detection using Haversine distance calculations and ray-casting polygon containment.

**Version**: 1.0.0 | **Python**: 3.11+

## File Structure

```
shared/geofencing/
├── __init__.py    # Public API and re-exports
├── models.py      # Geofence, PositionUpdate, GeofenceAlert, EquipmentZoneStatus
├── engine.py      # GeofenceEngine, point-in-polygon, Haversine distance, theft detection
└── alerts.py      # Alert generation helpers: exit, entry, speed, theft
```

## Key Components

### Geofence Types (`GeofenceType`)

| Type | Description | Default Alert |
|------|-------------|---------------|
| `ALLOWED` | Permitted operating area | Exit alert (HIGH) |
| `RESTRICTED` | Prohibited zone | Entry alert (HIGH) |
| `SENSITIVE` | Water sources, protected areas | Entry alert (CRITICAL) |
| `FARM_BOUNDARY` | Outer farm perimeter | Exit alert (CRITICAL) |
| `FIELD` | Individual crop field | Configurable |
| `PARKING` | Equipment storage area | Configurable |

### Alert Types (`AlertType`)
`EXIT`, `ENTRY`, `SPEEDING`, `THEFT`, `IDLE`, `UNAUTHORIZED_MOVE`

### Alert Severity (`AlertSeverity`)
`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`

### `GeofenceEngine`
Stateful engine that manages all geofences and equipment positions in memory. On each `update_position()` call it:
1. Detects zone entry/exit transitions vs. the previous position
2. Checks speed against per-zone `max_speed_kmh` limits
3. Runs theft heuristics (outside farm boundary + significant movement, high speed outside operating hours, rapid movement away from all allowed zones)
4. Returns a list of `GeofenceAlert` objects ready for NATS publishing

### Geometry Support
- **Circular**: defined by `center: LatLng` + `radius_m` — O(1) containment via Haversine
- **Polygon**: defined by `boundary: list[LatLng]` — ray-casting algorithm, distance to nearest edge

## Usage Example

```python
from shared.geofencing import (
    GeofenceEngine,
    create_circular_geofence,
    create_polygon_geofence,
    GeofenceType,
    PositionUpdate,
)
from datetime import datetime, timezone

engine = GeofenceEngine()

# Define the farm boundary (circular, 500m radius)
farm_fence = create_circular_geofence(
    tenant_id="farm_001",
    name="Al-Rashid Farm Boundary",
    name_ar="حدود مزرعة الراشد",
    center_lat=24.7136,
    center_lng=46.6753,
    radius_m=500.0,
    geofence_type=GeofenceType.FARM_BOUNDARY,
    alert_on_exit=True,
    alert_channels=["push", "sms", "whatsapp"],
)
engine.add_geofence(farm_fence)

# Define a restricted water source zone (polygon)
water_zone = create_polygon_geofence(
    tenant_id="farm_001",
    name="Irrigation Canal",
    name_ar="قناة الري",
    boundary=[
        (24.715, 46.674), (24.716, 46.674),
        (24.716, 46.676), (24.715, 46.676),
    ],
    geofence_type=GeofenceType.SENSITIVE,
    alert_on_entry=True,
    max_speed_kmh=5.0,
)
engine.add_geofence(water_zone)

# Process a GPS position update from a tractor
update = PositionUpdate(
    equipment_id="TRACTOR-001",
    tenant_id="farm_001",
    timestamp=datetime.now(timezone.utc),
    lat=24.7200,
    lng=46.6753,
    speed_kmh=35.0,
    engine_on=True,
    fuel_percent=72.0,
)

alerts = engine.update_position(update)
for alert in alerts:
    print(f"[{alert.severity}] {alert.title_en}")
    print(f"  AR: {alert.title_ar}")
    # Publish to NATS: sahool.geofence.{alert.alert_type}
    payload = alert.to_dict()

# Query current equipment status across all zones
status = engine.get_equipment_status("TRACTOR-001", "New Holland T7")
print(f"Within allowed zones: {status.is_within_allowed_zones}")
print(f"In restricted zone: {status.is_in_restricted_zone}")
print(f"Nearest boundary: {status.nearest_boundary_distance_m}m")

# Acknowledge an alert
engine.acknowledge_alert(alerts[0].alert_id, acknowledged_by="user-456")

# Get all unacknowledged alerts for the tenant
pending = engine.get_unacknowledged_alerts(tenant_id="farm_001")
```

## Buffer Zone and Operating Hours

```python
# Alert when equipment approaches within 50m of boundary
farm_fence = create_circular_geofence(
    ...,
    buffer_distance_m=50.0,       # approaching-alert threshold
    operating_hours_start="06:00",
    operating_hours_end="20:00",
    alert_outside_hours=True,      # alert if moving outside hours
)
```

## Integration Notes

- Publish `GeofenceAlert.to_dict()` to NATS subjects `sahool.geofence.exit`, `sahool.geofence.entry`, `sahool.geofence.theft`, etc. for downstream notification routing.
- `GeofenceEngine` is in-process and stateless between restarts; persist `Geofence` definitions and `PositionUpdate` history to PostgreSQL via `equipment-service` (port 8101).
- Theft detection uses three heuristics: outside all `FARM_BOUNDARY` zones with movement > 100m, high-speed movement (> 30 km/h) outside operating hours, and rapid movement (> 50 km/h) outside all allowed zones.
- Alert channels are configurable per geofence: `["push", "sms", "whatsapp", "call"]`.
