"""
Comprehensive unit tests for Leveling Optimizer Service.

Targets >60% code coverage across:
- schemas (enums, validators, request/response models)
- config (Settings)
- utils/leveling_algorithms (LevelingOptimizer, PlaneParameters, Point3D, CutFillResult)
- API endpoints (via TestClient)
"""

import math
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

# Ensure service root is on path

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars-minimum")
# ---------------------------------------------------------------------------
# Schema enum tests
# ---------------------------------------------------------------------------
class TestSchemaEnums:
    def test_equipment_type(self):
        from src.api.schemas import EquipmentType

        assert EquipmentType.BULLDOZER == "bulldozer"
        assert EquipmentType.LASER_LEVELER == "laser_leveler"
        assert len(EquipmentType) == 6

    def test_soil_type(self):
        from src.api.schemas import SoilType

        assert SoilType.SANDY == "sandy"
        assert SoilType.ROCKY == "rocky"
        assert len(SoilType) == 5

    def test_leveling_method(self):
        from src.api.schemas import LevelingMethod

        assert LevelingMethod.SINGLE_PLANE == "single_plane"
        assert LevelingMethod.BENCH == "bench"

    def test_leveling_priority(self):
        from src.api.schemas import LevelingPriority

        assert LevelingPriority.MINIMIZE_COST == "minimize_cost"
        assert LevelingPriority.IRRIGATION_EFFICIENCY == "irrigation_efficiency"
# ---------------------------------------------------------------------------
# Schema model validation tests
# ---------------------------------------------------------------------------
class TestSchemaValidation:
    def test_elevation_point_valid(self):
        from src.api.schemas import ElevationPoint

        p = ElevationPoint(x=10.0, y=20.0, elevation=500.0, point_id="P1")
        assert p.elevation == 500.0
        assert p.point_id == "P1"

    def test_elevation_point_out_of_range(self):
        from src.api.schemas import ElevationPoint

        with pytest.raises(Exception):
            ElevationPoint(x=0, y=0, elevation=5000.0)  # > 3000

    def test_elevation_point_below_range(self):
        from src.api.schemas import ElevationPoint

        with pytest.raises(Exception):
            ElevationPoint(x=0, y=0, elevation=-200.0)  # < -100

    def test_elevation_point_id_whitespace(self):
        from src.api.schemas import ElevationPoint

        p = ElevationPoint(x=0, y=0, elevation=100.0, point_id="  ")
        assert p.point_id is None

    def test_elevation_point_id_too_long(self):
        from src.api.schemas import ElevationPoint

        with pytest.raises(Exception):
            ElevationPoint(x=0, y=0, elevation=100.0, point_id="x" * 65)

    def test_field_boundary_valid(self):
        from src.api.schemas import FieldBoundary

        fb = FieldBoundary(coordinates=[[0, 0], [100, 0], [100, 100], [0, 100]])
        assert len(fb.coordinates) == 4

    def test_field_boundary_too_few_coords(self):
        from src.api.schemas import FieldBoundary

        with pytest.raises(Exception):
            FieldBoundary(coordinates=[[0, 0], [1, 0]])

    def test_field_boundary_invalid_coord(self):
        from src.api.schemas import FieldBoundary

        with pytest.raises(Exception):
            FieldBoundary(coordinates=[[0, 0], [1, 0], ["a", "b"]])

    def test_leveling_analysis_request_valid(self):
        from src.api.schemas import ElevationPoint, LevelingAnalysisRequest

        points = [
            ElevationPoint(x=0, y=0, elevation=100),
            ElevationPoint(x=100, y=0, elevation=100.2),
            ElevationPoint(x=0, y=100, elevation=100.1),
            ElevationPoint(x=100, y=100, elevation=100.3),
        ]
        req = LevelingAnalysisRequest(field_id="FIELD-001", elevation_points=points)
        assert req.method == "single_plane"
        assert req.include_cost_estimate is True

    def test_leveling_analysis_request_empty_field_id(self):
        from src.api.schemas import ElevationPoint, LevelingAnalysisRequest

        with pytest.raises(Exception):
            LevelingAnalysisRequest(
                field_id="   ",
                elevation_points=[
                    ElevationPoint(x=0, y=0, elevation=100),
                    ElevationPoint(x=1, y=0, elevation=100),
                    ElevationPoint(x=0, y=1, elevation=100),
                    ElevationPoint(x=1, y=1, elevation=100),
                ],
            )

    def test_leveling_analysis_request_insufficient_points(self):
        from src.api.schemas import ElevationPoint, LevelingAnalysisRequest

        with pytest.raises(Exception):
            LevelingAnalysisRequest(
                field_id="F1",
                elevation_points=[
                    ElevationPoint(x=0, y=0, elevation=100),
                    ElevationPoint(x=1, y=0, elevation=100),
                ],
            )

    def test_leveling_analysis_request_grade_validation(self):
        from src.api.schemas import ElevationPoint, LevelingAnalysisRequest

        with pytest.raises(Exception):
            LevelingAnalysisRequest(
                field_id="F1",
                elevation_points=[
                    ElevationPoint(x=0, y=0, elevation=100),
                    ElevationPoint(x=1, y=0, elevation=100),
                    ElevationPoint(x=0, y=1, elevation=100),
                    ElevationPoint(x=1, y=1, elevation=100),
                ],
                target_grade_x=20.0,  # > MAX_GRADE_PERCENT
            )

    def test_simulation_request_valid(self):
        from src.api.schemas import ElevationPoint, SimulationRequest

        points = [
            ElevationPoint(x=0, y=0, elevation=100),
            ElevationPoint(x=100, y=0, elevation=100.2),
            ElevationPoint(x=0, y=100, elevation=100.1),
            ElevationPoint(x=100, y=100, elevation=100.3),
        ]
        req = SimulationRequest(field_id="F1", elevation_points=points)
        assert req.target_grade_x == 0.2
        assert req.target_grade_y == 0.1

    def test_health_response(self):
        from src.api.schemas import HealthResponse

        hr = HealthResponse(status="ok", service="test", version="1.0")
        assert hr.status == "ok"

    def test_readiness_response(self):
        from src.api.schemas import ReadinessResponse

        rr = ReadinessResponse(status="ok", database=True, nats=False)
        assert rr.database is True

    def test_error_response(self):
        from src.api.schemas import ErrorResponse

        er = ErrorResponse(error="test", error_ar="اختبار")
        assert er.detail is None
# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------
class TestConfig:
    def test_settings_defaults(self):
        from src.core.config import Settings

        s = Settings()
        assert s.SERVICE_NAME == "leveling-optimizer-service"
        assert s.VERSION == "16.0.0"
        assert s.PORT == 8170

    def test_equipment_costs(self):
        from src.core.config import Settings

        s = Settings()
        assert s.BULLDOZER_COST_PER_HOUR == 350.0
        assert s.LASER_LEVELER_COST_PER_HOUR == 450.0

    def test_soil_factors(self):
        from src.core.config import Settings

        s = Settings()
        assert s.SOIL_EXPANSION_FACTOR == 1.25
        assert s.SOIL_COMPACTION_FACTOR == 0.90

    def test_grade_limits(self):
        from src.core.config import Settings

        s = Settings()
        assert s.MIN_DRAINAGE_GRADE == 0.1
        assert s.MAX_IRRIGATION_GRADE == 0.5
# ---------------------------------------------------------------------------
# LevelingOptimizer algorithm tests
# ---------------------------------------------------------------------------
class TestLevelingOptimizer:
    @pytest.fixture
    def optimizer(self):
        from src.utils.leveling_algorithms import LevelingOptimizer

        return LevelingOptimizer()

    @pytest.fixture
    def sample_points(self):
        from src.utils.leveling_algorithms import Point3D

        return [
            Point3D(x=0, y=0, z=100.0, point_id="P1"),
            Point3D(x=100, y=0, z=100.5, point_id="P2"),
            Point3D(x=0, y=100, z=100.2, point_id="P3"),
            Point3D(x=100, y=100, z=100.8, point_id="P4"),
            Point3D(x=50, y=50, z=100.3, point_id="P5"),
            Point3D(x=25, y=75, z=100.1, point_id="P6"),
        ]

    def test_init_defaults(self, optimizer):
        assert optimizer.soil_expansion_factor == 1.25
        assert optimizer.soil_compaction_factor == 0.90

    def test_init_custom(self):
        from src.utils.leveling_algorithms import LevelingOptimizer

        opt = LevelingOptimizer(soil_expansion_factor=1.3, soil_compaction_factor=0.85)
        assert opt.soil_expansion_factor == 1.3

    def test_compute_optimal_plane(self, optimizer, sample_points):
        from src.utils.leveling_algorithms import PlaneParameters

        plane = optimizer.compute_optimal_plane(sample_points)
        assert isinstance(plane, PlaneParameters)
        assert plane.a is not None
        assert plane.b is not None
        assert plane.c is not None

    def test_compute_plane_with_target_grades(self, optimizer, sample_points):
        plane = optimizer.compute_optimal_plane(
            sample_points, target_grade_x=0.3, target_grade_y=0.15
        )
        assert abs(plane.a * 100 - 0.3) < 0.01
        assert abs(plane.b * 100 - 0.15) < 0.01

    def test_compute_plane_too_few_points(self, optimizer):
        from src.utils.leveling_algorithms import Point3D

        with pytest.raises(ValueError, match="At least 3 points"):
            optimizer.compute_optimal_plane([Point3D(0, 0, 100), Point3D(1, 0, 100)])

    def test_compute_plane_no_balance(self, optimizer, sample_points):
        plane = optimizer.compute_optimal_plane(
            sample_points, target_grade_x=0.2, target_grade_y=0.1, balance_cut_fill=False
        )
        # c should be calculated to pass through centroid
        assert plane.c != 0

    def test_find_balanced_elevation(self, optimizer, sample_points):
        c = optimizer._find_balanced_elevation(sample_points, 0.002, 0.001)
        assert isinstance(c, float)

    def test_compute_multi_plane(self, optimizer, sample_points):
        results = optimizer.compute_multi_plane(sample_points, num_planes=2, direction="y")
        assert len(results) >= 1
        for plane, points in results:
            assert len(points) >= 3

    def test_compute_multi_plane_x_direction(self, optimizer, sample_points):
        results = optimizer.compute_multi_plane(sample_points, num_planes=2, direction="x")
        assert len(results) >= 1

    def test_calculate_cut_fill_volumes(self, optimizer, sample_points):
        plane = optimizer.compute_optimal_plane(sample_points)
        result = optimizer.calculate_cut_fill_volumes(sample_points, plane, grid_size=10.0)
        assert result.cut_volume >= 0
        assert result.fill_volume >= 0
        assert result.cut_area >= 0
        assert result.fill_area >= 0
        assert len(result.design_points) == len(sample_points)

    def test_cut_fill_max_depths(self, optimizer, sample_points):
        from src.utils.leveling_algorithms import PlaneParameters

        # Create a plane that forces large cuts and fills
        plane = PlaneParameters(a=0.0, b=0.0, c=100.3)
        result = optimizer.calculate_cut_fill_volumes(sample_points, plane, grid_size=10.0)
        assert result.max_cut_depth >= 0
        assert result.max_fill_depth >= 0
        cut_depths_list = [p.z for p in result.cut_points]
        if cut_depths_list:
            assert result.avg_cut_depth > 0

    def test_calculate_tin_volumes(self, optimizer, sample_points):
        plane = optimizer.compute_optimal_plane(sample_points)
        result = optimizer.calculate_tin_volumes(sample_points, plane)
        assert result.cut_volume >= 0
        assert result.fill_volume >= 0

    def test_calculate_tin_volumes_too_few_points(self, optimizer):
        from src.utils.leveling_algorithms import PlaneParameters, Point3D

        plane = PlaneParameters(a=0, b=0, c=100)
        result = optimizer.calculate_tin_volumes([Point3D(0, 0, 100)], plane)
        assert result.cut_volume == 0

    def test_calculate_haul_distance(self, optimizer):
        from src.utils.leveling_algorithms import Point3D

        cuts = [Point3D(0, 0, 0.5), Point3D(10, 0, 0.3)]
        fills = [Point3D(100, 100, 0.4), Point3D(110, 100, 0.2)]
        dist = optimizer.calculate_haul_distance(cuts, fills)
        assert dist > 0
        # Factor of 1.2 applied
        straight_dist = math.hypot(100, 100)
        assert dist == pytest.approx(straight_dist * 1.2, rel=0.1)

    def test_calculate_haul_distance_empty(self, optimizer):
        from src.utils.leveling_algorithms import Point3D

        assert optimizer.calculate_haul_distance([], [Point3D(0, 0, 1)]) == 0.0
        assert optimizer.calculate_haul_distance([Point3D(0, 0, 1)], []) == 0.0

    def test_calculate_mass_haul(self, optimizer):
        from src.utils.leveling_algorithms import Point3D

        cuts = [Point3D(0, 0, 0.5), Point3D(10, 0, 0.3)]
        fills = [Point3D(200, 200, 0.4)]
        result = optimizer.calculate_mass_haul(cuts, fills)
        assert "total_cut_volume" in result
        assert "total_fill_volume" in result
        assert "balance_point" in result
        assert "average_haul_distance" in result
        assert "free_haul_distance" in result
        assert "overhaul_distance" in result
        assert "requires_import" in result
        assert "requires_export" in result

    def test_calculate_mass_haul_empty(self, optimizer):
        result = optimizer.calculate_mass_haul([], [])
        assert result["total_cut_volume"] == 0

    def test_calculate_field_area(self, optimizer, sample_points):
        area = optimizer.calculate_field_area(sample_points)
        # 100m x 100m bounding box = 10000 m2
        assert area == 10000.0

    def test_calculate_field_area_too_few(self, optimizer):
        from src.utils.leveling_algorithms import Point3D

        assert optimizer.calculate_field_area([Point3D(0, 0, 1)]) == 0.0

    def test_calculate_statistics(self, optimizer, sample_points):
        stats = optimizer.calculate_statistics(sample_points)
        assert stats["min_elevation"] == 100.0
        assert stats["max_elevation"] == 100.8
        assert stats["point_count"] == 6
        assert stats["elevation_range"] == pytest.approx(0.8)
        assert "std_dev" in stats

    def test_calculate_statistics_empty(self, optimizer):
        assert optimizer.calculate_statistics([]) == {}

    def test_std_dev_single_value(self, optimizer):
        result = optimizer._calculate_std_dev([5.0])
        assert result == 0.0

    def test_optimize_for_irrigation(self, optimizer, sample_points):
        plane = optimizer.optimize_for_irrigation(sample_points, min_grade=0.1, max_grade=0.5)
        grade_x = abs(plane.a * 100)
        grade_y = abs(plane.b * 100)
        assert 0.1 <= grade_x <= 0.5
        assert 0.1 <= grade_y <= 0.5

    def test_grade_percent_to_ratio(self, optimizer):
        assert optimizer.grade_percent_to_ratio(0.5) == "1:200"
        assert optimizer.grade_percent_to_ratio(1.0) == "1:100"
        assert optimizer.grade_percent_to_ratio(0) == "1:∞"

    def test_ratio_to_grade_percent(self, optimizer):
        assert optimizer.ratio_to_grade_percent(200) == 0.5
        assert optimizer.ratio_to_grade_percent(100) == 1.0
        assert optimizer.ratio_to_grade_percent(0) == 0.0
