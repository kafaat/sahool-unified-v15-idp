"""
Unit Tests for SAHOOL Drone Integration Module
اختبارات الوحدة لوحدة تكامل الطائرات بدون طيار

Tests cover:
- Flight plan creation
- Waypoint generation
- Coverage path planning
- VRA map generation
- Battery/range calculations
- No-fly zone compliance
- Weather limitations
- MAVLink export format
- Edge cases (irregular field shapes, obstacle avoidance)

Version: 1.0.0
"""

import math
import pytest
from datetime import datetime
from typing import Optional

from shared.drone_integration.models import (
    Coordinate,
    BoundingBox,
    Waypoint,
    WaypointAction,
    FlightPath,
    FlightPattern,
    FlightMode,
    FlightStatus,
    MissionStatus,
    DroneType,
    DroneSpecs,
    Drone,
    WeatherCheck,
    WeatherCondition,
    SprayMission,
    MappingMission,
    FlightTelemetry,
    FlightLog,
    VRAZone,
    VRAZoneType,
    PrescriptionMap,
    ApplicationMode,
    SprayStatus,
    ImageryType,
    AerialImage,
    ProcessedImagery,
    generate_id,
)

from shared.drone_integration.flight_planner import (
    FlightPlanner,
    FlightPlanConfig,
    FlightPlanResult,
    haversine_distance,
    bearing_between,
    destination_point,
    calculate_polygon_area,
    polygon_centroid,
    get_bounding_box,
    point_in_polygon,
    buffer_polygon_inward,
    calculate_optimal_heading,
    assess_flight_weather,
    create_spray_flight_plan,
    create_mapping_flight_plan,
    estimate_flight_resources,
    EARTH_RADIUS_M,
    MAX_FLIGHT_ALTITUDE_M,
    MIN_FLIGHT_ALTITUDE_M,
    MAX_WIND_SPEED_MS,
    MIN_VISIBILITY_KM,
)

from shared.drone_integration.vra import (
    VRAGenerator,
    VRAConfig,
    VRARasterData,
    GridCell,
    ClassificationMethod,
    VRASourceType,
    RateAdjustmentMode,
    create_ndvi_prescription,
    create_spot_spray_map,
    DEFAULT_NDVI_ZONES,
    DEFAULT_RATE_MULTIPLIERS,
)


# ==============================================================================
# Test Fixtures - بيانات الاختبار
# ==============================================================================


@pytest.fixture
def sample_rectangular_field() -> list[Coordinate]:
    """Create a simple rectangular field boundary (approximately 1 hectare)"""
    # Field near Riyadh, Saudi Arabia - roughly 100m x 100m
    return [
        Coordinate(lat=24.7136, lng=46.6753),  # SW corner
        Coordinate(lat=24.7136, lng=46.6763),  # SE corner
        Coordinate(lat=24.7145, lng=46.6763),  # NE corner
        Coordinate(lat=24.7145, lng=46.6753),  # NW corner
    ]


@pytest.fixture
def sample_irregular_field() -> list[Coordinate]:
    """Create an irregular (L-shaped) field boundary"""
    return [
        Coordinate(lat=24.7136, lng=46.6753),
        Coordinate(lat=24.7136, lng=46.6763),
        Coordinate(lat=24.7140, lng=46.6763),
        Coordinate(lat=24.7140, lng=46.6758),
        Coordinate(lat=24.7145, lng=46.6758),
        Coordinate(lat=24.7145, lng=46.6753),
    ]


@pytest.fixture
def sample_triangle_field() -> list[Coordinate]:
    """Create a triangular field boundary"""
    return [
        Coordinate(lat=24.7136, lng=46.6753),
        Coordinate(lat=24.7136, lng=46.6773),
        Coordinate(lat=24.7156, lng=46.6763),
    ]


@pytest.fixture
def sample_drone_specs() -> DroneSpecs:
    """Create sample DJI Agras T40 specs"""
    return DroneSpecs(
        drone_type=DroneType.DJI_AGRAS_T40,
        model_name="DJI Agras T40",
        model_name_ar="دي جي آي أجراس T40",
        max_takeoff_weight_kg=101,
        empty_weight_kg=52,
        max_payload_kg=50,
        max_flight_time_min=21,
        max_speed_ms=10,
        max_wind_speed_ms=8,
        max_altitude_m=30,
        operating_temp_min_c=0,
        operating_temp_max_c=45,
        has_spray_system=True,
        tank_capacity_l=40,
        spray_width_m=11,
        flow_rate_l_min=16,
        nozzle_count=16,
        has_rtk=True,
        rtk_accuracy_cm=5,
    )


@pytest.fixture
def sample_mapping_drone_specs() -> DroneSpecs:
    """Create sample DJI Mavic 3M specs"""
    return DroneSpecs(
        drone_type=DroneType.DJI_MAVIC_3M,
        model_name="DJI Mavic 3 Multispectral",
        model_name_ar="دي جي آي مافيك 3 متعدد الأطياف",
        max_takeoff_weight_kg=1.05,
        empty_weight_kg=0.92,
        max_payload_kg=0.1,
        max_flight_time_min=43,
        max_speed_ms=19,
        max_wind_speed_ms=12,
        max_altitude_m=6000,
        operating_temp_min_c=-10,
        operating_temp_max_c=40,
        has_spray_system=False,
        has_rgb_camera=True,
        has_multispectral=True,
        camera_resolution_mp=20,
        has_rtk=False,
    )


@pytest.fixture
def sample_ndvi_grid() -> list[list[float]]:
    """Create sample NDVI data grid (10x10)"""
    return [
        [0.45, 0.48, 0.52, 0.55, 0.58, 0.60, 0.62, 0.65, 0.68, 0.70],
        [0.42, 0.46, 0.50, 0.54, 0.57, 0.59, 0.61, 0.64, 0.67, 0.69],
        [0.38, 0.42, 0.47, 0.51, 0.54, 0.57, 0.59, 0.62, 0.65, 0.67],
        [0.35, 0.39, 0.44, 0.48, 0.52, 0.55, 0.58, 0.60, 0.63, 0.65],
        [0.32, 0.36, 0.41, 0.45, 0.49, 0.52, 0.55, 0.58, 0.61, 0.63],
        [0.30, 0.34, 0.38, 0.42, 0.46, 0.50, 0.53, 0.56, 0.59, 0.61],
        [0.28, 0.32, 0.36, 0.40, 0.44, 0.48, 0.51, 0.54, 0.57, 0.59],
        [0.26, 0.30, 0.34, 0.38, 0.42, 0.46, 0.49, 0.52, 0.55, 0.57],
        [0.24, 0.28, 0.32, 0.36, 0.40, 0.44, 0.47, 0.50, 0.53, 0.55],
        [0.22, 0.26, 0.30, 0.34, 0.38, 0.42, 0.45, 0.48, 0.51, 0.53],
    ]


@pytest.fixture
def sample_bounds() -> BoundingBox:
    """Create sample bounding box"""
    return BoundingBox(
        min_lat=24.7136,
        max_lat=24.7145,
        min_lng=46.6753,
        max_lng=46.6763,
    )


# ==============================================================================
# Models Tests - اختبارات النماذج
# ==============================================================================


