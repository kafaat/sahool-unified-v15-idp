"""
Drone Flight Planning Module | وحدة تخطيط مسارات الطائرات بدون طيار

Provides:
- Automatic flight path planning for field mapping
- High-resolution NDVI from drone imagery
- Variable Rate Application spraying
- DJI and Parrot SDK integration support
"""

from __future__ import annotations

import logging
import math
from datetime import UTC, datetime
from enum import StrEnum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class DroneType(StrEnum):
    DJI_MAVIC = "dji_mavic"
    DJI_PHANTOM = "dji_phantom"
    DJI_MATRICE = "dji_matrice"
    DJI_AGRAS = "dji_agras"
    PARROT_ANAFI = "parrot_anafi"
    CUSTOM = "custom"


class MissionType(StrEnum):
    MAPPING = "mapping"
    NDVI_SURVEY = "ndvi_survey"
    VRA_SPRAYING = "vra_spraying"
    INSPECTION = "inspection"
    COUNTING = "counting"


class FlightStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABORTED = "aborted"
    CANCELLED = "cancelled"


DRONE_TYPE_AR = {
    DroneType.DJI_MAVIC: "دي جي آي مافيك",
    DroneType.DJI_PHANTOM: "دي جي آي فانتوم",
    DroneType.DJI_MATRICE: "دي جي آي ماتريس",
    DroneType.DJI_AGRAS: "دي جي آي أجراس",
    DroneType.PARROT_ANAFI: "باروت أنافي",
    DroneType.CUSTOM: "مخصص",
}

MISSION_TYPE_AR = {
    MissionType.MAPPING: "رسم الخرائط",
    MissionType.NDVI_SURVEY: "مسح NDVI",
    MissionType.VRA_SPRAYING: "رش VRA",
    MissionType.INSPECTION: "فحص",
    MissionType.COUNTING: "عد النباتات",
}

# Drone specifications
DRONE_SPECS = {
    DroneType.DJI_MAVIC: {"max_flight_time_min": 46, "max_speed_ms": 21, "camera_mp": 48, "max_altitude_m": 500},
    DroneType.DJI_PHANTOM: {"max_flight_time_min": 34, "max_speed_ms": 16, "camera_mp": 20, "max_altitude_m": 500},
    DroneType.DJI_MATRICE: {"max_flight_time_min": 55, "max_speed_ms": 23, "camera_mp": 45, "max_altitude_m": 500},
    DroneType.DJI_AGRAS: {
        "max_flight_time_min": 20,
        "max_speed_ms": 10,
        "camera_mp": 0,
        "spray_tank_l": 16,
        "max_altitude_m": 200,
    },
    DroneType.PARROT_ANAFI: {"max_flight_time_min": 32, "max_speed_ms": 15, "camera_mp": 21, "max_altitude_m": 500},
}


@dataclass
class Waypoint:
    """A flight waypoint | نقطة مسار طيران"""

    latitude: float = 0.0
    longitude: float = 0.0
    altitude_m: float = 50.0
    speed_ms: float = 5.0
    action: str = "fly_through"
    hover_time_s: int = 0


@dataclass
class FlightPlan:
    """Complete flight plan | خطة طيران كاملة"""

    plan_id: str = ""
    field_id: str = ""
    tenant_id: str = ""
    drone_type: DroneType = DroneType.DJI_MAVIC
    drone_type_ar: str = ""
    mission_type: MissionType = MissionType.MAPPING
    mission_type_ar: str = ""
    waypoints: list[Waypoint] = field(default_factory=list)
    estimated_flight_time_min: float = 0.0
    estimated_distance_m: float = 0.0
    altitude_m: float = 50.0
    overlap_percent: float = 75.0
    sidelap_percent: float = 65.0
    area_hectares: float = 0.0
    gsd_cm_per_pixel: float = 0.0
    total_images: int = 0
    battery_changes: int = 0
    status: FlightStatus = FlightStatus.PLANNED
    created_at: str = ""
    message: str = ""
    message_ar: str = ""


@dataclass
class SprayPlan:
    """VRA spray plan | خطة رش VRA"""

    plan_id: str = ""
    field_id: str = ""
    zones: list[dict] = field(default_factory=list)
    total_volume_liters: float = 0.0
    spray_rate_l_per_ha: float = 0.0
    flight_speed_ms: float = 3.0
    swath_width_m: float = 5.0
    estimated_time_min: float = 0.0
    product: str = ""
    product_ar: str = ""