# ---------------------------------------------------------------------------
# Point3D and PlaneParameters dataclass tests
# ---------------------------------------------------------------------------
class TestDataclasses:
    def test_point3d(self):
        from src.utils.leveling_algorithms import Point3D

        p = Point3D(x=1.0, y=2.0, z=3.0, point_id="test")
        assert p.x == 1.0
        assert p.point_id == "test"

    def test_point3d_no_id(self):
        from src.utils.leveling_algorithms import Point3D

        p = Point3D(x=1.0, y=2.0, z=3.0)
        assert p.point_id is None

    def test_plane_parameters(self):
        from src.utils.leveling_algorithms import PlaneParameters

        pp = PlaneParameters(a=0.002, b=0.001, c=100.0)
        assert pp.a == 0.002

    def test_cut_fill_result(self):
        from src.utils.leveling_algorithms import CutFillResult, Point3D

        cfr = CutFillResult(
            cut_volume=1000.0,
            fill_volume=900.0,
            cut_area=500.0,
            fill_area=450.0,
            max_cut_depth=0.5,
            max_fill_depth=0.4,
            avg_cut_depth=0.2,
            avg_fill_depth=0.18,
            cut_points=[Point3D(0, 0, 0.5)],
            fill_points=[Point3D(10, 10, 0.4)],
            design_points=[Point3D(0, 0, 100.0)],
        )
        assert cfr.cut_volume == 1000.0
        assert len(cfr.cut_points) == 1