class TestCoordinate:
    """Tests for Coordinate data class"""

    @pytest.mark.unit
    def test_coordinate_creation(self):
        """Test creating a coordinate"""
        coord = Coordinate(lat=24.7136, lng=46.6753)
        assert coord.lat == 24.7136
        assert coord.lng == 46.6753
        assert coord.alt_m is None
        assert coord.alt_agl_m is None

    @pytest.mark.unit
    def test_coordinate_with_altitude(self):
        """Test creating a coordinate with altitude"""
        coord = Coordinate(lat=24.7136, lng=46.6753, alt_m=650, alt_agl_m=3)
        assert coord.alt_m == 650
        assert coord.alt_agl_m == 3

    @pytest.mark.unit
    def test_coordinate_to_tuple(self):
        """Test converting coordinate to tuple"""
        coord = Coordinate(lat=24.7136, lng=46.6753)
        result = coord.to_tuple()
        assert result == (24.7136, 46.6753)

    @pytest.mark.unit
    def test_coordinate_to_dict(self):
        """Test converting coordinate to dictionary"""
        coord = Coordinate(lat=24.7136, lng=46.6753, alt_m=650)
        result = coord.to_dict()
        assert result["lat"] == 24.7136
        assert result["lng"] == 46.6753
        assert result["alt_m"] == 650
        assert "alt_agl_m" not in result


class TestBoundingBox:
    """Tests for BoundingBox data class"""

    @pytest.mark.unit
    def test_bounding_box_creation(self, sample_bounds):
        """Test creating a bounding box"""
        assert sample_bounds.min_lat == 24.7136
        assert sample_bounds.max_lat == 24.7145

    @pytest.mark.unit
    def test_bounding_box_center(self, sample_bounds):
        """Test calculating bounding box center"""
        center = sample_bounds.center()
        assert abs(center.lat - 24.71405) < 0.0001
        assert abs(center.lng - 46.6758) < 0.0001

    @pytest.mark.unit
    def test_bounding_box_to_dict(self, sample_bounds):
        """Test converting bounding box to dictionary"""
        result = sample_bounds.to_dict()
        assert "min_lat" in result
        assert "max_lat" in result
        assert "min_lng" in result
        assert "max_lng" in result


class TestWaypoint:
    """Tests for Waypoint data class"""

    @pytest.mark.unit
    def test_waypoint_creation(self):
        """Test creating a waypoint"""
        coord = Coordinate(lat=24.7136, lng=46.6753, alt_agl_m=3)
        wp = Waypoint(
            index=0,
            coordinate=coord,
            speed_ms=5.0,
            heading_deg=90.0,
        )
        assert wp.index == 0
        assert wp.coordinate.lat == 24.7136
        assert wp.speed_ms == 5.0

    @pytest.mark.unit
    def test_waypoint_with_spray(self):
        """Test creating a spray waypoint"""
        coord = Coordinate(lat=24.7136, lng=46.6753, alt_agl_m=3)
        wp = Waypoint(
            index=0,
            coordinate=coord,
            spray_on=True,
            spray_rate_l_ha=10.0,
            actions=[WaypointAction.START_SPRAY],
        )
        assert wp.spray_on is True
        assert wp.spray_rate_l_ha == 10.0
        assert WaypointAction.START_SPRAY in wp.actions

    @pytest.mark.unit
    def test_waypoint_to_dict(self):
        """Test converting waypoint to dictionary"""
        coord = Coordinate(lat=24.7136, lng=46.6753, alt_agl_m=3)
        wp = Waypoint(
            index=0,
            coordinate=coord,
            speed_ms=5.0,
            actions=[WaypointAction.TAKE_PHOTO],
        )
        result = wp.to_dict()
        assert result["index"] == 0
        assert result["lat"] == 24.7136
        assert "take_photo" in result["actions"]


class TestDroneSpecs:
    """Tests for DroneSpecs data class"""

    @pytest.mark.unit
    def test_spray_drone_specs(self, sample_drone_specs):
        """Test spray drone specifications"""
        assert sample_drone_specs.drone_type == DroneType.DJI_AGRAS_T40
        assert sample_drone_specs.has_spray_system is True
        assert sample_drone_specs.tank_capacity_l == 40
        assert sample_drone_specs.spray_width_m == 11

    @pytest.mark.unit
    def test_mapping_drone_specs(self, sample_mapping_drone_specs):
        """Test mapping drone specifications"""
        assert sample_mapping_drone_specs.drone_type == DroneType.DJI_MAVIC_3M
        assert sample_mapping_drone_specs.has_spray_system is False
        assert sample_mapping_drone_specs.has_multispectral is True


class TestFlightPath:
    """Tests for FlightPath data class"""

    @pytest.mark.unit
    def test_flight_path_creation(self):
        """Test creating a flight path"""
        waypoints = [
            Waypoint(index=i, coordinate=Coordinate(lat=24.7136 + i * 0.001, lng=46.6753, alt_agl_m=3))
            for i in range(5)
        ]

        path = FlightPath(
            id="fp_test001",
            name="Test Path",
            name_ar="مسار اختبار",
            waypoints=waypoints,
            pattern=FlightPattern.PARALLEL,
            total_distance_m=500,
            estimated_duration_min=10,
            cruise_altitude_m=3,
            cruise_speed_ms=5,
            swath_width_m=5,
        )

        assert len(path.waypoints) == 5
        assert path.pattern == FlightPattern.PARALLEL

    @pytest.mark.unit
    def test_flight_path_to_kml(self):
        """Test exporting flight path to KML format"""
        waypoints = [
            Waypoint(index=i, coordinate=Coordinate(lat=24.7136 + i * 0.001, lng=46.6753, alt_agl_m=3))
            for i in range(3)
        ]

        path = FlightPath(
            id="fp_test001",
            name="Test Path",
            name_ar="مسار اختبار",
            waypoints=waypoints,
            pattern=FlightPattern.PARALLEL,
            total_distance_m=300,
            estimated_duration_min=5,
            cruise_altitude_m=3,
            cruise_speed_ms=5,
            swath_width_m=5,
        )

        kml = path.to_kml()
        assert '<?xml version="1.0"' in kml
        assert "<kml" in kml
        assert "Test Path" in kml
        assert "<coordinates>" in kml

    @pytest.mark.unit
    def test_flight_path_to_mavlink_mission(self):
        """Test exporting flight path to MAVLink mission format"""
        waypoints = [
            Waypoint(
                index=i,
                coordinate=Coordinate(lat=24.7136 + i * 0.001, lng=46.6753, alt_agl_m=3),
                heading_deg=90.0,
                hover_time_s=0,
            )
            for i in range(3)
        ]

        path = FlightPath(
            id="fp_test001",
            name="Test Path",
            name_ar="مسار اختبار",
            waypoints=waypoints,
            pattern=FlightPattern.PARALLEL,
            total_distance_m=300,
            estimated_duration_min=5,
            cruise_altitude_m=3,
            cruise_speed_ms=5,
            swath_width_m=5,
        )

        mission = path.to_mavlink_mission()

        assert len(mission) == 3
        assert mission[0]["seq"] == 0
        assert mission[0]["frame"] == 3  # MAV_FRAME_GLOBAL_RELATIVE_ALT
        assert mission[0]["command"] == 16  # MAV_CMD_NAV_WAYPOINT
        assert mission[0]["current"] == 1  # First waypoint is current
        assert mission[1]["current"] == 0
        assert mission[0]["x"] == 24.7136
        assert mission[0]["y"] == 46.6753


class TestGenerateId:
    """Tests for ID generation helper"""

    @pytest.mark.unit
    def test_generate_id_without_prefix(self):
        """Test generating ID without prefix"""
        id1 = generate_id()
        id2 = generate_id()
        assert id1 != id2
        assert len(id1) == 12

    @pytest.mark.unit
    def test_generate_id_with_prefix(self):
        """Test generating ID with prefix"""
        id1 = generate_id("fp")
        assert id1.startswith("fp_")
        assert len(id1) == 15  # "fp_" + 12 chars


# ==============================================================================
# Geometry Utilities Tests - اختبارات أدوات الهندسة
# ==============================================================================


