"""
SAHOOL Drone Flight Planner - مخطط رحلات الطائرات بدون طيار

Flight path generation for agricultural fields with support for:
- Parallel (boustrophedon) patterns - الأنماط المتوازية
- Crosshatch patterns - أنماط التقاطع
- Contour following for slopes - تتبع خطوط الكنتور
- Perimeter flights - رحلات المحيط
- Obstacle avoidance - تجنب العوائق

Supports DJI and MAVLink (ArduPilot/PX4) protocols.

Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .models import (
    BoundingBox,
    Coordinate,
    DroneSpecs,
    FlightMode,
    FlightPath,
    FlightPattern,
    Waypoint,
    WaypointAction,
    WeatherCheck,
    WeatherCondition,
    generate_id,
)

# ==============================================================================
# Constants - الثوابت
# ==============================================================================

# Earth radius in meters
EARTH_RADIUS_M = 6371000

# Default flight parameters
DEFAULT_CRUISE_ALTITUDE_M = 3.0  # For spraying | للرش
DEFAULT_MAPPING_ALTITUDE_M = 50.0  # For mapping | للتصوير
DEFAULT_CRUISE_SPEED_MS = 5.0  # 5 m/s = 18 km/h
DEFAULT_SWATH_WIDTH_M = 5.0  # Spray swath | عرض الرش
DEFAULT_OVERLAP_PERCENT = 10.0  # Overlap for spraying
DEFAULT_PHOTO_OVERLAP_PERCENT = 80.0  # Frontal overlap for mapping
DEFAULT_PHOTO_SIDELAP_PERCENT = 70.0  # Side overlap for mapping

# Safety limits
MAX_FLIGHT_ALTITUDE_M = 120.0  # Regulatory limit in most countries
MIN_FLIGHT_ALTITUDE_M = 2.0
MAX_WIND_SPEED_MS = 8.0  # 8 m/s = 29 km/h
MIN_VISIBILITY_KM = 3.0


# ==============================================================================
# Flight Planner Configuration - تكوين مخطط الرحلات
# ==============================================================================


@dataclass
class FlightPlanConfig:
    """Configuration for flight path generation - تكوين إنشاء مسار الطيران"""

    # Flight mode - وضع الطيران
    mode: FlightMode = FlightMode.SPRAYING

    # Altitude and speed - الارتفاع والسرعة
    cruise_altitude_m: float = DEFAULT_CRUISE_ALTITUDE_M
    cruise_speed_ms: float = DEFAULT_CRUISE_SPEED_MS
    safe_altitude_m: float = 30.0  # RTH altitude | ارتفاع العودة للمنزل

    # Swath and overlap - العرض والتداخل
    swath_width_m: float = DEFAULT_SWATH_WIDTH_M
    overlap_percent: float = DEFAULT_OVERLAP_PERCENT
    side_overlap_percent: float = DEFAULT_PHOTO_SIDELAP_PERCENT  # For mapping

    # Pattern - النمط
    pattern: FlightPattern = FlightPattern.PARALLEL
    heading_deg: float | None = None  # Auto-calculate if None
    optimize_for_wind: bool = True  # Align with wind direction

    # Turn parameters - معاملات الانعطاف
    turn_radius_m: float = 3.0  # Minimum turn radius
    approach_distance_m: float = 5.0  # Distance before first pass

    # Boundaries and exclusions - الحدود والاستثناءات
    buffer_distance_m: float = 0.0  # Inward buffer from boundary
    exclusion_zones: list[list[Coordinate]] = field(default_factory=list)

    # Safety - السلامة
    max_distance_from_home_m: float = 2000.0  # Maximum range
    return_to_home: bool = True

    # Battery - البطارية
    reserve_battery_percent: float = 20.0  # Reserve for RTH

    # Spray parameters (for spraying mode) - معاملات الرش
    spray_rate_l_ha: float = 10.0


@dataclass
class FlightPlanResult:
    """Result of flight path generation - نتيجة إنشاء مسار الطيران"""

    success: bool
    flight_path: FlightPath | None = None

    # Statistics - الإحصائيات
    total_waypoints: int = 0
    total_distance_m: float = 0
    estimated_duration_min: float = 0
    coverage_area_ha: float = 0
    effective_area_ha: float = 0

    # Spray estimates (for spraying mode) - تقديرات الرش
    total_spray_volume_l: float = 0
    spray_passes: int = 0

    # Photo estimates (for mapping mode) - تقديرات التصوير
    estimated_photos: int = 0
    gsd_cm_px: float = 0

    # Battery estimate - تقدير البطارية
    estimated_battery_percent: float = 0
    flights_needed: int = 1  # Number of flights needed

    # Warnings and errors - التحذيرات والأخطاء
    warnings_en: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)
    error_en: str = ""
    error_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "total_waypoints": self.total_waypoints,
            "total_distance_m": self.total_distance_m,
            "estimated_duration_min": self.estimated_duration_min,
            "coverage_area_ha": self.coverage_area_ha,
            "effective_area_ha": self.effective_area_ha,
            "total_spray_volume_l": self.total_spray_volume_l,
            "estimated_photos": self.estimated_photos,
            "estimated_battery_percent": self.estimated_battery_percent,
            "flights_needed": self.flights_needed,
            "warnings_en": self.warnings_en,
            "warnings_ar": self.warnings_ar,
            "error_en": self.error_en,
            "error_ar": self.error_ar,
        }


# ==============================================================================
# Geometry Utilities - أدوات الهندسة
# ==============================================================================


def haversine_distance(coord1: Coordinate, coord2: Coordinate) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    حساب المسافة بين إحداثيين باستخدام صيغة هافرساين.

    Args:
        coord1: First coordinate | الإحداثي الأول
        coord2: Second coordinate | الإحداثي الثاني

    Returns:
        Distance in meters | المسافة بالمتر
    """
    lat1, lng1 = math.radians(coord1.lat), math.radians(coord1.lng)
    lat2, lng2 = math.radians(coord2.lat), math.radians(coord2.lng)

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS_M * c


