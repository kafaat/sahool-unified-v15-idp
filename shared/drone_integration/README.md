# shared/drone_integration

Drone flight planning and Variable Rate Application (VRA) for the SAHOOL platform.
Supports DJI agricultural drones and open-source MAVLink platforms (ArduPilot/PX4).

## File Structure

```
shared/drone_integration/
├── __init__.py          # Public API and module docstring
├── models.py            # All data models, enums, and dataclasses
├── flight_planner.py    # Flight path generation and weather assessment
└── vra.py               # Variable Rate Application prescription maps
```

## Key Components

### models.py

Core data classes and enumerations:

| Class | Purpose |
|-------|---------|
| `Coordinate` | GPS coordinate with altitude (lat, lng, alt_m, alt_agl_m) |
| `DroneSpecs` | Hardware specifications: payload, spray tank, camera, RTK |
| `Drone` | Drone asset with registration, maintenance, battery state |
| `Waypoint` | Single waypoint with speed, actions, spray parameters |
| `FlightPath` | Full path with KML and MAVLink export methods |
| `SprayMission` | Spray mission definition with PHI/REI compliance fields |
| `MappingMission` | Aerial mapping mission with overlap and GSD settings |
| `FlightLog` | Complete flight record with telemetry and GeoJSON export |
| `VRAZone` | Single VRA zone polygon with application rate |
| `PrescriptionMap` | Full VRA map as a GeoJSON FeatureCollection |
| `WeatherCheck` | Pre-flight weather assessment result |

Enumerations: `DroneType`, `FlightMode`, `FlightStatus`, `MissionStatus`,
`FlightPattern`, `ApplicationMode`, `SprayStatus`, `ImageryType`, `VRAZoneType`.

### flight_planner.py

Generates autonomous flight paths for agricultural fields.

**Supported flight patterns:**
- `PARALLEL` (boustrophedon) - default for spraying
- `CROSSHATCH` - double-pass for dense coverage
- `PERIMETER` - boundary inspection
- `CONTOUR` - slope-following
- `SPIRAL`

**Key classes and functions:**

| Symbol | Description |
|--------|-------------|
| `FlightPlanConfig` | Altitude, speed, swath, overlap, boundary buffer settings |
| `FlightPlanResult` | Resulting path, distance, spray volume, resource estimates |
| `FlightPlanner` | Main planner class; call `.plan()` with a boundary polygon |
| `create_spray_flight_plan()` | Convenience function for single-call spray mission creation |
| `create_mapping_flight_plan()` | Convenience function for orthomosaic/NDVI mapping missions |
| `assess_flight_weather()` | Classifies weather as OPTIMAL / ACCEPTABLE / MARGINAL / PROHIBITED |
| `estimate_flight_resources()` | Estimates battery cycles, spray fills, flight time |
| `haversine_distance()` | Great-circle distance between two coordinates |
| `calculate_polygon_area()` | Field area in hectares from boundary polygon |

**Safety limits enforced:** max altitude 120 m, max wind 8 m/s, min visibility 3 km.

### vra.py

Generates Variable Rate Application prescription maps from raster or zone data.

**Supported input sources (`VRASourceType`):**
NDVI, LAI, yield history, soil EC/OM/N/P/K, pest pressure, weed density, thermal, custom.

**Classification methods (`ClassificationMethod`):**
QUANTILE, EQUAL_INTERVAL, JENKS (natural breaks), MANUAL thresholds, STANDARD_DEVIATION.

**Rate adjustment modes:** PROPORTIONAL, INVERSE, THRESHOLD, CUSTOM.

| Symbol | Description |
|--------|-------------|
| `VRAConfig` | Zone count, base rate, min/max rate, classification method |
| `VRAGenerator` | Generates `PrescriptionMap` from grid data or NDVI values |
| `create_ndvi_prescription()` | Convenience function: NDVI array → prescription map |
| `create_spot_spray_map()` | Generates targeted spray zones from detection hotspots |
| `export_prescription_to_shapefile()` | Exports zones to Shapefile format |

## Usage Examples

### Spray Mission Flight Plan

```python
from shared.drone_integration import (
    create_spray_flight_plan,
    Coordinate,
)

boundary = [
    Coordinate(lat=24.7136, lng=46.6753),
    Coordinate(lat=24.7136, lng=46.6853),
    Coordinate(lat=24.7236, lng=46.6853),
    Coordinate(lat=24.7236, lng=46.6753),
]

result = create_spray_flight_plan(
    boundary=boundary,
    spray_rate_l_ha=10.0,
    swath_width_m=5.0,
    altitude_m=3.0,
    name="Field A Herbicide",
    name_ar="مهمة رش الحقل أ",
)

if result.success:
    print(f"Waypoints: {len(result.flight_path.waypoints)}")
    print(f"Distance: {result.total_distance_m:.0f} m")
    print(f"Volume: {result.total_spray_volume_l:.1f} L")

    # Export for autopilot
    mission_items = result.flight_path.to_mavlink_mission()
    kml = result.flight_path.to_kml()
```

### NDVI-Based Prescription Map

```python
from shared.drone_integration import create_ndvi_prescription

# NDVI values on a regular grid
ndvi_grid = [
    [0.72, 0.68, 0.45, 0.31],
    [0.69, 0.71, 0.42, 0.28],
    [0.65, 0.66, 0.48, 0.35],
]

prescription = create_ndvi_prescription(
    field_id="FIELD-003",
    tenant_id="tenant_001",
    ndvi_grid=ndvi_grid,
    base_rate_l_ha=15.0,
    product_name="Urea Solution",
)

# GeoJSON export for drone controller upload
geojson = prescription.to_geojson()
```

## Supported Drones

| Platform | Protocol | Notes |
|----------|----------|-------|
| DJI Agras T40/T30/T20P | DJI SDK | Agricultural sprayers |
| DJI Mavic 3 Multispectral | DJI SDK | NDVI mapping |
| DJI Phantom 4 RTK | DJI SDK | Precision mapping |
| DJI Matrice 300/350 RTK | DJI SDK | Heavy-lift platform |
| ArduPilot-based | MAVLink | Open-source autopilot |
| PX4-based | MAVLink | Open-source autopilot |