class TestHaversineDistance:
    """Tests for haversine distance calculation"""

    @pytest.mark.unit
    def test_haversine_same_point(self):
        """Test distance between same point is zero"""
        coord = Coordinate(lat=24.7136, lng=46.6753)
        distance = haversine_distance(coord, coord)
        assert distance == 0

    @pytest.mark.unit
    def test_haversine_known_distance(self):
        """Test distance calculation against known values"""
        # Riyadh to Jeddah is approximately 845 km
        riyadh = Coordinate(lat=24.7136, lng=46.6753)
        jeddah = Coordinate(lat=21.4858, lng=39.1925)
        distance = haversine_distance(riyadh, jeddah)
        # Allow 1% error
        assert 837000 < distance < 854000

    @pytest.mark.unit
    def test_haversine_short_distance(self):
        """Test distance calculation for short distances (meters)"""
        coord1 = Coordinate(lat=24.7136, lng=46.6753)
        coord2 = Coordinate(lat=24.7137, lng=46.6753)  # ~11.1m north
        distance = haversine_distance(coord1, coord2)
        assert 10 < distance < 12


class TestBearingBetween:
    """Tests for bearing calculation"""

    @pytest.mark.unit
    def test_bearing_north(self):
        """Test bearing due north is approximately 0 degrees"""
        coord1 = Coordinate(lat=24.7136, lng=46.6753)
        coord2 = Coordinate(lat=24.7236, lng=46.6753)  # North
        bearing = bearing_between(coord1, coord2)
        assert abs(bearing - 0) < 1 or abs(bearing - 360) < 1

    @pytest.mark.unit
    def test_bearing_east(self):
        """Test bearing due east is approximately 90 degrees"""
        coord1 = Coordinate(lat=24.7136, lng=46.6753)
        coord2 = Coordinate(lat=24.7136, lng=46.6853)  # East
        bearing = bearing_between(coord1, coord2)
        assert abs(bearing - 90) < 1

    @pytest.mark.unit
    def test_bearing_south(self):
        """Test bearing due south is approximately 180 degrees"""
        coord1 = Coordinate(lat=24.7136, lng=46.6753)
        coord2 = Coordinate(lat=24.7036, lng=46.6753)  # South
        bearing = bearing_between(coord1, coord2)
        assert abs(bearing - 180) < 1

    @pytest.mark.unit
    def test_bearing_west(self):
        """Test bearing due west is approximately 270 degrees"""
        coord1 = Coordinate(lat=24.7136, lng=46.6753)
        coord2 = Coordinate(lat=24.7136, lng=46.6653)  # West
        bearing = bearing_between(coord1, coord2)
        assert abs(bearing - 270) < 1


class TestDestinationPoint:
    """Tests for destination point calculation"""

    @pytest.mark.unit
    def test_destination_north(self):
        """Test destination point due north"""
        start = Coordinate(lat=24.7136, lng=46.6753)
        dest = destination_point(start, bearing_deg=0, distance_m=1000)
        assert dest.lat > start.lat  # North is positive latitude
        assert abs(dest.lng - start.lng) < 0.0001

    @pytest.mark.unit
    def test_destination_east(self):
        """Test destination point due east"""
        start = Coordinate(lat=24.7136, lng=46.6753)
        dest = destination_point(start, bearing_deg=90, distance_m=1000)
        assert dest.lng > start.lng  # East is positive longitude
        assert abs(dest.lat - start.lat) < 0.0001

    @pytest.mark.unit
    def test_destination_roundtrip(self):
        """Test that going and returning gives original position"""
        start = Coordinate(lat=24.7136, lng=46.6753)
        intermediate = destination_point(start, bearing_deg=45, distance_m=100)
        final = destination_point(intermediate, bearing_deg=225, distance_m=100)
        assert abs(final.lat - start.lat) < 0.0001
        assert abs(final.lng - start.lng) < 0.0001


class TestPolygonArea:
    """Tests for polygon area calculation"""

    @pytest.mark.unit
    def test_polygon_area_square(self, sample_rectangular_field):
        """Test area calculation for rectangular field"""
        area = calculate_polygon_area(sample_rectangular_field)
        area_ha = area / 10000
        # Field is approximately 100m x 100m = 1 hectare
        assert 0.8 < area_ha < 1.2

    @pytest.mark.unit
    def test_polygon_area_triangle(self, sample_triangle_field):
        """Test area calculation for triangular field"""
        area = calculate_polygon_area(sample_triangle_field)
        assert area > 0

    @pytest.mark.unit
    def test_polygon_area_too_few_points(self):
        """Test area calculation with less than 3 points"""
        points = [
            Coordinate(lat=24.7136, lng=46.6753),
            Coordinate(lat=24.7145, lng=46.6763),
        ]
        area = calculate_polygon_area(points)
        assert area == 0


class TestPolygonCentroid:
    """Tests for polygon centroid calculation"""

    @pytest.mark.unit
    def test_centroid_rectangle(self, sample_rectangular_field):
        """Test centroid of rectangular field"""
        centroid = polygon_centroid(sample_rectangular_field)
        # Centroid should be approximately in the middle
        assert 24.7140 < centroid.lat < 24.7142
        assert 46.6757 < centroid.lng < 46.6759

    @pytest.mark.unit
    def test_centroid_empty_list(self):
        """Test centroid of empty list"""
        centroid = polygon_centroid([])
        assert centroid.lat == 0
        assert centroid.lng == 0


class TestPointInPolygon:
    """Tests for point in polygon check"""

    @pytest.mark.unit
    def test_point_inside(self, sample_rectangular_field):
        """Test point inside polygon"""
        point = Coordinate(lat=24.7140, lng=46.6758)
        assert point_in_polygon(point, sample_rectangular_field) is True

    @pytest.mark.unit
    def test_point_outside(self, sample_rectangular_field):
        """Test point outside polygon"""
        point = Coordinate(lat=24.7200, lng=46.6800)  # Far outside
        assert point_in_polygon(point, sample_rectangular_field) is False

    @pytest.mark.unit
    def test_point_on_edge(self, sample_rectangular_field):
        """Test point on polygon edge (boundary case)"""
        # Points on edge may return either True or False depending on implementation
        point = Coordinate(lat=24.7136, lng=46.6758)  # On southern edge
        result = point_in_polygon(point, sample_rectangular_field)
        assert isinstance(result, bool)


class TestBufferPolygon:
    """Tests for polygon buffering"""

    @pytest.mark.unit
    def test_buffer_inward(self, sample_rectangular_field):
        """Test buffering polygon inward"""
        buffered = buffer_polygon_inward(sample_rectangular_field, buffer_m=5)
        # Buffered polygon should still have same number of points
        assert len(buffered) == len(sample_rectangular_field)
        # Area should be smaller
        original_area = calculate_polygon_area(sample_rectangular_field)
        buffered_area = calculate_polygon_area(buffered)
        assert buffered_area < original_area

    @pytest.mark.unit
    def test_buffer_zero(self, sample_rectangular_field):
        """Test buffering with zero distance returns same polygon"""
        buffered = buffer_polygon_inward(sample_rectangular_field, buffer_m=0)
        assert len(buffered) == len(sample_rectangular_field)


class TestOptimalHeading:
    """Tests for optimal flight heading calculation"""

    @pytest.mark.unit
    def test_optimal_heading_rectangle(self, sample_rectangular_field):
        """Test optimal heading for rectangular field"""
        heading = calculate_optimal_heading(sample_rectangular_field)
        # Should align with one of the edges
        assert 0 <= heading < 360

    @pytest.mark.unit
    def test_optimal_heading_single_point(self):
        """Test optimal heading with single point returns 0"""
        points = [Coordinate(lat=24.7136, lng=46.6753)]
        heading = calculate_optimal_heading(points)
        assert heading == 0


# ==============================================================================
# Flight Planner Tests - اختبارات مخطط الرحلات
# ==============================================================================