def bearing_between(coord1: Coordinate, coord2: Coordinate) -> float:
    """
    Calculate bearing from coord1 to coord2.
    حساب الاتجاه من الإحداثي الأول إلى الثاني.

    Args:
        coord1: Start coordinate | إحداثي البداية
        coord2: End coordinate | إحداثي النهاية

    Returns:
        Bearing in degrees (0-360) | الاتجاه بالدرجات
    """
    lat1 = math.radians(coord1.lat)
    lat2 = math.radians(coord2.lat)
    dlng = math.radians(coord2.lng - coord1.lng)

    x = math.sin(dlng) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlng)

    bearing = math.atan2(x, y)
    return (math.degrees(bearing) + 360) % 360


def destination_point(start: Coordinate, bearing_deg: float, distance_m: float) -> Coordinate:
    """
    Calculate destination point given start, bearing, and distance.
    حساب نقطة الوجهة من البداية والاتجاه والمسافة.

    Args:
        start: Starting coordinate | إحداثي البداية
        bearing_deg: Bearing in degrees | الاتجاه بالدرجات
        distance_m: Distance in meters | المسافة بالمتر

    Returns:
        Destination coordinate | إحداثي الوجهة
    """
    lat1 = math.radians(start.lat)
    lng1 = math.radians(start.lng)
    bearing = math.radians(bearing_deg)

    d = distance_m / EARTH_RADIUS_M

    lat2 = math.asin(
        math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(bearing)
    )
    lng2 = lng1 + math.atan2(
        math.sin(bearing) * math.sin(d) * math.cos(lat1),
        math.cos(d) - math.sin(lat1) * math.sin(lat2),
    )

    return Coordinate(lat=math.degrees(lat2), lng=math.degrees(lng2), alt_agl_m=start.alt_agl_m)


def calculate_polygon_area(boundary: list[Coordinate]) -> float:
    """
    Calculate area of polygon using Shoelace formula with geodetic correction.
    حساب مساحة المضلع باستخدام صيغة الرباط مع تصحيح جيوديسي.

    Args:
        boundary: List of polygon vertices | قائمة رؤوس المضلع

    Returns:
        Area in square meters | المساحة بالمتر المربع
    """
    if len(boundary) < 3:
        return 0.0

    # Convert to local Cartesian coordinates
    center_lat = sum(c.lat for c in boundary) / len(boundary)
    center_lng = sum(c.lng for c in boundary) / len(boundary)

    # Meters per degree at this latitude
    m_per_deg_lat = 111320  # Approximately constant
    m_per_deg_lng = 111320 * math.cos(math.radians(center_lat))

    # Convert to meters
    points_m = [
        ((c.lng - center_lng) * m_per_deg_lng, (c.lat - center_lat) * m_per_deg_lat)
        for c in boundary
    ]

    # Shoelace formula
    n = len(points_m)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points_m[i][0] * points_m[j][1]
        area -= points_m[j][0] * points_m[i][1]

    return abs(area) / 2.0


def polygon_centroid(boundary: list[Coordinate]) -> Coordinate:
    """
    Calculate centroid of polygon.
    حساب مركز ثقل المضلع.

    Args:
        boundary: List of polygon vertices | قائمة رؤوس المضلع

    Returns:
        Centroid coordinate | إحداثي مركز الثقل
    """
    n = len(boundary)
    if n == 0:
        return Coordinate(lat=0, lng=0)

    centroid_lat = sum(c.lat for c in boundary) / n
    centroid_lng = sum(c.lng for c in boundary) / n

    return Coordinate(lat=centroid_lat, lng=centroid_lng)


def get_bounding_box(boundary: list[Coordinate]) -> BoundingBox:
    """
    Get bounding box of polygon.
    الحصول على مربع الحدود للمضلع.

    Args:
        boundary: List of polygon vertices | قائمة رؤوس المضلع

    Returns:
        Bounding box | مربع الحدود
    """
    lats = [c.lat for c in boundary]
    lngs = [c.lng for c in boundary]

    return BoundingBox(min_lat=min(lats), max_lat=max(lats), min_lng=min(lngs), max_lng=max(lngs))


def point_in_polygon(point: Coordinate, boundary: list[Coordinate]) -> bool:
    """
    Check if point is inside polygon using ray casting.
    التحقق مما إذا كانت النقطة داخل المضلع.

    Args:
        point: Point to check | النقطة للتحقق
        boundary: Polygon boundary | حدود المضلع

    Returns:
        True if inside | صحيح إذا كانت داخل
    """
    n = len(boundary)
    inside = False

    j = n - 1
    for i in range(n):
        if ((boundary[i].lat > point.lat) != (boundary[j].lat > point.lat)) and (
            point.lng
            < (boundary[j].lng - boundary[i].lng)
            * (point.lat - boundary[i].lat)
            / (boundary[j].lat - boundary[i].lat)
            + boundary[i].lng
        ):
            inside = not inside
        j = i

    return inside


def buffer_polygon_inward(boundary: list[Coordinate], buffer_m: float) -> list[Coordinate]:
    """
    Buffer polygon inward by specified distance.
    تقليص المضلع للداخل بمسافة محددة.

    Args:
        boundary: Polygon boundary | حدود المضلع
        buffer_m: Buffer distance in meters | مسافة الحماية بالمتر

    Returns:
        Buffered polygon boundary | حدود المضلع المقلص
    """
    if buffer_m <= 0:
        return boundary

    centroid = polygon_centroid(boundary)
    buffered = []

    for coord in boundary:
        # Move point toward centroid
        bearing = bearing_between(coord, centroid)
        new_coord = destination_point(coord, bearing, buffer_m)
        buffered.append(new_coord)

    return buffered


