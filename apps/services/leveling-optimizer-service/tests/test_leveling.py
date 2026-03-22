"""
Tests for Leveling Optimizer Service.

اختبارات خدمة تحسين التسوية
"""

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)
from src.main import app
from src.api.endpoints.leveling import get_current_user
from src.utils.leveling_algorithms import (
    LevelingOptimizer,
    PlaneParameters,
    Point3D,
)


def _mock_current_user():
    """Mock user for testing."""
    return {"id": "test-user", "tenant_id": "00000000-0000-0000-0000-000000000001"}


@pytest.fixture
def auth_headers():
    """Headers with tenant and auth for API requests."""
    return {
        "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
        "Authorization": "Bearer test-token-for-unit-tests",
    }


@pytest.fixture
def client():
    """Create test client with auth override."""
    app.dependency_overrides[get_current_user] = _mock_current_user
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


@pytest.fixture
def optimizer():
    """Create leveling optimizer instance."""
    return LevelingOptimizer()


@pytest.fixture
def sample_points():
    """Sample elevation points for testing."""
    return [
        Point3D(x=0, y=0, z=100.0, point_id="P1"),
        Point3D(x=100, y=0, z=100.2, point_id="P2"),
        Point3D(x=0, y=100, z=100.1, point_id="P3"),
        Point3D(x=100, y=100, z=100.4, point_id="P4"),
        Point3D(x=50, y=50, z=100.15, point_id="P5"),
    ]