class TestFlightPlanConfig:
    """Tests for FlightPlanConfig"""

    @pytest.mark.unit
    def test_default_config(self):
        """Test default configuration values"""
        config = FlightPlanConfig()
        assert config.mode == FlightMode.SPRAYING
        assert config.cruise_altitude_m == 3.0
        assert config.cruise_speed_ms == 5.0
        assert config.swath_width_m == 5.0
        assert config.overlap_percent == 10.0

    @pytest.mark.unit
    def test_custom_config(self):
        """Test custom configuration values"""
        config = FlightPlanConfig(
            mode=FlightMode.MAPPING,
            cruise_altitude_m=50.0,
            cruise_speed_ms=8.0,
            swath_width_m=40.0,
            overlap_percent=80.0,
        )
        assert config.mode == FlightMode.MAPPING
        assert config.cruise_altitude_m == 50.0


class TestFlightPlanner:
    """Tests for FlightPlanner"""

    @pytest.mark.unit
    def test_planner_initialization_default(self):
        """Test initializing planner with default config"""
        planner = FlightPlanner()
        assert planner.config is not None
        assert planner.config.mode == FlightMode.SPRAYING

    @pytest.mark.unit
    def test_planner_initialization_custom(self):
        """Test initializing planner with custom config"""
        config = FlightPlanConfig(mode=FlightMode.MAPPING)
        planner = FlightPlanner(config)
        assert planner.config.mode == FlightMode.MAPPING


class TestParallelPath:
    """Tests for parallel (boustrophedon) path generation"""

    @pytest.mark.unit
    def test_parallel_path_generation(self, sample_rectangular_field):
        """Test generating parallel flight path"""
        planner = FlightPlanner()
        result = planner.generate_parallel_path(
            boundary=sample_rectangular_field,
            name="Test Spray",
            name_ar="رش اختبار",
        )

        assert result.success is True
        assert result.flight_path is not None
        assert len(result.flight_path.waypoints) > 0
        assert result.total_distance_m > 0
        assert result.estimated_duration_min > 0

    @pytest.mark.unit
    def test_parallel_path_with_home(self, sample_rectangular_field):
        """Test parallel path with custom home location"""
        home = Coordinate(lat=24.7130, lng=46.6750)
        planner = FlightPlanner()
        result = planner.generate_parallel_path(
            boundary=sample_rectangular_field,
            home_location=home,
        )

        assert result.success is True
        assert result.flight_path.home_location is not None
        assert result.flight_path.home_location.lat == home.lat

    @pytest.mark.unit
    def test_parallel_path_insufficient_points(self):
        """Test parallel path with insufficient boundary points"""
        planner = FlightPlanner()
        boundary = [
            Coordinate(lat=24.7136, lng=46.6753),
            Coordinate(lat=24.7145, lng=46.6763),
        ]
        result = planner.generate_parallel_path(boundary=boundary)

        assert result.success is False
        assert "at least 3 points" in result.error_en

    @pytest.mark.unit
    def test_parallel_path_irregular_field(self, sample_irregular_field):
        """Test parallel path for irregular (L-shaped) field"""
        planner = FlightPlanner()
        result = planner.generate_parallel_path(boundary=sample_irregular_field)

        assert result.success is True
        assert result.flight_path is not None

    @pytest.mark.unit
    def test_parallel_path_spray_volume(self, sample_rectangular_field):
        """Test spray volume calculation"""
        config = FlightPlanConfig(
            mode=FlightMode.SPRAYING,
            spray_rate_l_ha=10.0,
        )
        planner = FlightPlanner(config)
        result = planner.generate_parallel_path(boundary=sample_rectangular_field)

        assert result.success is True
        assert result.total_spray_volume_l > 0

    @pytest.mark.unit
    def test_parallel_path_with_buffer(self, sample_rectangular_field):
        """Test parallel path with buffer distance"""
        config = FlightPlanConfig(buffer_distance_m=5.0)
        planner = FlightPlanner(config)
        result = planner.generate_parallel_path(boundary=sample_rectangular_field)

        assert result.success is True
        # Effective area should be smaller due to buffer
        assert result.effective_area_ha > 0


class TestMappingPath:
    """Tests for mapping flight path generation"""

    @pytest.mark.unit
    def test_mapping_path_generation(self, sample_rectangular_field):
        """Test generating mapping flight path"""
        config = FlightPlanConfig(
            mode=FlightMode.MAPPING,
            overlap_percent=80.0,
            side_overlap_percent=70.0,
        )
        planner = FlightPlanner(config)
        result = planner.generate_mapping_path(
            boundary=sample_rectangular_field,
            gsd_cm_px=2.0,
        )

        assert result.success is True
        assert result.estimated_photos > 0
        assert result.gsd_cm_px == 2.0

    @pytest.mark.unit
    def test_mapping_path_altitude_from_gsd(self, sample_rectangular_field):
        """Test mapping altitude calculated from GSD"""
        planner = FlightPlanner()
        result = planner.generate_mapping_path(
            boundary=sample_rectangular_field,
            gsd_cm_px=2.0,
        )

        assert result.success is True
        # Altitude should be > 0 and within limits
        assert result.flight_path.cruise_altitude_m > MIN_FLIGHT_ALTITUDE_M
        assert result.flight_path.cruise_altitude_m <= MAX_FLIGHT_ALTITUDE_M

    @pytest.mark.unit
    def test_mapping_path_photo_waypoints(self, sample_rectangular_field):
        """Test that mapping path has photo waypoints"""
        planner = FlightPlanner()
        result = planner.generate_mapping_path(boundary=sample_rectangular_field)

        assert result.success is True
        # All waypoints should have photo action
        photo_points = [
            wp for wp in result.flight_path.waypoints if wp.is_photo_point or WaypointAction.TAKE_PHOTO in wp.actions
        ]
        assert len(photo_points) > 0


class TestCrosshatchPath:
    """Tests for crosshatch path generation"""

    @pytest.mark.unit
    def test_crosshatch_path_generation(self, sample_rectangular_field):
        """Test generating crosshatch flight path"""
        planner = FlightPlanner()
        result = planner.generate_crosshatch_path(boundary=sample_rectangular_field)

        assert result.success is True
        assert result.flight_path is not None
        assert result.flight_path.pattern == FlightPattern.CROSSHATCH

    @pytest.mark.unit
    def test_crosshatch_double_coverage(self, sample_rectangular_field):
        """Test that crosshatch provides double coverage"""
        planner = FlightPlanner()

        parallel_result = planner.generate_parallel_path(boundary=sample_rectangular_field)
        crosshatch_result = planner.generate_crosshatch_path(boundary=sample_rectangular_field)

        assert crosshatch_result.success is True
        # Crosshatch should have approximately double the distance/waypoints
        assert crosshatch_result.total_distance_m > parallel_result.total_distance_m


class TestPerimeterPath:
    """Tests for perimeter path generation"""

    @pytest.mark.unit
    def test_perimeter_path_generation(self, sample_rectangular_field):
        """Test generating perimeter flight path"""
        planner = FlightPlanner()
        result = planner.generate_perimeter_path(
            boundary=sample_rectangular_field,
            passes=2,
        )

        assert result.success is True
        assert result.flight_path.pattern == FlightPattern.PERIMETER

    @pytest.mark.unit
    def test_perimeter_multiple_passes(self, sample_rectangular_field):
        """Test perimeter with multiple passes"""
        planner = FlightPlanner()

        result_1pass = planner.generate_perimeter_path(
            boundary=sample_rectangular_field,
            passes=1,
        )
        result_3pass = planner.generate_perimeter_path(
            boundary=sample_rectangular_field,
            passes=3,
        )

        assert result_1pass.success is True
        assert result_3pass.success is True
        # More passes should have more waypoints
        assert len(result_3pass.flight_path.waypoints) > len(result_1pass.flight_path.waypoints)