def calculate_optimal_heading(boundary: list[Coordinate]) -> float:
    """
    Calculate optimal flight heading based on field geometry.
    حساب الاتجاه الأمثل للطيران بناءً على هندسة الحقل.

    Uses longest edge of bounding box or longest edge of polygon.

    Args:
        boundary: Field boundary | حدود الحقل

    Returns:
        Optimal heading in degrees | الاتجاه الأمثل بالدرجات
    """
    if len(boundary) < 2:
        return 0.0

    # Find longest edge
    max_length = 0
    best_heading = 0

    for i in range(len(boundary)):
        j = (i + 1) % len(boundary)
        length = haversine_distance(boundary[i], boundary[j])
        if length > max_length:
            max_length = length
            best_heading = bearing_between(boundary[i], boundary[j])

    return best_heading


# ==============================================================================
# Flight Path Generator - مولد مسار الطيران
# ==============================================================================


class FlightPlanner:
    """
    Flight path planner for agricultural drones.
    مخطط مسار الطيران للطائرات الزراعية.

    Generates optimized flight paths for:
    - Spraying missions | مهام الرش
    - Mapping missions | مهام التصوير
    - Scouting missions | مهام الاستكشاف
    """

    def __init__(self, config: FlightPlanConfig | None = None):
        """
        Initialize flight planner.

        Args:
            config: Flight plan configuration | تكوين خطة الطيران
        """
        self.config = config or FlightPlanConfig()

    def generate_parallel_path(
        self,
        boundary: list[Coordinate],
        name: str = "Flight Path",
        name_ar: str = "مسار الطيران",
        home_location: Coordinate | None = None,
    ) -> FlightPlanResult:
        """
        Generate parallel (boustrophedon) flight path.
        إنشاء مسار طيران متوازي (متعرج).

        Args:
            boundary: Field boundary polygon | مضلع حدود الحقل
            name: Path name in English | اسم المسار بالإنجليزية
            name_ar: Path name in Arabic | اسم المسار بالعربية
            home_location: Home/takeoff location | موقع المنزل/الإقلاع

        Returns:
            FlightPlanResult with generated path | نتيجة خطة الطيران
        """
        result = FlightPlanResult(success=False)

        # Validate boundary
        if len(boundary) < 3:
            result.error_en = "Field boundary must have at least 3 points"
            result.error_ar = "يجب أن تحتوي حدود الحقل على 3 نقاط على الأقل"
            return result

        # Apply buffer if specified
        working_boundary = buffer_polygon_inward(boundary, self.config.buffer_distance_m)

        # Calculate field properties
        area_m2 = calculate_polygon_area(working_boundary)
        area_ha = area_m2 / 10000
        result.coverage_area_ha = area_ha

        bbox = get_bounding_box(working_boundary)
        centroid = polygon_centroid(working_boundary)

        # Determine flight heading
        if self.config.heading_deg is not None:
            heading = self.config.heading_deg
        else:
            heading = calculate_optimal_heading(working_boundary)

        # Calculate swath spacing
        overlap_factor = 1 - (self.config.overlap_percent / 100)
        swath_spacing_m = self.config.swath_width_m * overlap_factor

        # Calculate perpendicular direction
        perp_heading = (heading + 90) % 360

        # Generate flight lines
        waypoints = []
        wp_index = 0

        # Calculate field dimensions along and perpendicular to heading
        # Use bounding box diagonal as reference
        bbox_width = haversine_distance(
            Coordinate(lat=bbox.min_lat, lng=bbox.min_lng),
            Coordinate(lat=bbox.min_lat, lng=bbox.max_lng),
        )
        bbox_height = haversine_distance(
            Coordinate(lat=bbox.min_lat, lng=bbox.min_lng),
            Coordinate(lat=bbox.max_lat, lng=bbox.min_lng),
        )
        field_extent = math.sqrt(bbox_width**2 + bbox_height**2)

        # Number of passes needed
        num_passes = int(math.ceil(field_extent / swath_spacing_m)) + 2
        result.spray_passes = num_passes

        # Home location
        if home_location is None:
            home_location = centroid

        # Generate passes
        total_distance = 0
        effective_area = 0

        # Start from edge of field
        start_offset = -(num_passes // 2) * swath_spacing_m

        for pass_idx in range(num_passes):
            # Calculate offset from centerline
            offset = start_offset + pass_idx * swath_spacing_m

            # Calculate pass start point
            pass_center = destination_point(centroid, perp_heading, offset)

            # Calculate line endpoints
            half_extent = field_extent / 2 + self.config.approach_distance_m
            line_start = destination_point(pass_center, heading + 180, half_extent)
            line_end = destination_point(pass_center, heading, half_extent)

            # Alternate direction for each pass (boustrophedon)
            if pass_idx % 2 == 1:
                line_start, line_end = line_end, line_start

            # Set altitude
            line_start.alt_agl_m = self.config.cruise_altitude_m
            line_end.alt_agl_m = self.config.cruise_altitude_m

            # Clip line to polygon and get segments inside field
            inside_segments = self._clip_line_to_polygon(line_start, line_end, working_boundary)

            for seg_start, seg_end in inside_segments:
                # Start waypoint
                wp_start = Waypoint(
                    index=wp_index,
                    coordinate=seg_start,
                    speed_ms=self.config.cruise_speed_ms,
                    heading_deg=heading if pass_idx % 2 == 0 else (heading + 180) % 360,
                    spray_on=True if self.config.mode == FlightMode.SPRAYING else False,
                    spray_rate_l_ha=self.config.spray_rate_l_ha,
                    actions=[WaypointAction.START_SPRAY]
                    if self.config.mode == FlightMode.SPRAYING
                    else [],
                    is_turn_point=wp_index > 0,
                )
                waypoints.append(wp_start)
                wp_index += 1

                # End waypoint
                wp_end = Waypoint(
                    index=wp_index,
                    coordinate=seg_end,
                    speed_ms=self.config.cruise_speed_ms,
                    heading_deg=heading if pass_idx % 2 == 0 else (heading + 180) % 360,
                    spray_on=False,
                    actions=[WaypointAction.STOP_SPRAY]
                    if self.config.mode == FlightMode.SPRAYING
                    else [],
                    is_turn_point=True,
                )
                waypoints.append(wp_end)
                wp_index += 1

                # Calculate segment distance and area
                seg_distance = haversine_distance(seg_start, seg_end)
                total_distance += seg_distance
                effective_area += seg_distance * self.config.swath_width_m

        # Convert effective area to hectares
        result.effective_area_ha = effective_area / 10000

        if len(waypoints) == 0:
            result.error_en = "No valid flight path could be generated"
            result.error_ar = "لا يمكن إنشاء مسار طيران صالح"
            return result

        # Add turn distances between passes (only between end of one segment and start of next)
        # Waypoints are added in pairs (start, end) per segment, so turns occur at odd indices
        for i in range(1, len(waypoints)):
            if i % 2 == 0:  # Turn from end of previous segment to start of next segment
                total_distance += haversine_distance(
                    waypoints[i - 1].coordinate, waypoints[i].coordinate
                )

        # Calculate timing
        flight_time_s = total_distance / self.config.cruise_speed_ms
        result.estimated_duration_min = flight_time_s / 60
        result.total_distance_m = total_distance
        result.total_waypoints = len(waypoints)

        # Spray volume estimate
        if self.config.mode == FlightMode.SPRAYING:
            result.total_spray_volume_l = result.effective_area_ha * self.config.spray_rate_l_ha

        # Create flight path
        flight_path = FlightPath(
            id=generate_id("fp"),
            name=name,
            name_ar=name_ar,
            waypoints=waypoints,
            pattern=FlightPattern.PARALLEL,
            total_distance_m=total_distance,
            estimated_duration_min=result.estimated_duration_min,
            cruise_altitude_m=self.config.cruise_altitude_m,
            cruise_speed_ms=self.config.cruise_speed_ms,
            swath_width_m=self.config.swath_width_m,
            overlap_percent=self.config.overlap_percent,
            coverage_area_ha=area_ha,
            effective_area_ha=result.effective_area_ha,
            home_location=home_location,
            safe_altitude_m=self.config.safe_altitude_m,
        )

        result.success = True
        result.flight_path = flight_path

        # Add warnings if needed
        if result.estimated_duration_min > 20:
            result.warnings_en.append(
                f"Flight time ({result.estimated_duration_min:.1f} min) may require multiple batteries"
            )
            result.warnings_ar.append(
                f"وقت الطيران ({result.estimated_duration_min:.1f} دقيقة) قد يتطلب بطاريات متعددة"
            )
            result.flights_needed = int(math.ceil(result.estimated_duration_min / 20))

        return result

    def generate_mapping_path(
        self,
        boundary: list[Coordinate],
        gsd_cm_px: float = 2.0,
        camera_sensor_width_mm: float = 13.2,
        camera_focal_length_mm: float = 8.8,
        image_width_px: int = 5472,
        image_height_px: int = 3648,
        name: str = "Mapping Mission",
        name_ar: str = "مهمة التصوير",
        home_location: Coordinate | None = None,
    ) -> FlightPlanResult:
        """
        Generate mapping flight path with photo overlap calculation.
        إنشاء مسار طيران للتصوير مع حساب التداخل.

        Args:
            boundary: Field boundary polygon | مضلع حدود الحقل
            gsd_cm_px: Target ground sample distance | دقة الأرض المستهدفة
            camera_sensor_width_mm: Camera sensor width | عرض مستشعر الكاميرا
            camera_focal_length_mm: Camera focal length | البعد البؤري للكاميرا
            image_width_px: Image width in pixels | عرض الصورة بالبكسل
            image_height_px: Image height in pixels | ارتفاع الصورة بالبكسل
            name: Mission name | اسم المهمة
            name_ar: Mission name in Arabic | اسم المهمة بالعربية
            home_location: Home/takeoff location | موقع المنزل

        Returns:
            FlightPlanResult with generated path | نتيجة خطة الطيران
        """
        result = FlightPlanResult(success=False)

        if len(boundary) < 3:
            result.error_en = "Field boundary must have at least 3 points"
            result.error_ar = "يجب أن تحتوي حدود الحقل على 3 نقاط على الأقل"
            return result

        # Calculate flight altitude from GSD
        # GSD = (sensor_width * altitude) / (focal_length * image_width)
        # altitude = (GSD * focal_length * image_width) / sensor_width
        altitude_m = (
            (gsd_cm_px / 100) * camera_focal_length_mm * image_width_px
        ) / camera_sensor_width_mm

        # Validate altitude
        if altitude_m > MAX_FLIGHT_ALTITUDE_M:
            result.error_en = (
                f"Required altitude ({altitude_m:.1f}m) exceeds maximum ({MAX_FLIGHT_ALTITUDE_M}m)"
            )
            result.error_ar = f"الارتفاع المطلوب ({altitude_m:.1f}م) يتجاوز الحد الأقصى ({MAX_FLIGHT_ALTITUDE_M}م)"
            return result

        if altitude_m < MIN_FLIGHT_ALTITUDE_M:
            altitude_m = MIN_FLIGHT_ALTITUDE_M

        # Calculate ground coverage per image
        ground_width_m = (camera_sensor_width_mm * altitude_m) / camera_focal_length_mm
        ground_height_m = (camera_sensor_width_mm * altitude_m * image_height_px) / (
            camera_focal_length_mm * image_width_px
        )

        # Calculate photo spacing based on overlap
        frontal_overlap = (
            self.config.overlap_percent / 100
            if self.config.overlap_percent > 50
            else DEFAULT_PHOTO_OVERLAP_PERCENT / 100
        )
        side_overlap = self.config.side_overlap_percent / 100

        photo_spacing_m = ground_height_m * (1 - frontal_overlap)

        # Update config for path generation
        mapping_config = FlightPlanConfig(
            mode=FlightMode.MAPPING,
            cruise_altitude_m=altitude_m,
            cruise_speed_ms=min(self.config.cruise_speed_ms, 8.0),  # Slower for mapping
            swath_width_m=ground_width_m,
            overlap_percent=side_overlap * 100,
            pattern=FlightPattern.PARALLEL,
            heading_deg=self.config.heading_deg,
            buffer_distance_m=0,  # No buffer for mapping
        )

        # Generate basic parallel path
        original_config = self.config
        self.config = mapping_config

        path_result = self.generate_parallel_path(
            boundary=boundary, name=name, name_ar=name_ar, home_location=home_location
        )

        self.config = original_config

        if not path_result.success:
            return path_result

        # Add photo points to waypoints
        flight_path = path_result.flight_path
        photo_waypoints = []
        wp_index = 0
        total_photos = 0

        for i in range(0, len(flight_path.waypoints), 2):
            if i + 1 >= len(flight_path.waypoints):
                break

            start_wp = flight_path.waypoints[i]
            end_wp = flight_path.waypoints[i + 1]

            # Calculate number of photos on this line
            line_distance = haversine_distance(start_wp.coordinate, end_wp.coordinate)
            num_photos = max(1, int(line_distance / photo_spacing_m))

            # Generate photo points
            heading = bearing_between(start_wp.coordinate, end_wp.coordinate)

            for j in range(num_photos + 1):
                progress = j / max(1, num_photos)
                photo_coord = Coordinate(
                    lat=start_wp.coordinate.lat
                    + progress * (end_wp.coordinate.lat - start_wp.coordinate.lat),
                    lng=start_wp.coordinate.lng
                    + progress * (end_wp.coordinate.lng - start_wp.coordinate.lng),
                    alt_agl_m=altitude_m,
                )

                photo_wp = Waypoint(
                    index=wp_index,
                    coordinate=photo_coord,
                    speed_ms=mapping_config.cruise_speed_ms,
                    heading_deg=heading,
                    gimbal_pitch_deg=-90,  # Nadir
                    actions=[WaypointAction.TAKE_PHOTO],
                    is_photo_point=True,
                )
                photo_waypoints.append(photo_wp)
                wp_index += 1
                total_photos += 1

        # Update flight path with photo waypoints
        flight_path.waypoints = photo_waypoints
        flight_path.cruise_altitude_m = altitude_m

        # Update result
        result = path_result
        result.estimated_photos = total_photos
        result.gsd_cm_px = gsd_cm_px
        result.flight_path = flight_path
        result.total_waypoints = len(photo_waypoints)

        return result

    def generate_crosshatch_path(
        self,
        boundary: list[Coordinate],
        name: str = "Crosshatch Path",
        name_ar: str = "مسار متقاطع",
        home_location: Coordinate | None = None,
    ) -> FlightPlanResult:
        """
        Generate crosshatch (perpendicular double coverage) flight path.
        إنشاء مسار طيران متقاطع (تغطية مزدوجة متعامدة).

        Args:
            boundary: Field boundary polygon | مضلع حدود الحقل
            name: Path name | اسم المسار
            name_ar: Path name in Arabic | اسم المسار بالعربية
            home_location: Home location | موقع المنزل

        Returns:
            FlightPlanResult with generated path | نتيجة خطة الطيران
        """
        # Generate first pass
        original_heading = self.config.heading_deg
        if original_heading is None:
            original_heading = calculate_optimal_heading(boundary)

        self.config.heading_deg = original_heading
        result1 = self.generate_parallel_path(
            boundary=boundary,
            name=f"{name} Pass 1",
            name_ar=f"{name_ar} - المرور 1",
            home_location=home_location,
        )

        if not result1.success:
            return result1

        # Generate second pass perpendicular
        self.config.heading_deg = (original_heading + 90) % 360
        result2 = self.generate_parallel_path(
            boundary=boundary,
            name=f"{name} Pass 2",
            name_ar=f"{name_ar} - المرور 2",
            home_location=home_location,
        )

        # Reset config
        self.config.heading_deg = original_heading

        if not result2.success:
            return result1  # Return first pass if second fails

        # Merge results
        combined_waypoints = result1.flight_path.waypoints + result2.flight_path.waypoints

        # Re-index waypoints
        for i, wp in enumerate(combined_waypoints):
            wp.index = i

        combined_path = FlightPath(
            id=generate_id("fp"),
            name=name,
            name_ar=name_ar,
            waypoints=combined_waypoints,
            pattern=FlightPattern.CROSSHATCH,
            total_distance_m=result1.total_distance_m + result2.total_distance_m,
            estimated_duration_min=result1.estimated_duration_min + result2.estimated_duration_min,
            cruise_altitude_m=self.config.cruise_altitude_m,
            cruise_speed_ms=self.config.cruise_speed_ms,
            swath_width_m=self.config.swath_width_m,
            overlap_percent=self.config.overlap_percent,
            coverage_area_ha=result1.coverage_area_ha,
            effective_area_ha=result1.effective_area_ha + result2.effective_area_ha,
            home_location=home_location,
            safe_altitude_m=self.config.safe_altitude_m,
        )

        final_result = FlightPlanResult(
            success=True,
            flight_path=combined_path,
            total_waypoints=len(combined_waypoints),
            total_distance_m=result1.total_distance_m + result2.total_distance_m,
            estimated_duration_min=result1.estimated_duration_min + result2.estimated_duration_min,
            coverage_area_ha=result1.coverage_area_ha,
            effective_area_ha=result1.effective_area_ha + result2.effective_area_ha,
            total_spray_volume_l=result1.total_spray_volume_l + result2.total_spray_volume_l,
            spray_passes=result1.spray_passes + result2.spray_passes,
        )

        final_result.warnings_en = result1.warnings_en + result2.warnings_en
        final_result.warnings_ar = result1.warnings_ar + result2.warnings_ar

        if final_result.estimated_duration_min > 20:
            final_result.flights_needed = int(math.ceil(final_result.estimated_duration_min / 20))

        return final_result

    def generate_perimeter_path(
        self,
        boundary: list[Coordinate],
        passes: int = 2,
        name: str = "Perimeter Path",
        name_ar: str = "مسار المحيط",
        home_location: Coordinate | None = None,
    ) -> FlightPlanResult:
        """
        Generate perimeter (boundary following) flight path.
        إنشاء مسار طيران لمحيط الحقل.

        Args:
            boundary: Field boundary polygon | مضلع حدود الحقل
            passes: Number of perimeter passes | عدد المرات حول المحيط
            name: Path name | اسم المسار
            name_ar: Path name in Arabic | اسم المسار بالعربية
            home_location: Home location | موقع المنزل

        Returns:
            FlightPlanResult with generated path | نتيجة خطة الطيران
        """
        result = FlightPlanResult(success=False)

        if len(boundary) < 3:
            result.error_en = "Field boundary must have at least 3 points"
            result.error_ar = "يجب أن تحتوي حدود الحقل على 3 نقاط على الأقل"
            return result

        waypoints = []
        wp_index = 0
        total_distance = 0

        overlap_factor = 1 - (self.config.overlap_percent / 100)
        pass_offset_m = self.config.swath_width_m * overlap_factor

        for pass_num in range(passes):
            # Buffer inward for each pass
            pass_boundary = buffer_polygon_inward(boundary, pass_offset_m * pass_num)

            if len(pass_boundary) < 3:
                break

            for i, coord in enumerate(pass_boundary):
                coord.alt_agl_m = self.config.cruise_altitude_m

                # Calculate heading to next point
                next_idx = (i + 1) % len(pass_boundary)
                heading = bearing_between(coord, pass_boundary[next_idx])

                wp = Waypoint(
                    index=wp_index,
                    coordinate=coord,
                    speed_ms=self.config.cruise_speed_ms,
                    heading_deg=heading,
                    spray_on=True if self.config.mode == FlightMode.SPRAYING else False,
                    spray_rate_l_ha=self.config.spray_rate_l_ha,
                )
                waypoints.append(wp)
                wp_index += 1

                # Calculate distance
                if i > 0:
                    total_distance += haversine_distance(pass_boundary[i - 1], coord)

            # Close the loop
            if len(pass_boundary) > 0:
                total_distance += haversine_distance(pass_boundary[-1], pass_boundary[0])

        if len(waypoints) == 0:
            result.error_en = "Could not generate perimeter path"
            result.error_ar = "لا يمكن إنشاء مسار المحيط"
            return result

        # Calculate area and timing
        area_ha = calculate_polygon_area(boundary) / 10000
        flight_time_min = (total_distance / self.config.cruise_speed_ms) / 60

        # Create flight path
        centroid = polygon_centroid(boundary)
        if home_location is None:
            home_location = centroid

        flight_path = FlightPath(
            id=generate_id("fp"),
            name=name,
            name_ar=name_ar,
            waypoints=waypoints,
            pattern=FlightPattern.PERIMETER,
            total_distance_m=total_distance,
            estimated_duration_min=flight_time_min,
            cruise_altitude_m=self.config.cruise_altitude_m,
            cruise_speed_ms=self.config.cruise_speed_ms,
            swath_width_m=self.config.swath_width_m,
            overlap_percent=self.config.overlap_percent,
            coverage_area_ha=area_ha,
            effective_area_ha=area_ha * (passes * self.config.swath_width_m) / 100,  # Approximate
            home_location=home_location,
            safe_altitude_m=self.config.safe_altitude_m,
        )

        result.success = True
        result.flight_path = flight_path
        result.total_waypoints = len(waypoints)
        result.total_distance_m = total_distance
        result.estimated_duration_min = flight_time_min
        result.coverage_area_ha = area_ha
        result.spray_passes = passes

        return result

    def _clip_line_to_polygon(
        self, line_start: Coordinate, line_end: Coordinate, polygon: list[Coordinate]
    ) -> list[tuple[Coordinate, Coordinate]]:
        """
        Clip line segment to polygon boundary.
        قص قطعة الخط إلى حدود المضلع.

        Returns list of line segments inside the polygon.
        """
        # Simple implementation: check if start/end are inside, find intersections
        start_inside = point_in_polygon(line_start, polygon)
        end_inside = point_in_polygon(line_end, polygon)

        if start_inside and end_inside:
            return [(line_start, line_end)]

        # Find intersection points
        intersections = []
        for i in range(len(polygon)):
            j = (i + 1) % len(polygon)
            intersection = self._line_intersection(line_start, line_end, polygon[i], polygon[j])
            if intersection:
                intersections.append(intersection)

        if not intersections:
            if start_inside or end_inside:
                return [(line_start, line_end)]
            return []

        # Sort intersections by distance from start
        intersections.sort(key=lambda p: haversine_distance(line_start, p))

        # Build segments
        segments = []
        points = [line_start] + intersections + [line_end]

        for i in range(len(points) - 1):
            midpoint = Coordinate(
                lat=(points[i].lat + points[i + 1].lat) / 2,
                lng=(points[i].lng + points[i + 1].lng) / 2,
                alt_agl_m=self.config.cruise_altitude_m,
            )
            if point_in_polygon(midpoint, polygon):
                seg_start = Coordinate(
                    lat=points[i].lat, lng=points[i].lng, alt_agl_m=self.config.cruise_altitude_m
                )
                seg_end = Coordinate(
                    lat=points[i + 1].lat,
                    lng=points[i + 1].lng,
                    alt_agl_m=self.config.cruise_altitude_m,
                )
                segments.append((seg_start, seg_end))

        return segments

    def _line_intersection(
        self, p1: Coordinate, p2: Coordinate, p3: Coordinate, p4: Coordinate
    ) -> Coordinate | None:
        """
        Find intersection point of two line segments.
        إيجاد نقطة تقاطع قطعتي خط.
        """
        x1, y1 = p1.lng, p1.lat
        x2, y2 = p2.lng, p2.lat
        x3, y3 = p3.lng, p3.lat
        x4, y4 = p4.lng, p4.lat

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return Coordinate(lat=y, lng=x, alt_agl_m=self.config.cruise_altitude_m)

        return None


# ==============================================================================
# Weather Assessment - تقييم الطقس
# ==============================================================================


def assess_flight_weather(
    temperature_c: float,
    humidity_percent: float,
    wind_speed_ms: float,
    wind_direction_deg: float,
    precipitation_mm: float = 0,
    visibility_km: float = 10,
    drone_specs: DroneSpecs | None = None,
) -> WeatherCheck:
    """
    Assess weather conditions for drone flight.
    تقييم ظروف الطقس لطيران الطائرة.

    Args:
        temperature_c: Temperature in Celsius | درجة الحرارة بالسلسيوس
        humidity_percent: Relative humidity | الرطوبة النسبية
        wind_speed_ms: Wind speed in m/s | سرعة الرياح بالمتر/ثانية
        wind_direction_deg: Wind direction in degrees | اتجاه الرياح بالدرجات
        precipitation_mm: Precipitation | الهطول بالملم
        visibility_km: Visibility in km | الرؤية بالكم
        drone_specs: Drone specifications | مواصفات الطائرة

    Returns:
        WeatherCheck with assessment | تقييم الطقس
    """
    check = WeatherCheck(
        check_time=datetime.now(UTC),
        condition=WeatherCondition.OPTIMAL,
        temperature_c=temperature_c,
        humidity_percent=humidity_percent,
        wind_speed_ms=wind_speed_ms,
        wind_direction_deg=wind_direction_deg,
        precipitation_mm=precipitation_mm,
        visibility_km=visibility_km,
        can_fly=True,
    )

    warnings_en = []
    warnings_ar = []

    # Get wind limit from drone specs or use default
    max_wind = MAX_WIND_SPEED_MS
    if drone_specs:
        max_wind = drone_specs.max_wind_speed_ms

    # Wind assessment
    if wind_speed_ms > max_wind:
        check.condition = WeatherCondition.PROHIBITED
        check.can_fly = False
        check.message_en = (
            f"Wind speed ({wind_speed_ms:.1f} m/s) exceeds safe limit ({max_wind} m/s)"
        )
        check.message_ar = (
            f"سرعة الرياح ({wind_speed_ms:.1f} م/ث) تتجاوز الحد الآمن ({max_wind} م/ث)"
        )
        return check
    elif wind_speed_ms > max_wind * 0.75:
        check.condition = WeatherCondition.MARGINAL
        warnings_en.append(f"High wind ({wind_speed_ms:.1f} m/s) - reduced spray efficiency")
        warnings_ar.append(f"رياح قوية ({wind_speed_ms:.1f} م/ث) - كفاءة رش منخفضة")

    # Precipitation
    if precipitation_mm > 0:
        check.condition = WeatherCondition.PROHIBITED
        check.can_fly = False
        check.message_en = "Do not fly during rain"
        check.message_ar = "لا تطير أثناء المطر"
        return check

    # Temperature
    min_temp = -10
    max_temp = 45
    if drone_specs:
        min_temp = drone_specs.operating_temp_min_c
        max_temp = drone_specs.operating_temp_max_c

    if temperature_c < min_temp or temperature_c > max_temp:
        check.condition = WeatherCondition.PROHIBITED
        check.can_fly = False
        check.message_en = f"Temperature ({temperature_c}C) outside operating range"
        check.message_ar = f"درجة الحرارة ({temperature_c}C) خارج نطاق التشغيل"
        return check

    if temperature_c > 40:
        warnings_en.append("High temperature - reduced battery performance expected")
        warnings_ar.append("درجة حرارة عالية - أداء بطارية منخفض متوقع")

    # Visibility
    if visibility_km < MIN_VISIBILITY_KM:
        check.condition = WeatherCondition.UNFAVORABLE
        check.can_fly = False
        check.message_en = f"Low visibility ({visibility_km} km) - maintain visual line of sight"
        check.message_ar = f"رؤية منخفضة ({visibility_km} كم) - حافظ على خط البصر"
        return check

    # Delta T for spraying (dry-bulb minus wet-bulb approximation)
    # August-Roche-Magnus approximation for wet-bulb depression
    wet_bulb_c = temperature_c * math.atan(0.151977 * (humidity_percent + 8.313659) ** 0.5) + math.atan(temperature_c + humidity_percent) - math.atan(humidity_percent - 1.676331) + 0.00391838 * humidity_percent ** 1.5 * math.atan(0.023101 * humidity_percent) - 4.686035
    delta_t = temperature_c - wet_bulb_c

    if delta_t < 2:
        warnings_en.append("Low Delta T - risk of evaporation and spray drift")
        warnings_ar.append("دلتا تي منخفض - خطر التبخر وانجراف الرش")
    elif delta_t > 10:
        warnings_en.append("High Delta T - spray evaporation likely")
        warnings_ar.append("دلتا تي مرتفع - تبخر الرش محتمل")

    # Set final status
    if len(warnings_en) > 0 and check.condition == WeatherCondition.OPTIMAL:
        check.condition = WeatherCondition.ACCEPTABLE

    check.warnings_en = warnings_en
    check.warnings_ar = warnings_ar

    if check.can_fly:
        check.message_en = f"Weather conditions are {check.condition.value} for flight"
        check.message_ar = f"ظروف الطقس {_condition_ar(check.condition)} للطيران"

    return check


def _condition_ar(condition: WeatherCondition) -> str:
    """Get Arabic translation of weather condition"""
    mapping = {
        WeatherCondition.OPTIMAL: "مثالية",
        WeatherCondition.ACCEPTABLE: "مقبولة",
        WeatherCondition.MARGINAL: "حدية",
        WeatherCondition.UNFAVORABLE: "غير ملائمة",
        WeatherCondition.PROHIBITED: "ممنوعة",
    }
    return mapping.get(condition, condition.value)


# ==============================================================================
# Convenience Functions - دوال مساعدة
# ==============================================================================


def create_spray_flight_plan(
    boundary: list[Coordinate],
    spray_rate_l_ha: float,
    swath_width_m: float = 5.0,
    altitude_m: float = 3.0,
    speed_ms: float = 5.0,
    pattern: FlightPattern = FlightPattern.PARALLEL,
    name: str = "Spray Mission",
    name_ar: str = "مهمة الرش",
    home_location: Coordinate | None = None,
) -> FlightPlanResult:
    """
    Create a spray mission flight plan.
    إنشاء خطة طيران لمهمة رش.

    Args:
        boundary: Field boundary | حدود الحقل
        spray_rate_l_ha: Application rate in L/ha | معدل الرش لتر/هكتار
        swath_width_m: Spray width in meters | عرض الرش بالمتر
        altitude_m: Flight altitude in meters | ارتفاع الطيران بالمتر
        speed_ms: Flight speed in m/s | سرعة الطيران م/ث
        pattern: Flight pattern | نمط الطيران
        name: Mission name | اسم المهمة
        name_ar: Mission name in Arabic | اسم المهمة بالعربية
        home_location: Home location | موقع المنزل

    Returns:
        FlightPlanResult | نتيجة خطة الطيران
    """
    config = FlightPlanConfig(
        mode=FlightMode.SPRAYING,
        cruise_altitude_m=altitude_m,
        cruise_speed_ms=speed_ms,
        swath_width_m=swath_width_m,
        overlap_percent=10.0,
        pattern=pattern,
        spray_rate_l_ha=spray_rate_l_ha,
    )

    planner = FlightPlanner(config)

    if pattern == FlightPattern.CROSSHATCH:
        return planner.generate_crosshatch_path(
            boundary=boundary, name=name, name_ar=name_ar, home_location=home_location
        )
    elif pattern == FlightPattern.PERIMETER:
        return planner.generate_perimeter_path(
            boundary=boundary, name=name, name_ar=name_ar, home_location=home_location
        )
    else:
        return planner.generate_parallel_path(
            boundary=boundary, name=name, name_ar=name_ar, home_location=home_location
        )


def create_mapping_flight_plan(
    boundary: list[Coordinate],
    gsd_cm_px: float = 2.0,
    frontal_overlap: float = 80.0,
    side_overlap: float = 70.0,
    name: str = "Mapping Mission",
    name_ar: str = "مهمة التصوير",
    home_location: Coordinate | None = None,
) -> FlightPlanResult:
    """
    Create a mapping mission flight plan.
    إنشاء خطة طيران لمهمة تصوير.

    Args:
        boundary: Field boundary | حدود الحقل
        gsd_cm_px: Target GSD in cm/pixel | دقة الأرض سم/بكسل
        frontal_overlap: Frontal overlap percentage | نسبة التداخل الأمامي
        side_overlap: Side overlap percentage | نسبة التداخل الجانبي
        name: Mission name | اسم المهمة
        name_ar: Mission name in Arabic | اسم المهمة بالعربية
        home_location: Home location | موقع المنزل

    Returns:
        FlightPlanResult | نتيجة خطة الطيران
    """
    config = FlightPlanConfig(
        mode=FlightMode.MAPPING,
        overlap_percent=frontal_overlap,
        side_overlap_percent=side_overlap,
        pattern=FlightPattern.PARALLEL,
    )

    planner = FlightPlanner(config)

    return planner.generate_mapping_path(
        boundary=boundary,
        gsd_cm_px=gsd_cm_px,
        name=name,
        name_ar=name_ar,
        home_location=home_location,
    )


def estimate_flight_resources(
    area_ha: float,
    spray_rate_l_ha: float,
    tank_capacity_l: float,
    flight_time_per_tank_min: float = 15.0,
) -> dict:
    """
    Estimate resources needed for a spray mission.
    تقدير الموارد اللازمة لمهمة الرش.

    Args:
        area_ha: Field area in hectares | مساحة الحقل بالهكتار
        spray_rate_l_ha: Application rate L/ha | معدل الرش لتر/هكتار
        tank_capacity_l: Tank capacity in liters | سعة الخزان باللتر
        flight_time_per_tank_min: Flight time per tank | وقت الطيران لكل خزان

    Returns:
        Dictionary with resource estimates | قاموس بتقديرات الموارد
    """
    total_volume_l = area_ha * spray_rate_l_ha
    tank_fills = math.ceil(total_volume_l / tank_capacity_l)
    total_flight_time_min = tank_fills * flight_time_per_tank_min

    # Estimate batteries (assuming 20 min flight per battery)
    batteries_needed = math.ceil(total_flight_time_min / 20)

    return {
        "total_volume_l": total_volume_l,
        "total_volume_l_ar": f"{total_volume_l:.1f} لتر",
        "tank_fills": tank_fills,
        "tank_fills_ar": f"{tank_fills} تعبئة",
        "total_flight_time_min": total_flight_time_min,
        "total_flight_time_ar": f"{total_flight_time_min:.0f} دقيقة",
        "batteries_needed": batteries_needed,
        "batteries_needed_ar": f"{batteries_needed} بطارية",
        "estimated_cost_factor": total_volume_l + (batteries_needed * 10),  # Simplified cost factor
    }