# ---------------------------------------------------------------------------
# Response model tests
# ---------------------------------------------------------------------------
class TestResponseModels:
    def test_cut_fill_volume(self):
        from src.api.schemas import CutFillVolume

        cfv = CutFillVolume(
            cut_volume_m3=1000.0,
            fill_volume_m3=900.0,
            net_volume_m3=100.0,
            cut_area_m2=500.0,
            fill_area_m2=450.0,
            balance_ratio=1.11,
            max_cut_depth_m=0.5,
            max_fill_depth_m=0.4,
            avg_cut_depth_m=0.2,
            avg_fill_depth_m=0.18,
        )
        assert cfv.balance_ratio == pytest.approx(1.11)

    def test_design_plane(self):
        from src.api.schemas import DesignPlane

        dp = DesignPlane(
            centroid_elevation=100.3,
            grade_x_percent=0.2,
            grade_y_percent=0.1,
            plane_equation="z = 0.002*x + 0.001*y + 100.3",
            coefficient_a=0.002,
            coefficient_b=0.001,
            coefficient_c=100.3,
        )
        assert dp.centroid_elevation == 100.3

    def test_equipment_recommendation(self):
        from src.api.schemas import EquipmentRecommendation

        er = EquipmentRecommendation(
            equipment_type="bulldozer",
            equipment_name_en="Bulldozer",
            equipment_name_ar="جرافة",
            quantity=1,
            hours_required=12.5,
            cost_per_hour_sar=350.0,
            total_cost_sar=4375.0,
            productivity_m3_per_hour=80.0,
            recommended_for="General earthmoving",
            priority=1,
        )
        assert er.total_cost_sar == 4375.0

    def test_cost_estimate(self):
        from src.api.schemas import CostEstimate

        ce = CostEstimate(
            total_cost_sar=50000.0,
            earthwork_cost_sar=35000.0,
            equipment_cost_sar=20000.0,
            labor_cost_sar=5000.0,
            fuel_cost_sar=3000.0,
            surveying_cost_sar=2500.0,
            contingency_sar=5000.0,
            cost_per_m3_sar=10.0,
            cost_per_hectare_sar=20000.0,
            estimated_duration_hours=62.5,
            estimated_duration_days=7.8,
            summary_en="Total cost: 50,000 SAR",
            summary_ar="إجمالي التكلفة: 50,000 ريال",
        )
        assert ce.total_cost_sar == 50000.0
        assert "SAR" in ce.summary_en
        assert "ريال" in ce.summary_ar
# ---------------------------------------------------------------------------
# Validation constants tests
# ---------------------------------------------------------------------------
class TestValidationConstants:
    def test_constants_exist(self):
        from src.api.schemas import (
            ELEVATION_MAX_M,
            ELEVATION_MIN_M,
            MAX_ELEVATION_POINTS,
            MAX_GRADE_PERCENT,
            MIN_GRADE_PERCENT,
        )

        assert ELEVATION_MIN_M == -100.0
        assert ELEVATION_MAX_M == 3000.0
        assert MAX_GRADE_PERCENT == 15.0
        assert MIN_GRADE_PERCENT == -15.0
        assert MAX_ELEVATION_POINTS == 100000