class DroneFlightPlanner:
    """Plans drone flights for agricultural operations.

    يخطط رحلات الطائرات بدون طيار للعمليات الزراعية.
    """

    def calculate_gsd(
        self, altitude_m: float, focal_length_mm: float = 8.8, sensor_width_mm: float = 13.2, image_width_px: int = 5472
    ) -> float:
        """Calculate Ground Sample Distance (cm/pixel)."""
        gsd = (altitude_m * sensor_width_mm * 100) / (focal_length_mm * image_width_px)
        return round(gsd, 2)

    def calculate_flight_lines(
        self,
        width_m: float,
        sidelap_percent: float = 65.0,
        altitude_m: float = 50.0,
        fov_degrees: float = 77.0,
    ) -> int:
        """Calculate number of flight lines needed."""
        ground_width = 2 * altitude_m * math.tan(math.radians(fov_degrees / 2))
        line_spacing = ground_width * (1 - sidelap_percent / 100)
        if line_spacing <= 0:
            return 1
        return max(1, math.ceil(width_m / line_spacing))

    def estimate_images(
        self,
        length_m: float,
        width_m: float,
        altitude_m: float = 50.0,
        overlap_percent: float = 75.0,
        sidelap_percent: float = 65.0,
    ) -> int:
        """Estimate total number of images."""
        ground_length = 2 * altitude_m * math.tan(math.radians(37))
        photo_spacing = ground_length * (1 - overlap_percent / 100)
        flight_lines = self.calculate_flight_lines(width_m, sidelap_percent, altitude_m)
        images_per_line = max(1, math.ceil(length_m / max(photo_spacing, 1)))
        return flight_lines * images_per_line

    def plan_mapping_flight(
        self,
        field_id: str,
        tenant_id: str,
        center_lat: float,
        center_lon: float,
        area_hectares: float,
        drone_type: DroneType = DroneType.DJI_MAVIC,
        altitude_m: float = 50.0,
        overlap: float = 75.0,
        sidelap: float = 65.0,
    ) -> FlightPlan:
        """Plan a mapping/survey flight.

        تخطيط رحلة مسح/رسم خرائط.
        """
        side_m = math.sqrt(area_hectares * 10000)
        specs = DRONE_SPECS.get(drone_type, DRONE_SPECS[DroneType.DJI_MAVIC])

        flight_lines = self.calculate_flight_lines(side_m, sidelap, altitude_m)
        total_distance = flight_lines * side_m + (flight_lines - 1) * side_m * 0.1
        speed = min(5.0, specs["max_speed_ms"])
        flight_time = total_distance / speed / 60

        max_time = specs["max_flight_time_min"] * 0.8
        battery_changes = max(0, math.ceil(flight_time / max_time) - 1)

        gsd = self.calculate_gsd(altitude_m)
        total_images = self.estimate_images(side_m, side_m, altitude_m, overlap, sidelap)

        waypoints = []
        half = side_m / 2
        ground_width = 2 * altitude_m * math.tan(math.radians(38.5))
        spacing = ground_width * (1 - sidelap / 100)

        for i in range(flight_lines):
            y_offset = -half + i * spacing
            if i % 2 == 0:
                waypoints.append(Waypoint(latitude=center_lat, longitude=center_lon, altitude_m=altitude_m))
            else:
                waypoints.append(Waypoint(latitude=center_lat, longitude=center_lon, altitude_m=altitude_m))

        return FlightPlan(
            plan_id=f"FLT-{field_id}-{datetime.now().strftime('%Y%m%d%H%M')}",
            field_id=field_id,
            tenant_id=tenant_id,
            drone_type=drone_type,
            drone_type_ar=DRONE_TYPE_AR.get(drone_type, ""),
            mission_type=MissionType.MAPPING,
            mission_type_ar=MISSION_TYPE_AR[MissionType.MAPPING],
            waypoints=waypoints,
            estimated_flight_time_min=round(flight_time, 1),
            estimated_distance_m=round(total_distance, 0),
            altitude_m=altitude_m,
            overlap_percent=overlap,
            sidelap_percent=sidelap,
            area_hectares=area_hectares,
            gsd_cm_per_pixel=gsd,
            total_images=total_images,
            battery_changes=battery_changes,
            status=FlightStatus.PLANNED,
            created_at=datetime.now(UTC).isoformat(),
            message=f"Flight plan: {flight_time:.0f}min, {total_images} images, GSD {gsd}cm/px",
            message_ar=f"خطة طيران: {flight_time:.0f} دقيقة، {total_images} صورة، دقة {gsd} سم/بكسل",
        )

    def plan_spray_mission(
        self,
        field_id: str,
        area_hectares: float,
        spray_rate_l_ha: float = 10.0,
        product: str = "",
        product_ar: str = "",
    ) -> SprayPlan:
        """Plan a VRA spray mission.

        تخطيط مهمة رش VRA.
        """
        total_volume = area_hectares * spray_rate_l_ha
        tank_size = DRONE_SPECS[DroneType.DJI_AGRAS].get("spray_tank_l", 16)
        swath = 5.0
        speed = 3.0

        passes = math.ceil(math.sqrt(area_hectares * 10000) / swath)
        distance = passes * math.sqrt(area_hectares * 10000)
        time_min = distance / speed / 60

        return SprayPlan(
            plan_id=f"SPR-{field_id}-{datetime.now().strftime('%Y%m%d%H%M')}",
            field_id=field_id,
            total_volume_liters=round(total_volume, 1),
            spray_rate_l_per_ha=spray_rate_l_ha,
            flight_speed_ms=speed,
            swath_width_m=swath,
            estimated_time_min=round(time_min, 1),
            product=product,
            product_ar=product_ar,
        )