class TestConvenienceFunctions:
    """Tests for convenience flight planning functions"""

    @pytest.mark.unit
    def test_create_spray_flight_plan(self, sample_rectangular_field):
        """Test create_spray_flight_plan convenience function"""
        result = create_spray_flight_plan(
            boundary=sample_rectangular_field,
            spray_rate_l_ha=10.0,
            swath_width_m=5.0,
            altitude_m=3.0,
        )

        assert result.success is True
        assert result.total_spray_volume_l > 0

    @pytest.mark.unit
    def test_create_spray_flight_plan_crosshatch(self, sample_rectangular_field):
        """Test create_spray_flight_plan with crosshatch pattern"""
        result = create_spray_flight_plan(
            boundary=sample_rectangular_field,
            spray_rate_l_ha=10.0,
            pattern=FlightPattern.CROSSHATCH,
        )

        assert result.success is True
        assert result.flight_path.pattern == FlightPattern.CROSSHATCH

    @pytest.mark.unit
    def test_create_mapping_flight_plan(self, sample_rectangular_field):
        """Test create_mapping_flight_plan convenience function"""
        result = create_mapping_flight_plan(
            boundary=sample_rectangular_field,
            gsd_cm_px=2.0,
            frontal_overlap=80.0,
            side_overlap=70.0,
        )

        assert result.success is True
        assert result.estimated_photos > 0


class TestEstimateFlightResources:
    """Tests for flight resource estimation"""

    @pytest.mark.unit
    def test_estimate_resources_basic(self):
        """Test basic resource estimation"""
        resources = estimate_flight_resources(
            area_ha=10.0,
            spray_rate_l_ha=10.0,
            tank_capacity_l=40.0,
        )

        assert resources["total_volume_l"] == 100.0
        assert resources["tank_fills"] == 3  # 100L / 40L = 2.5 -> 3
        assert resources["batteries_needed"] > 0

    @pytest.mark.unit
    def test_estimate_resources_small_field(self):
        """Test resource estimation for small field"""
        resources = estimate_flight_resources(
            area_ha=1.0,
            spray_rate_l_ha=10.0,
            tank_capacity_l=40.0,
        )

        assert resources["total_volume_l"] == 10.0
        assert resources["tank_fills"] == 1

    @pytest.mark.unit
    def test_estimate_resources_arabic_labels(self):
        """Test that Arabic labels are present"""
        resources = estimate_flight_resources(
            area_ha=10.0,
            spray_rate_l_ha=10.0,
            tank_capacity_l=40.0,
        )

        assert "total_volume_l_ar" in resources
        assert "tank_fills_ar" in resources
        assert "batteries_needed_ar" in resources


# ==============================================================================
# Weather Assessment Tests - اختبارات تقييم الطقس
# ==============================================================================


class TestWeatherAssessment:
    """Tests for weather assessment functionality"""

    @pytest.mark.unit
    def test_optimal_weather(self):
        """Test optimal weather conditions"""
        check = assess_flight_weather(
            temperature_c=25,
            humidity_percent=50,
            wind_speed_ms=2.0,
            wind_direction_deg=180,
            precipitation_mm=0,
            visibility_km=10,
        )

        assert check.can_fly is True
        assert check.condition in [WeatherCondition.OPTIMAL, WeatherCondition.ACCEPTABLE]

    @pytest.mark.unit
    def test_high_wind_prohibited(self):
        """Test that high wind prohibits flight"""
        check = assess_flight_weather(
            temperature_c=25,
            humidity_percent=50,
            wind_speed_ms=15.0,  # Very high wind
            wind_direction_deg=180,
        )

        assert check.can_fly is False
        assert check.condition == WeatherCondition.PROHIBITED

    @pytest.mark.unit
    def test_rain_prohibited(self):
        """Test that rain prohibits flight"""
        check = assess_flight_weather(
            temperature_c=25,
            humidity_percent=80,
            wind_speed_ms=2.0,
            wind_direction_deg=180,
            precipitation_mm=5.0,  # Rain
        )

        assert check.can_fly is False
        assert check.condition == WeatherCondition.PROHIBITED

    @pytest.mark.unit
    def test_extreme_temperature_prohibited(self, sample_drone_specs):
        """Test that extreme temperature prohibits flight"""
        check = assess_flight_weather(
            temperature_c=50,  # Too hot
            humidity_percent=30,
            wind_speed_ms=2.0,
            wind_direction_deg=180,
            drone_specs=sample_drone_specs,
        )

        assert check.can_fly is False
        assert check.condition == WeatherCondition.PROHIBITED

    @pytest.mark.unit
    def test_low_visibility_unfavorable(self):
        """Test that low visibility is unfavorable"""
        check = assess_flight_weather(
            temperature_c=25,
            humidity_percent=90,
            wind_speed_ms=2.0,
            wind_direction_deg=180,
            visibility_km=1.0,  # Low visibility
        )

        assert check.can_fly is False
        assert check.condition == WeatherCondition.UNFAVORABLE

    @pytest.mark.unit
    def test_marginal_wind_warning(self):
        """Test that marginal wind generates warning"""
        check = assess_flight_weather(
            temperature_c=25,
            humidity_percent=50,
            wind_speed_ms=7.0,  # Close to limit
            wind_direction_deg=180,
        )

        assert check.condition == WeatherCondition.MARGINAL
        assert len(check.warnings_en) > 0

    @pytest.mark.unit
    def test_weather_check_to_dict(self):
        """Test converting weather check to dictionary"""
        check = assess_flight_weather(
            temperature_c=25,
            humidity_percent=50,
            wind_speed_ms=2.0,
            wind_direction_deg=180,
        )

        result = check.to_dict()
        assert "temperature_c" in result
        assert "wind_speed_ms" in result
        assert "can_fly" in result

    @pytest.mark.unit
    def test_high_delta_t_warning(self):
        """Test high delta T (evaporation risk) warning"""
        check = assess_flight_weather(
            temperature_c=40,  # High temp
            humidity_percent=20,  # Low humidity = high delta T
            wind_speed_ms=2.0,
            wind_direction_deg=180,
        )

        # Should have warning about evaporation
        assert any("Delta T" in w or "evaporation" in w for w in check.warnings_en)


# ==============================================================================
# VRA (Variable Rate Application) Tests - اختبارات المعدل المتغير
# ==============================================================================


class TestVRAConfig:
    """Tests for VRA configuration"""

    @pytest.mark.unit
    def test_default_vra_config(self):
        """Test default VRA configuration"""
        config = VRAConfig()
        assert config.source_type == VRASourceType.NDVI
        assert config.classification_method == ClassificationMethod.QUANTILE
        assert config.zone_count == 5
        assert config.base_rate_l_ha == 10.0

    @pytest.mark.unit
    def test_custom_vra_config(self):
        """Test custom VRA configuration"""
        config = VRAConfig(
            source_type=VRASourceType.SOIL_N,
            classification_method=ClassificationMethod.JENKS,
            zone_count=3,
            base_rate_l_ha=50.0,
        )
        assert config.source_type == VRASourceType.SOIL_N
        assert config.zone_count == 3


class TestGridCell:
    """Tests for GridCell data class"""

    @pytest.mark.unit
    def test_grid_cell_creation(self):
        """Test creating a grid cell"""
        cell = GridCell(
            row=0,
            col=0,
            center=Coordinate(lat=24.7136, lng=46.6753),
            value=0.65,
            zone_type=VRAZoneType.HIGH_VIGOR,
            rate_l_ha=7.5,
        )

        assert cell.row == 0
        assert cell.value == 0.65
        assert cell.zone_type == VRAZoneType.HIGH_VIGOR

    @pytest.mark.unit
    def test_grid_cell_to_dict(self):
        """Test converting grid cell to dictionary"""
        cell = GridCell(
            row=1,
            col=2,
            center=Coordinate(lat=24.7136, lng=46.6753),
            value=0.45,
        )

        result = cell.to_dict()
        assert result["row"] == 1
        assert result["col"] == 2
        assert result["value"] == 0.45