@pytest.fixture
def sample_elevation_data():
    """Sample elevation data for API testing."""
    return [
        {"x": 0, "y": 0, "elevation": 100.0, "point_id": "P1"},
        {"x": 100, "y": 0, "elevation": 100.2, "point_id": "P2"},
        {"x": 0, "y": 100, "elevation": 100.1, "point_id": "P3"},
        {"x": 100, "y": 100, "elevation": 100.4, "point_id": "P4"},
        {"x": 50, "y": 50, "elevation": 100.15, "point_id": "P5"},
    ]


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_healthz(self, client):
        """Test liveness probe."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "leveling-optimizer-service"
        assert data["version"] == "16.0.0"

    def test_readyz(self, client):
        """Test readiness probe."""
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert "nats" in data

    def test_health(self, client):
        """Test combined health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "components" in data

    def test_root(self, client, auth_headers):
        """Test root endpoint."""
        response = client.get("/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "service_ar" in data
        assert data["documentation"] == "/docs"


class TestLevelingAlgorithms:
    """Test leveling optimization algorithms."""

    def test_compute_optimal_plane(self, optimizer, sample_points):
        """Test optimal plane computation."""
        plane = optimizer.compute_optimal_plane(sample_points)

        assert isinstance(plane, PlaneParameters)
        assert plane.a is not None
        assert plane.b is not None
        assert plane.c is not None

    def test_compute_plane_with_target_grades(self, optimizer, sample_points):
        """Test plane computation with specified target grades."""
        plane = optimizer.compute_optimal_plane(
            sample_points,
            target_grade_x=0.2,
            target_grade_y=0.1,
        )

        # Check grades are close to target (within tolerance)
        assert abs(plane.a * 100 - 0.2) < 0.01
        assert abs(plane.b * 100 - 0.1) < 0.01

    def test_calculate_cut_fill_volumes(self, optimizer, sample_points):
        """Test cut/fill volume calculation."""
        plane = optimizer.compute_optimal_plane(sample_points)
        result = optimizer.calculate_cut_fill_volumes(sample_points, plane)

        assert result.cut_volume >= 0
        assert result.fill_volume >= 0
        assert result.cut_area >= 0
        assert result.fill_area >= 0
        assert len(result.design_points) == len(sample_points)

    def test_calculate_haul_distance(self, optimizer):
        """Test haul distance calculation."""
        cut_points = [Point3D(0, 0, 0.1), Point3D(10, 0, 0.2)]
        fill_points = [Point3D(90, 100, 0.1), Point3D(100, 100, 0.2)]

        distance = optimizer.calculate_haul_distance(cut_points, fill_points)

        assert distance > 0
        # Distance should be roughly sqrt((95-5)^2 + (100-0)^2) * 1.2 factor
        assert distance > 100

    def test_calculate_field_area(self, optimizer, sample_points):
        """Test field area calculation."""
        area = optimizer.calculate_field_area(sample_points)

        # 100m x 100m field = 10000 m²
        assert area == 10000

    def test_calculate_statistics(self, optimizer, sample_points):
        """Test elevation statistics calculation."""
        stats = optimizer.calculate_statistics(sample_points)

        assert stats["min_elevation"] == 100.0
        assert stats["max_elevation"] == 100.4
        assert stats["point_count"] == 5
        assert stats["elevation_range"] == pytest.approx(0.4)
        assert "std_dev" in stats

    def test_optimize_for_irrigation(self, optimizer, sample_points):
        """Test irrigation-optimized plane computation."""
        plane = optimizer.optimize_for_irrigation(
            sample_points,
            min_grade=0.1,
            max_grade=0.5,
        )

        grade_x = abs(plane.a * 100)
        grade_y = abs(plane.b * 100)

        # Grades should be within specified range
        assert grade_x >= 0.1 and grade_x <= 0.5
        assert grade_y >= 0.1 and grade_y <= 0.5

    def test_grade_conversion(self, optimizer):
        """Test grade percentage to ratio conversion."""
        ratio = optimizer.grade_percent_to_ratio(0.5)
        assert ratio == "1:200"

        ratio = optimizer.grade_percent_to_ratio(1.0)
        assert ratio == "1:100"

        percent = optimizer.ratio_to_grade_percent(200)
        assert percent == 0.5


class TestLevelingAPI:
    """Test leveling API endpoints."""

    def test_analyze_field_leveling(self, client, sample_elevation_data, auth_headers):
        """Test field leveling analysis endpoint."""
        request_data = {
            "field_id": "FIELD-001",
            "elevation_points": sample_elevation_data,
            "soil_type": "loamy",
            "method": "single_plane",
            "priority": "minimize_cost",
            "include_cost_estimate": True,
        }

        response = client.post("/api/v1/leveling/analyze", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["field_id"] == "FIELD-001"
        assert "plan" in data

        plan = data["plan"]
        assert "design_plane" in plan
        assert "cut_fill" in plan
        assert "equipment_recommendations" in plan
        assert "cost_estimate" in plan
        assert "summary_en" in plan
        assert "summary_ar" in plan

    def test_analyze_field_with_target_grades(self, client, sample_elevation_data, auth_headers):
        """Test analysis with specified target grades."""
        request_data = {
            "field_id": "FIELD-002",
            "elevation_points": sample_elevation_data,
            "target_grade_x": 0.3,
            "target_grade_y": 0.2,
            "method": "single_plane",
            "priority": "irrigation_efficiency",
        }

        response = client.post("/api/v1/leveling/analyze", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_leveling_plan(self, client, auth_headers):
        """Test get leveling plan endpoint."""
        response = client.get("/api/v1/leveling/plan/FIELD-001", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["field_id"] == "FIELD-001"
        assert "design_plane" in data
        assert "cut_fill" in data

    def test_get_cost_estimation(self, client, auth_headers):
        """Test cost estimation endpoint."""
        response = client.get(
            "/api/v1/leveling/cost/FIELD-001",
            params={
                "cut_volume_m3": 2500,
                "fill_volume_m3": 2300,
                "field_area_hectares": 2.5,
                "haul_distance_m": 100,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert "total_cost_sar" in data
        assert "earthwork_cost_sar" in data
        assert "equipment_cost_sar" in data
        assert "cost_per_m3_sar" in data
        assert "cost_per_hectare_sar" in data
        assert "summary_en" in data
        assert "summary_ar" in data

        # Verify costs are positive
        assert data["total_cost_sar"] > 0
        assert data["cost_per_m3_sar"] > 0

    def test_get_equipment_recommendations(self, client, auth_headers):
        """Test equipment recommendations endpoint."""
        response = client.get(
            "/api/v1/leveling/equipment/FIELD-001",
            params={
                "total_volume_m3": 5000,
                "haul_distance_m": 150,
                "method": "single_plane",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        for equipment in data:
            assert "equipment_type" in equipment
            assert "equipment_name_en" in equipment
            assert "equipment_name_ar" in equipment
            assert "hours_required" in equipment
            assert "cost_per_hour_sar" in equipment
            assert "total_cost_sar" in equipment

    def test_simulate_leveling(self, client, sample_elevation_data, auth_headers):
        """Test leveling simulation endpoint."""
        request_data = {
            "field_id": "FIELD-001",
            "elevation_points": sample_elevation_data,
            "target_grade_x": 0.2,
            "target_grade_y": 0.1,
            "soil_type": "loamy",
            "method": "single_plane",
        }

        response = client.post("/api/v1/leveling/simulate", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["field_id"] == "FIELD-001"
        assert "original_points" in data
        assert "simulated_points" in data
        assert "cut_points" in data
        assert "fill_points" in data
        assert "design_plane" in data
        assert "cut_fill" in data
        assert "uniformity_improvement" in data
        assert "summary_en" in data
        assert "summary_ar" in data

        # Verify simulation results
        assert len(data["simulated_points"]) == len(sample_elevation_data)

    def test_analyze_insufficient_points(self, client, auth_headers):
        """Test analysis with insufficient elevation points."""
        request_data = {
            "field_id": "FIELD-001",
            "elevation_points": [
                {"x": 0, "y": 0, "elevation": 100.0},
                {"x": 100, "y": 0, "elevation": 100.2},
            ],
            "method": "single_plane",
        }

        response = client.post("/api/v1/leveling/analyze", json=request_data, headers=auth_headers)

        # Should fail validation (min_length=4)
        assert response.status_code == 422


class TestBilingualOutput:
    """Test bilingual (Arabic/English) output."""

    def test_bilingual_cost_estimate(self, client, auth_headers):
        """Test bilingual cost estimate output."""
        response = client.get(
            "/api/v1/leveling/cost/FIELD-001",
            params={
                "cut_volume_m3": 1000,
                "fill_volume_m3": 1000,
                "field_area_hectares": 1.0,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Check English summary
        assert "summary_en" in data
        assert "SAR" in data["summary_en"]

        # Check Arabic summary
        assert "summary_ar" in data
        assert "ريال" in data["summary_ar"]

    def test_bilingual_equipment_names(self, client, auth_headers):
        """Test bilingual equipment names."""
        response = client.get(
            "/api/v1/leveling/equipment/FIELD-001",
            params={"total_volume_m3": 3000},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        for equipment in data:
            assert "equipment_name_en" in equipment
            assert "equipment_name_ar" in equipment
            # Verify Arabic name exists
            assert len(equipment["equipment_name_ar"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
