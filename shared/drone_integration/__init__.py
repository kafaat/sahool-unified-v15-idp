"""
SAHOOL Drone Integration Module - وحدة تكامل الطائرات بدون طيار

Comprehensive drone integration for agricultural operations including:
- Flight planning and waypoint generation | تخطيط الرحلات وإنشاء نقاط المسار
- Variable rate application (VRA) maps | خرائط التطبيق بالمعدل المتغير
- Spraying mission management | إدارة مهام الرش
- Aerial imagery processing | معالجة الصور الجوية
- Flight log management | إدارة سجلات الطيران

Supports DJI and open-source drone protocols (ArduPilot/PX4).

## Features | الميزات

### Flight Planning | تخطيط الرحلات
- Parallel (boustrophedon) patterns | أنماط متوازية
- Crosshatch patterns | أنماط متقاطعة
- Perimeter flights | رحلات المحيط
- Mapping missions with overlap calculation | مهام التصوير مع حساب التداخل

### Variable Rate Application | التطبيق بالمعدل المتغير
- NDVI-based prescription maps | خرائط وصفة مبنية على NDVI
- Weed/pest spot spray maps | خرائط الرش النقطي للأعشاب/الآفات
- Fertilizer prescription maps | خرائط وصفة التسميد
- Multiple classification methods | طرق تصنيف متعددة

### Mission Management | إدارة المهام
- Spray mission planning | تخطيط مهام الرش
- Mapping mission planning | تخطيط مهام التصوير
- Weather assessment | تقييم الطقس
- Resource estimation | تقدير الموارد

### Flight Logs | سجلات الطيران
- Telemetry recording | تسجيل القياس عن بعد
- Track export (GeoJSON, KML) | تصدير المسار
- Mission analytics | تحليلات المهام

## Quick Start | البداية السريعة

```python
from shared.drone_integration import (
    FlightPlanner,
    FlightPlanConfig,
    FlightMode,
    Coordinate,
    create_spray_flight_plan,
    create_ndvi_prescription,
)

# Create a spray mission flight plan
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
    name="Field A Spray Mission",
    name_ar="مهمة رش الحقل أ",
)

if result.success:
    print(f"Total distance: {result.total_distance_m:.0f}m")
    print(f"Spray volume: {result.total_spray_volume_l:.1f}L")

    # Export to MAVLink mission file
    mission_items = result.flight_path.to_mavlink_mission()

    # Export to KML
    kml = result.flight_path.to_kml()
```

## Supported Drones | الطائرات المدعومة

### DJI Agricultural Drones | طائرات DJI الزراعية
- DJI Agras T40, T30, T20P
- DJI Mavic 3 Multispectral
- DJI Phantom 4 RTK
- DJI Matrice 300/350 RTK

### Open Source Platforms | المنصات مفتوحة المصدر
- ArduPilot-based drones (MAVLink)
- PX4-based drones (MAVLink)
- Custom platforms

## Version: 1.0.0
## Author: SAHOOL Team
"""

# =============================================================================
# Models - النماذج
# =============================================================================
from .models import (
    # Enumerations
    DroneType,
    FlightMode,
    FlightStatus,
    MissionStatus,
    WaypointAction,
    FlightPattern,
    ApplicationMode,
    SprayStatus,
    ImageryType,
    WeatherCondition,
    VRAZoneType,
    # Base Classes
    Coordinate,
    BoundingBox,
    # Drone Models
    DroneSpecs,
    Drone,
    # Waypoint and Flight Path
    Waypoint,
    FlightPath,
    # Mission Models
    WeatherCheck,
    SprayMission,
    MappingMission,
    # Flight Logs
    FlightTelemetry,
    FlightLog,
    # VRA Models
    VRAZone,
    PrescriptionMap,
    # Imagery Models
    AerialImage,
    ProcessedImagery,
    # Utilities
    generate_id,
)

# =============================================================================
# Flight Planner - مخطط الرحلات
# =============================================================================
from .flight_planner import (
    # Configuration
    FlightPlanConfig,
    FlightPlanResult,
    # Main Planner Class
    FlightPlanner,
    # Weather Assessment
    assess_flight_weather,
    # Convenience Functions
    create_spray_flight_plan,
    create_mapping_flight_plan,
    estimate_flight_resources,
    # Geometry Utilities
    haversine_distance,
    bearing_between,
    destination_point,
    calculate_polygon_area,
    polygon_centroid,
    get_bounding_box,
    point_in_polygon,
    buffer_polygon_inward,
    calculate_optimal_heading,
)

# =============================================================================
# Variable Rate Application - التطبيق بالمعدل المتغير
# =============================================================================
from .vra import (
    # Configuration
    ClassificationMethod,
    VRASourceType,
    RateAdjustmentMode,
    VRAConfig,
    GridCell,
    VRARasterData,
    # Main Generator Class
    VRAGenerator,
    # Convenience Functions
    create_ndvi_prescription,
    create_spot_spray_map,
    export_prescription_to_shapefile,
)


# =============================================================================
# Module Exports - تصديرات الوحدة
# =============================================================================
__all__ = [
    # =========================================================================
    # Models - النماذج
    # =========================================================================
    # Enumerations
    "DroneType",
    "FlightMode",
    "FlightStatus",
    "MissionStatus",
    "WaypointAction",
    "FlightPattern",
    "ApplicationMode",
    "SprayStatus",
    "ImageryType",
    "WeatherCondition",
    "VRAZoneType",
    # Base Classes
    "Coordinate",
    "BoundingBox",
    # Drone Models
    "DroneSpecs",
    "Drone",
    # Waypoint and Flight Path
    "Waypoint",
    "FlightPath",
    # Mission Models
    "WeatherCheck",
    "SprayMission",
    "MappingMission",
    # Flight Logs
    "FlightTelemetry",
    "FlightLog",
    # VRA Models
    "VRAZone",
    "PrescriptionMap",
    # Imagery Models
    "AerialImage",
    "ProcessedImagery",
    # Utilities
    "generate_id",

    # =========================================================================
    # Flight Planner - مخطط الرحلات
    # =========================================================================
    # Configuration
    "FlightPlanConfig",
    "FlightPlanResult",
    # Main Class
    "FlightPlanner",
    # Weather
    "assess_flight_weather",
    # Convenience Functions
    "create_spray_flight_plan",
    "create_mapping_flight_plan",
    "estimate_flight_resources",
    # Geometry Utilities
    "haversine_distance",
    "bearing_between",
    "destination_point",
    "calculate_polygon_area",
    "polygon_centroid",
    "get_bounding_box",
    "point_in_polygon",
    "buffer_polygon_inward",
    "calculate_optimal_heading",

    # =========================================================================
    # VRA - التطبيق بالمعدل المتغير
    # =========================================================================
    # Configuration
    "ClassificationMethod",
    "VRASourceType",
    "RateAdjustmentMode",
    "VRAConfig",
    "GridCell",
    "VRARasterData",
    # Main Class
    "VRAGenerator",
    # Convenience Functions
    "create_ndvi_prescription",
    "create_spot_spray_map",
    "export_prescription_to_shapefile",
]

__version__ = "1.0.0"
__author__ = "SAHOOL Team"