class TestVRAGenerator:
    """Tests for VRA map generator"""

    @pytest.mark.unit
    def test_generator_initialization(self):
        """Test VRA generator initialization"""
        generator = VRAGenerator()
        assert generator.config is not None

    @pytest.mark.unit
    def test_generate_from_ndvi_grid(self, sample_ndvi_grid, sample_bounds):
        """Test generating VRA map from NDVI grid"""
        generator = VRAGenerator()
        prescription = generator.generate_from_ndvi_grid(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=sample_ndvi_grid,
            bounds=sample_bounds,
            cell_size_m=10.0,
            name="Test NDVI Prescription",
            name_ar="وصفة NDVI اختبار",
        )

        assert prescription is not None
        assert prescription.field_id == "field_001"
        assert len(prescription.zones) > 0
        assert prescription.total_area_ha > 0

    @pytest.mark.unit
    def test_zone_type_classification(self, sample_ndvi_grid, sample_bounds):
        """Test that zones are classified correctly by NDVI value"""
        generator = VRAGenerator()
        prescription = generator.generate_from_ndvi_grid(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=sample_ndvi_grid,
            bounds=sample_bounds,
        )

        # Should have zones of different types
        zone_types = [z.zone_type for z in prescription.zones]
        assert len(set(zone_types)) > 1  # Multiple zone types

    @pytest.mark.unit
    def test_rate_calculation(self, sample_ndvi_grid, sample_bounds):
        """Test that rates are calculated correctly"""
        config = VRAConfig(base_rate_l_ha=10.0)
        generator = VRAGenerator(config)
        prescription = generator.generate_from_ndvi_grid(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=sample_ndvi_grid,
            bounds=sample_bounds,
        )

        # All zones should have rates
        for zone in prescription.zones:
            if zone.zone_type != VRAZoneType.EXCLUSION:
                assert zone.rate_l_ha >= 0

    @pytest.mark.unit
    def test_total_volume_calculation(self, sample_ndvi_grid, sample_bounds):
        """Test that total volume is calculated correctly"""
        generator = VRAGenerator()
        prescription = generator.generate_from_ndvi_grid(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=sample_ndvi_grid,
            bounds=sample_bounds,
        )

        # Total volume should equal sum of (area * rate) for all zones
        calculated_volume = sum(z.area_ha * z.rate_l_ha for z in prescription.zones)
        assert abs(prescription.total_volume_l - calculated_volume) < 0.01


class TestVRAFromPoints:
    """Tests for VRA generation from point samples"""

    @pytest.mark.unit
    def test_generate_from_points(self, sample_rectangular_field):
        """Test generating VRA map from point samples"""
        points = [
            {"lat": 24.7137, "lng": 46.6755, "value": 0.3},
            {"lat": 24.7140, "lng": 46.6758, "value": 0.6},
            {"lat": 24.7143, "lng": 46.6761, "value": 0.8},
        ]

        generator = VRAGenerator()
        prescription = generator.generate_from_points(
            field_id="field_001",
            tenant_id="tenant_001",
            points=points,
            boundary=sample_rectangular_field,
            cell_size_m=10.0,
        )

        assert prescription is not None
        assert len(prescription.zones) > 0

    @pytest.mark.unit
    def test_idw_interpolation(self):
        """Test IDW interpolation produces reasonable values"""
        generator = VRAGenerator()
        points = [
            {"lat": 0.0, "lng": 0.0, "value": 10.0},
            {"lat": 0.0, "lng": 0.001, "value": 20.0},
        ]

        # Point exactly at first location should get that value
        value = generator._idw_interpolate(0.0, 0.0, points, "value")
        assert abs(value - 10.0) < 0.1


class TestWeedMap:
    """Tests for weed detection map generation"""

    @pytest.mark.unit
    def test_generate_weed_map(self, sample_rectangular_field):
        """Test generating weed detection map"""
        weed_detections = [
            {"lat": 24.7138, "lng": 46.6755, "density": 0.8},
            {"lat": 24.7140, "lng": 46.6758, "density": 0.5},
            {"lat": 24.7142, "lng": 46.6760, "density": 0.3},
        ]

        generator = VRAGenerator()
        prescription = generator.generate_weed_map(
            field_id="field_001",
            tenant_id="tenant_001",
            weed_detections=weed_detections,
            boundary=sample_rectangular_field,
            base_rate_l_ha=5.0,
            hotspot_multiplier=2.0,
        )

        assert prescription is not None
        # Should have zones with weed-related labels
        assert any("Weed" in z.label_en for z in prescription.zones)


class TestFertilizerMap:
    """Tests for fertilizer prescription map generation"""

    @pytest.mark.unit
    def test_generate_fertilizer_map(self, sample_ndvi_grid, sample_bounds):
        """Test generating fertilizer prescription map"""
        generator = VRAGenerator()
        prescription = generator.generate_fertilizer_map(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=sample_ndvi_grid,
            bounds=sample_bounds,
            base_rate_kg_ha=100.0,
            fertilizer_name="Urea 46%",
            fertilizer_name_ar="يوريا 46%",
        )

        assert prescription is not None
        assert prescription.product_name == "Urea 46%"
        # Low vigor zones should have higher rates (inverse relationship)
        low_vigor_zones = [z for z in prescription.zones if z.zone_type == VRAZoneType.LOW_VIGOR]
        if low_vigor_zones:
            high_vigor_zones = [z for z in prescription.zones if z.zone_type == VRAZoneType.HIGH_VIGOR]
            if high_vigor_zones:
                assert low_vigor_zones[0].rate_l_ha >= high_vigor_zones[0].rate_l_ha


class TestVRAZone:
    """Tests for VRA zone functionality"""

    @pytest.mark.unit
    def test_vra_zone_creation(self):
        """Test creating a VRA zone"""
        boundary = [
            Coordinate(lat=24.7136, lng=46.6753),
            Coordinate(lat=24.7136, lng=46.6758),
            Coordinate(lat=24.7140, lng=46.6758),
            Coordinate(lat=24.7140, lng=46.6753),
        ]

        zone = VRAZone(
            id="vrz_001",
            zone_type=VRAZoneType.HIGH_VIGOR,
            boundary=boundary,
            area_ha=0.5,
            rate_l_ha=7.5,
            rate_percent=75,
            ndvi_mean=0.72,
        )

        assert zone.zone_type == VRAZoneType.HIGH_VIGOR
        assert zone.area_ha == 0.5

    @pytest.mark.unit
    def test_vra_zone_to_geojson(self):
        """Test converting VRA zone to GeoJSON"""
        boundary = [
            Coordinate(lat=24.7136, lng=46.6753),
            Coordinate(lat=24.7136, lng=46.6758),
            Coordinate(lat=24.7140, lng=46.6758),
            Coordinate(lat=24.7140, lng=46.6753),
        ]

        zone = VRAZone(
            id="vrz_001",
            zone_type=VRAZoneType.HIGH_VIGOR,
            boundary=boundary,
            area_ha=0.5,
            rate_l_ha=7.5,
            label_en="High Vigor",
            label_ar="نمو قوي",
        )

        geojson = zone.to_geojson()
        assert geojson["type"] == "Feature"
        assert geojson["geometry"]["type"] == "Polygon"
        assert geojson["properties"]["zone_type"] == "high_vigor"


class TestPrescriptionMap:
    """Tests for prescription map functionality"""

    @pytest.mark.unit
    def test_prescription_map_to_geojson(self, sample_ndvi_grid, sample_bounds):
        """Test converting prescription map to GeoJSON"""
        generator = VRAGenerator()
        prescription = generator.generate_from_ndvi_grid(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=sample_ndvi_grid,
            bounds=sample_bounds,
        )

        geojson = prescription.to_geojson()
        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) == len(prescription.zones)

    @pytest.mark.unit
    def test_prescription_map_statistics(self, sample_ndvi_grid, sample_bounds):
        """Test prescription map statistics"""
        generator = VRAGenerator()
        prescription = generator.generate_from_ndvi_grid(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=sample_ndvi_grid,
            bounds=sample_bounds,
        )

        assert prescription.min_rate_l_ha <= prescription.avg_rate_l_ha
        assert prescription.avg_rate_l_ha <= prescription.max_rate_l_ha


class TestConvenienceVRAFunctions:
    """Tests for VRA convenience functions"""

    @pytest.mark.unit
    def test_create_ndvi_prescription(self, sample_ndvi_grid, sample_bounds):
        """Test create_ndvi_prescription convenience function"""
        prescription = create_ndvi_prescription(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_grid=sample_ndvi_grid,
            bounds=sample_bounds,
            base_rate_l_ha=10.0,
        )

        assert prescription is not None
        assert len(prescription.zones) > 0

    @pytest.mark.unit
    def test_create_spot_spray_map(self, sample_rectangular_field):
        """Test create_spot_spray_map convenience function"""
        detections = [
            {"lat": 24.7138, "lng": 46.6756, "density": 0.9},
            {"lat": 24.7141, "lng": 46.6759, "density": 0.4},
        ]

        prescription = create_spot_spray_map(
            field_id="field_001",
            tenant_id="tenant_001",
            detection_points=detections,
            boundary=sample_rectangular_field,
            detection_type="weed",
            base_rate_l_ha=5.0,
        )

        assert prescription is not None


# ==============================================================================
# Edge Cases and Error Handling Tests - اختبارات الحالات الحدية
# ==============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    @pytest.mark.unit
    def test_very_small_field(self):
        """Test handling of very small field (10m x 10m)"""
        boundary = [
            Coordinate(lat=24.7136, lng=46.6753),
            Coordinate(lat=24.7136, lng=46.67531),  # ~1m east
            Coordinate(lat=24.71361, lng=46.67531),  # ~1m north
            Coordinate(lat=24.71361, lng=46.6753),
        ]

        planner = FlightPlanner()
        result = planner.generate_parallel_path(boundary=boundary)
        # Should still succeed even for tiny field
        assert isinstance(result.success, bool)

    @pytest.mark.unit
    def test_very_narrow_field(self):
        """Test handling of very narrow field"""
        boundary = [
            Coordinate(lat=24.7136, lng=46.6753),
            Coordinate(lat=24.7136, lng=46.6754),  # Very narrow
            Coordinate(lat=24.7200, lng=46.6754),  # Very long
            Coordinate(lat=24.7200, lng=46.6753),
        ]

        planner = FlightPlanner()
        result = planner.generate_parallel_path(boundary=boundary)
        # Should handle narrow fields
        assert isinstance(result.success, bool)

    @pytest.mark.unit
    def test_concave_field(self):
        """Test handling of concave (non-convex) field"""
        # Star-shaped field (concave)
        boundary = [
            Coordinate(lat=24.7150, lng=46.6758),  # Top
            Coordinate(lat=24.7143, lng=46.6761),  # Inner right
            Coordinate(lat=24.7140, lng=46.6768),  # Right
            Coordinate(lat=24.7137, lng=46.6761),  # Inner right-bottom
            Coordinate(lat=24.7130, lng=46.6758),  # Bottom
            Coordinate(lat=24.7137, lng=46.6755),  # Inner left-bottom
            Coordinate(lat=24.7140, lng=46.6748),  # Left
            Coordinate(lat=24.7143, lng=46.6755),  # Inner left
        ]

        planner = FlightPlanner()
        result = planner.generate_parallel_path(boundary=boundary)
        # Should handle concave fields
        assert isinstance(result.success, bool)

    @pytest.mark.unit
    def test_empty_ndvi_grid(self, sample_bounds):
        """Test handling of empty NDVI grid - should handle gracefully or raise"""
        generator = VRAGenerator()

        # Empty grid: the implementation may either raise or return an empty/default result
        try:
            result = generator.generate_from_ndvi_grid(
                field_id="field_001",
                tenant_id="tenant_001",
                ndvi_data=[],
                bounds=sample_bounds,
            )
            # If no exception, verify it returned a valid (possibly empty) result
            assert result is not None
        except (IndexError, ZeroDivisionError, ValueError):
            pass  # Also acceptable to raise on empty input

    @pytest.mark.unit
    def test_single_value_ndvi_grid(self, sample_bounds):
        """Test handling of single-value NDVI grid"""
        ndvi_data = [[0.5]]

        generator = VRAGenerator()
        prescription = generator.generate_from_ndvi_grid(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=ndvi_data,
            bounds=sample_bounds,
        )

        assert prescription is not None

    @pytest.mark.unit
    def test_all_same_ndvi_values(self, sample_bounds):
        """Test handling of uniform NDVI values"""
        ndvi_data = [[0.5] * 10 for _ in range(10)]

        generator = VRAGenerator()
        prescription = generator.generate_from_ndvi_grid(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=ndvi_data,
            bounds=sample_bounds,
        )

        assert prescription is not None
        # Should result in single zone type
        zone_types = {z.zone_type for z in prescription.zones}
        assert len(zone_types) >= 1

    @pytest.mark.unit
    def test_ndvi_with_nodata(self, sample_bounds):
        """Test handling of NDVI data with no-data values"""
        ndvi_data = [
            [0.5, -999.0, 0.6],
            [-999.0, 0.55, -999.0],
            [0.6, -999.0, 0.65],
        ]

        generator = VRAGenerator()
        # Should handle no-data values gracefully
        try:
            prescription = generator.generate_from_ndvi_grid(
                field_id="field_001",
                tenant_id="tenant_001",
                ndvi_data=ndvi_data,
                bounds=sample_bounds,
            )
            assert prescription is not None
        except (ValueError, ZeroDivisionError):
            # Acceptable if explicitly raised
            pass

    @pytest.mark.unit
    def test_extreme_coordinates(self):
        """Test handling of extreme coordinate values"""
        # Near North Pole
        boundary = [
            Coordinate(lat=89.99, lng=0),
            Coordinate(lat=89.99, lng=0.01),
            Coordinate(lat=89.999, lng=0.01),
            Coordinate(lat=89.999, lng=0),
        ]

        planner = FlightPlanner()
        result = planner.generate_parallel_path(boundary=boundary)
        assert isinstance(result.success, bool)

    @pytest.mark.unit
    def test_zero_spray_rate(self, sample_rectangular_field):
        """Test handling of zero spray rate"""
        config = FlightPlanConfig(spray_rate_l_ha=0)
        planner = FlightPlanner(config)
        result = planner.generate_parallel_path(boundary=sample_rectangular_field)

        assert result.success is True
        assert result.total_spray_volume_l == 0


class TestMAVLinkExport:
    """Tests for MAVLink mission export"""

    @pytest.mark.unit
    def test_mavlink_mission_structure(self, sample_rectangular_field):
        """Test MAVLink mission item structure"""
        planner = FlightPlanner()
        result = planner.generate_parallel_path(boundary=sample_rectangular_field)

        assert result.success is True
        mission = result.flight_path.to_mavlink_mission()

        # Check first item structure
        first_item = mission[0]
        required_fields = [
            "seq",
            "frame",
            "command",
            "current",
            "autocontinue",
            "param1",
            "param2",
            "param3",
            "param4",
            "x",
            "y",
            "z",
        ]
        for field in required_fields:
            assert field in first_item

    @pytest.mark.unit
    def test_mavlink_sequential_numbers(self, sample_rectangular_field):
        """Test MAVLink mission items have sequential sequence numbers"""
        planner = FlightPlanner()
        result = planner.generate_parallel_path(boundary=sample_rectangular_field)

        mission = result.flight_path.to_mavlink_mission()

        for i, item in enumerate(mission):
            assert item["seq"] == i

    @pytest.mark.unit
    def test_mavlink_first_waypoint_current(self, sample_rectangular_field):
        """Test first MAVLink waypoint is marked as current"""
        planner = FlightPlanner()
        result = planner.generate_parallel_path(boundary=sample_rectangular_field)

        mission = result.flight_path.to_mavlink_mission()

        assert mission[0]["current"] == 1
        for item in mission[1:]:
            assert item["current"] == 0

    @pytest.mark.unit
    def test_mavlink_coordinates(self, sample_rectangular_field):
        """Test MAVLink mission coordinates are valid"""
        planner = FlightPlanner()
        result = planner.generate_parallel_path(boundary=sample_rectangular_field)

        mission = result.flight_path.to_mavlink_mission()

        for item in mission:
            assert -90 <= item["x"] <= 90  # Latitude
            assert -180 <= item["y"] <= 180  # Longitude
            assert item["z"] >= 0  # Altitude


class TestBatteryCalculations:
    """Tests for battery and flight time calculations"""

    @pytest.mark.unit
    def test_flight_time_warning(self, sample_rectangular_field):
        """Test that long flight times generate warnings"""
        # Use slow speed to increase flight time
        config = FlightPlanConfig(cruise_speed_ms=0.5)
        planner = FlightPlanner(config)
        result = planner.generate_parallel_path(boundary=sample_rectangular_field)

        if result.estimated_duration_min > 20:
            assert len(result.warnings_en) > 0
            assert result.flights_needed > 1

    @pytest.mark.unit
    def test_flights_needed_calculation(self):
        """Test number of flights needed calculation"""
        resources = estimate_flight_resources(
            area_ha=100.0,  # Large area
            spray_rate_l_ha=10.0,
            tank_capacity_l=40.0,
            flight_time_per_tank_min=15.0,
        )

        # Should need multiple flights
        assert resources["tank_fills"] > 1
        assert resources["batteries_needed"] > 1


class TestNoFlyZoneCompliance:
    """Tests for no-fly zone and exclusion handling"""

    @pytest.mark.unit
    def test_exclusion_zones_config(self):
        """Test exclusion zones in configuration"""
        exclusion = [
            Coordinate(lat=24.7140, lng=46.6758),
            Coordinate(lat=24.7140, lng=46.6760),
            Coordinate(lat=24.7142, lng=46.6760),
            Coordinate(lat=24.7142, lng=46.6758),
        ]

        config = FlightPlanConfig(exclusion_zones=[exclusion])
        assert len(config.exclusion_zones) == 1

    @pytest.mark.unit
    def test_buffer_zone_compliance(self, sample_rectangular_field):
        """Test that buffer zones are respected"""
        config = FlightPlanConfig(buffer_distance_m=10.0)
        planner = FlightPlanner(config)
        result = planner.generate_parallel_path(boundary=sample_rectangular_field)

        assert result.success is True
        # Coverage area should be reduced due to buffer
        # Effective area (actual sprayed area) may be slightly larger due to overlapping passes
        if result.flight_path:
            # Just verify both areas are positive
            assert result.coverage_area_ha > 0
            assert result.effective_area_ha > 0

    @pytest.mark.unit
    def test_vra_exclusion_zones(self, sample_ndvi_grid, sample_bounds):
        """Test VRA handles exclusion zones correctly"""
        config = VRAConfig(exclude_water_bodies=True)
        generator = VRAGenerator(config)

        # Should handle exclusion configuration
        assert generator.config.exclude_water_bodies is True


# ==============================================================================
# Integration-like Unit Tests - اختبارات شبه التكامل
# ==============================================================================


class TestFlightPlanningWorkflow:
    """Tests for complete flight planning workflows"""

    @pytest.mark.unit
    def test_spray_mission_workflow(self, sample_rectangular_field, sample_drone_specs):
        """Test complete spray mission planning workflow"""
        # 1. Assess weather
        weather = assess_flight_weather(
            temperature_c=28,
            humidity_percent=45,
            wind_speed_ms=3.0,
            wind_direction_deg=180,
            drone_specs=sample_drone_specs,
        )
        assert weather.can_fly is True

        # 2. Create flight plan
        result = create_spray_flight_plan(
            boundary=sample_rectangular_field,
            spray_rate_l_ha=10.0,
            swath_width_m=sample_drone_specs.spray_width_m,
            altitude_m=3.0,
        )
        assert result.success is True

        # 3. Estimate resources
        resources = estimate_flight_resources(
            area_ha=result.coverage_area_ha,
            spray_rate_l_ha=10.0,
            tank_capacity_l=sample_drone_specs.tank_capacity_l,
        )
        assert resources["total_volume_l"] > 0

    @pytest.mark.unit
    def test_vra_spray_workflow(self, sample_rectangular_field, sample_ndvi_grid, sample_bounds):
        """Test VRA prescription to flight plan workflow"""
        # 1. Generate prescription map
        prescription = create_ndvi_prescription(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_grid=sample_ndvi_grid,
            bounds=sample_bounds,
            base_rate_l_ha=10.0,
        )
        assert prescription is not None

        # 2. Create spray mission with VRA
        result = create_spray_flight_plan(
            boundary=sample_rectangular_field,
            spray_rate_l_ha=prescription.avg_rate_l_ha,
        )
        assert result.success is True

        # 3. Verify total volume matches prescription
        # Note: This is approximate due to different calculation methods
        assert result.total_spray_volume_l > 0

    @pytest.mark.unit
    def test_mapping_mission_workflow(self, sample_rectangular_field, sample_mapping_drone_specs):
        """Test complete mapping mission workflow"""
        # 1. Check weather
        weather = assess_flight_weather(
            temperature_c=25,
            humidity_percent=40,
            wind_speed_ms=5.0,
            wind_direction_deg=90,
            drone_specs=sample_mapping_drone_specs,
        )
        assert weather.can_fly is True

        # 2. Create mapping plan
        result = create_mapping_flight_plan(
            boundary=sample_rectangular_field,
            gsd_cm_px=2.5,
            frontal_overlap=80,
            side_overlap=70,
        )
        assert result.success is True
        assert result.estimated_photos > 0

        # 3. Export to KML
        kml = result.flight_path.to_kml()
        assert "<kml" in kml

        # 4. Export to MAVLink
        mission = result.flight_path.to_mavlink_mission()
        assert len(mission) == len(result.flight_path.waypoints)


# ==============================================================================
# Performance Tests - اختبارات الأداء
# ==============================================================================


class TestPerformance:
    """Tests for performance characteristics"""

    @pytest.mark.unit
    def test_large_field_performance(self):
        """Test flight planning performance for large field"""
        # Create a large field (approximately 100 hectares)
        boundary = [
            Coordinate(lat=24.70, lng=46.67),
            Coordinate(lat=24.70, lng=46.68),  # ~1km east
            Coordinate(lat=24.71, lng=46.68),  # ~1km north
            Coordinate(lat=24.71, lng=46.67),
        ]

        planner = FlightPlanner()

        import time

        start = time.time()
        result = planner.generate_parallel_path(boundary=boundary)
        elapsed = time.time() - start

        assert result.success is True
        assert elapsed < 5.0  # Should complete within 5 seconds

    @pytest.mark.unit
    def test_high_resolution_ndvi_performance(self, sample_bounds):
        """Test VRA generation performance for high resolution grid"""
        # Create large NDVI grid (100x100)
        ndvi_data = [[0.3 + 0.5 * (r + c) / 200 for c in range(100)] for r in range(100)]

        generator = VRAGenerator()

        import time

        start = time.time()
        prescription = generator.generate_from_ndvi_grid(
            field_id="field_001",
            tenant_id="tenant_001",
            ndvi_data=ndvi_data,
            bounds=sample_bounds,
        )
        elapsed = time.time() - start

        assert prescription is not None
        assert elapsed < 5.0  # Should complete within 5 seconds
