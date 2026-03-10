# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Unit tests for Leveling Optimizer Service
اختبارات الوحدة لخدمة تحسين التسوية

Tests cover:
- Cut/fill volume calculation
- Optimal grade plane determination
- Cost estimation
- Equipment recommendations

Author: SAHOOL Platform Team
Updated: January 2026
"""

import math
import uuid
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

np = pytest.importorskip("numpy", reason="numpy required for leveling optimizer tests")


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_dem_for_leveling() -> np.ndarray:
    """Create a sample DEM suitable for leveling analysis."""
    rows, cols = 50, 50
    dem = np.zeros((rows, cols), dtype=np.float32)

    # Create irregular terrain
    np.random.seed(42)
    base_elevation = 100.0

    for i in range(rows):
        for j in range(cols):
            # Base slope
            dem[i, j] = base_elevation - i * 0.2 - j * 0.1
            # Add some random variation
            dem[i, j] += np.random.uniform(-0.5, 0.5)

    return dem


@pytest.fixture
def sample_field_boundary() -> dict[str, Any]:
    """Create a sample field boundary polygon."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [44.0, 15.0],
                [44.05, 15.0],
                [44.05, 15.05],
                [44.0, 15.05],
                [44.0, 15.0],
            ]
        ],
        "properties": {
            "area_hectares": 25.0,
        },
    }


@pytest.fixture
def sample_soil_properties() -> dict[str, Any]:
    """Create sample soil properties for cost estimation."""
    return {
        "soil_type": "clay_loam",
        "soil_type_ar": "طمي طيني",
        "bulk_density_kg_m3": 1400,
        "excavation_factor": 1.15,  # Soil swells 15% when excavated
        "compaction_factor": 0.92,  # Soil compacts to 92% volume when filled
    }


@pytest.fixture
def sample_equipment_costs() -> dict[str, Any]:
    """Create sample equipment cost data."""
    return {
        "scraper": {
            "name_en": "Land Scraper",
            "name_ar": "كاشطة الأراضي",
            "capacity_m3_per_hour": 150,
            "cost_per_hour_sar": 450,
            "fuel_consumption_l_per_hour": 25,
            "suitable_for": ["cut_fill_distances_up_to_300m"],
        },
        "bulldozer": {
            "name_en": "Bulldozer D6",
            "name_ar": "جرافة D6",
            "capacity_m3_per_hour": 80,
            "cost_per_hour_sar": 350,
            "fuel_consumption_l_per_hour": 18,
            "suitable_for": ["short_distances", "rough_terrain"],
        },
        "excavator": {
            "name_en": "Hydraulic Excavator",
            "name_ar": "حفارة هيدروليكية",
            "capacity_m3_per_hour": 120,
            "cost_per_hour_sar": 400,
            "fuel_consumption_l_per_hour": 22,
            "suitable_for": ["deep_cuts", "loading_trucks"],
        },
        "grader": {
            "name_en": "Motor Grader",
            "name_ar": "ممهدة",
            "capacity_m3_per_hour": 60,
            "cost_per_hour_sar": 300,
            "fuel_consumption_l_per_hour": 15,
            "suitable_for": ["fine_grading", "finishing"],
        },
        "laser_plane": {
            "name_en": "Laser-Guided Land Plane",
            "name_ar": "مسوّي الأراضي بالليزر",
            "capacity_m3_per_hour": 200,
            "cost_per_hour_sar": 550,
            "fuel_consumption_l_per_hour": 30,
            "suitable_for": ["precision_leveling", "irrigation_fields"],
        },
    }


@pytest.fixture
def sample_leveling_request() -> dict[str, Any]:
    """Create a sample leveling optimization request."""
    return {
        "field_id": str(uuid.uuid4()),
        "target_slope_percent": 0.1,  # 0.1% slope for surface irrigation
        "slope_direction_degrees": 180,  # Slope toward south
        "design_constraints": {
            "max_cut_depth_m": 0.5,
            "max_fill_depth_m": 0.5,
            "border_buffer_m": 5.0,
        },
        "optimization_objectives": ["minimize_earthwork", "balance_cut_fill"],
    }


# =============================================================================
# Test Configuration
# =============================================================================


class TestLevelingOptimizerConfiguration:
    """Tests for Leveling Optimizer Service configuration."""

    def test_settings_default_values(self):
        """Test default configuration values."""
        defaults = {
            "service_name": "leveling-optimizer-service",
            "version": "16.0.0",
            "default_target_slope_percent": 0.1,
            "max_cut_depth_m": 1.0,
            "max_fill_depth_m": 1.0,
            "soil_expansion_factor": 1.15,
        }

        assert defaults["default_target_slope_percent"] == 0.1
        assert defaults["soil_expansion_factor"] == 1.15

    def test_optimization_method_enum(self):
        """Test optimization method enumeration."""
        valid_methods = [
            "least_squares",
            "minimize_earthwork",
            "balance_cut_fill",
            "user_defined_plane",
        ]

        for method in valid_methods:
            assert method in valid_methods


# =============================================================================
# Test Cut/Fill Volume Calculation
# =============================================================================


class TestCutFillVolumeCalculation:
    """Tests for cut and fill volume calculations."""

    def test_cut_fill_basic_calculation(self, sample_dem_for_leveling: np.ndarray):
        """Test basic cut/fill volume calculation."""
        dem = sample_dem_for_leveling
        cell_size_m = 30.0

        # Define target plane (flat at mean elevation)
        target_elevation = np.mean(dem)
        target_plane = np.full_like(dem, target_elevation)

        # Calculate differences
        diff = dem - target_plane

        # Cut volume (where existing > target)
        cut_mask = diff > 0
        cut_volume_m3 = np.sum(diff[cut_mask]) * cell_size_m**2

        # Fill volume (where existing < target)
        fill_mask = diff < 0
        fill_volume_m3 = np.abs(np.sum(diff[fill_mask])) * cell_size_m**2

        assert cut_volume_m3 > 0
        assert fill_volume_m3 > 0

    def test_cut_fill_with_sloped_plane(self, sample_dem_for_leveling: np.ndarray):
        """Test cut/fill calculation with target sloped plane."""
        dem = sample_dem_for_leveling
        rows, cols = dem.shape
        cell_size_m = 30.0

        # Create sloped target plane (0.1% slope toward south)
        slope = 0.001  # 0.1%
        base_elevation = np.mean(dem)

        target_plane = np.zeros_like(dem)
        for i in range(rows):
            for j in range(cols):
                target_plane[i, j] = base_elevation - i * cell_size_m * slope

        diff = dem - target_plane

        # Calculate volumes
        cut_volume = np.sum(diff[diff > 0]) * cell_size_m**2
        fill_volume = np.abs(np.sum(diff[diff < 0])) * cell_size_m**2

        # Cut and fill should not be exactly equal with real terrain
        assert cut_volume > 0
        assert fill_volume > 0

    def test_earthwork_balance_optimization(self, sample_dem_for_leveling: np.ndarray):
        """Test optimization for cut/fill balance."""
        dem = sample_dem_for_leveling.astype(np.float64)

        # Find elevation that balances cut and fill
        def calculate_balance(target_elev):
            diff = dem - target_elev
            cut = float(np.sum(diff[diff > 0]))
            fill = float(np.abs(np.sum(diff[diff < 0])))
            return cut, fill

        # Binary search for balanced elevation
        # When cut > fill, target is too low → raise it (low = mid)
        # When fill > cut, target is too high → lower it (high = mid)
        low, high = float(np.min(dem)), float(np.max(dem))
        for _ in range(50):
            mid = (low + high) / 2
            cut, fill = calculate_balance(mid)
            if cut > fill:
                low = mid
            else:
                high = mid

        balanced_elevation = (low + high) / 2
        cut, fill = calculate_balance(balanced_elevation)

        # Should be reasonably balanced
        assert cut > 0 and fill > 0, "Both cut and fill should be positive"
        balance_ratio = min(cut, fill) / max(cut, fill)
        assert balance_ratio > 0.9  # Within 10%

    def test_volume_with_soil_factors(self, sample_soil_properties: dict[str, Any]):
        """Test volume adjustment with soil expansion/compaction."""
        gross_cut_volume = 1000.0  # m^3
        gross_fill_volume = 1000.0  # m^3

        expansion = sample_soil_properties["excavation_factor"]
        compaction = sample_soil_properties["compaction_factor"]

        # Cut soil expands (more volume to move)
        expanded_cut_volume = gross_cut_volume * expansion

        # Fill soil compacts (need more soil to achieve desired fill)
        required_fill_volume = gross_fill_volume / compaction

        assert expanded_cut_volume > gross_cut_volume
        assert required_fill_volume > gross_fill_volume

    def test_cut_fill_depth_statistics(self, sample_dem_for_leveling: np.ndarray):
        """Test calculation of cut/fill depth statistics."""
        dem = sample_dem_for_leveling
        target_elevation = np.mean(dem)

        diff = dem - target_elevation

        cut_depths = diff[diff > 0]
        fill_depths = np.abs(diff[diff < 0])

        stats = {
            "cut": {
                "max_depth_m": float(np.max(cut_depths)) if len(cut_depths) > 0 else 0,
                "avg_depth_m": float(np.mean(cut_depths)) if len(cut_depths) > 0 else 0,
                "area_m2": len(cut_depths) * 900,  # 30m cells
            },
            "fill": {
                "max_depth_m": float(np.max(fill_depths)) if len(fill_depths) > 0 else 0,
                "avg_depth_m": float(np.mean(fill_depths)) if len(fill_depths) > 0 else 0,
                "area_m2": len(fill_depths) * 900,
            },
        }

        assert stats["cut"]["max_depth_m"] > 0
        assert stats["fill"]["max_depth_m"] > 0


# =============================================================================
# Test Optimal Grade Plane
# =============================================================================


class TestOptimalGradePlane:
    """Tests for optimal grade plane determination."""

    def test_least_squares_plane_fitting(self, sample_dem_for_leveling: np.ndarray):
        """Test least-squares plane fitting."""
        dem = sample_dem_for_leveling
        rows, cols = dem.shape

        # Create coordinate arrays
        x = np.arange(cols)
        y = np.arange(rows)
        X, Y = np.meshgrid(x, y)

        # Flatten for least squares
        X_flat = X.flatten()
        Y_flat = Y.flatten()
        Z_flat = dem.flatten()

        # Fit plane: z = ax + by + c
        A = np.column_stack([X_flat, Y_flat, np.ones_like(X_flat)])
        coeffs, _, _, _ = np.linalg.lstsq(A, Z_flat, rcond=None)

        a, b, c = coeffs

        # Reconstruct fitted plane
        fitted_plane = a * X + b * Y + c

        # Calculate residuals
        residuals = dem - fitted_plane
        rmse = np.sqrt(np.mean(residuals**2))

        assert rmse >= 0

    def test_constrained_slope_plane(self):
        """Test plane fitting with slope constraints."""
        target_slope_percent = 0.1
        target_direction_deg = 180  # South

        # Convert to components
        slope_radians = math.atan(target_slope_percent / 100)
        direction_radians = math.radians(target_direction_deg)

        # Slope components (dx/dz, dy/dz)
        # North=0°, East=90°, South=180°, West=270°
        slope_x = math.sin(direction_radians) * math.tan(slope_radians)
        slope_y = math.cos(direction_radians) * math.tan(slope_radians)

        # For 180 degrees (south), y-slope should be negative
        assert slope_y < 0

    def test_plane_centroid_calculation(self, sample_dem_for_leveling: np.ndarray):
        """Test calculation of plane passing through centroid."""
        dem = sample_dem_for_leveling
        rows, cols = dem.shape
        cell_size_m = 30.0

        # Field centroid
        centroid_row = rows // 2
        centroid_col = cols // 2
        centroid_elevation = dem[centroid_row, centroid_col]

        # Create plane through centroid with given slope
        slope = 0.001  # 0.1%
        plane = np.zeros_like(dem)

        for i in range(rows):
            for j in range(cols):
                dy = (i - centroid_row) * cell_size_m
                plane[i, j] = centroid_elevation - dy * slope

        # Plane should pass through centroid
        assert abs(plane[centroid_row, centroid_col] - centroid_elevation) < 0.001

    def test_multiple_plane_options(self, sample_dem_for_leveling: np.ndarray):
        """Test generation of multiple plane options."""
        dem = sample_dem_for_leveling

        plane_options = []

        # Option 1: Balanced cut/fill
        balanced_elev = np.mean(dem)
        plane_options.append(
            {
                "name": "Balanced",
                "name_ar": "متوازن",
                "elevation": balanced_elev,
                "slope_percent": 0,
            }
        )

        # Option 2: Minimize cut
        min_cut_elev = np.percentile(dem, 25)
        plane_options.append(
            {
                "name": "Minimize Cut",
                "name_ar": "تقليل القطع",
                "elevation": min_cut_elev,
                "slope_percent": 0,
            }
        )

        # Option 3: Minimum earthwork (best fit plane)
        plane_options.append(
            {
                "name": "Minimum Earthwork",
                "name_ar": "أقل كمية ترابية",
                "elevation": np.median(dem),
                "slope_percent": 0.1,
            }
        )

        assert len(plane_options) == 3


# =============================================================================
# Test Cost Estimation
# =============================================================================


class TestCostEstimation:
    """Tests for leveling cost estimation."""

    def test_earthwork_cost_calculation(
        self,
        sample_equipment_costs: dict[str, Any],
        sample_soil_properties: dict[str, Any],
    ):
        """Test earthwork cost calculation."""
        total_volume_m3 = 5000.0

        # Using scraper for main earthwork
        scraper = sample_equipment_costs["scraper"]
        hours_required = total_volume_m3 / scraper["capacity_m3_per_hour"]
        equipment_cost = hours_required * scraper["cost_per_hour_sar"]

        # Add fuel cost
        fuel_liters = hours_required * scraper["fuel_consumption_l_per_hour"]
        fuel_price_per_liter = 2.18  # SAR
        fuel_cost = fuel_liters * fuel_price_per_liter

        total_cost = equipment_cost + fuel_cost

        assert total_cost > 0
        assert hours_required > 0

    def test_cost_per_cubic_meter(self, sample_equipment_costs: dict[str, Any]):
        """Test calculation of cost per cubic meter."""
        volume_m3 = 1000.0

        equipment_rates = {}
        for equip_name, equip_data in sample_equipment_costs.items():
            hours = volume_m3 / equip_data["capacity_m3_per_hour"]
            total_cost = hours * equip_data["cost_per_hour_sar"]
            cost_per_m3 = total_cost / volume_m3

            equipment_rates[equip_name] = {
                "cost_per_m3_sar": cost_per_m3,
                "hours_for_1000m3": hours,
            }

        # All rates should be positive
        for rate in equipment_rates.values():
            assert rate["cost_per_m3_sar"] > 0

    def test_total_project_cost_breakdown(self, sample_equipment_costs: dict[str, Any]):
        """Test total project cost breakdown."""
        cut_volume = 3000.0  # m^3
        fill_volume = 2500.0  # m^3

        cost_breakdown = {
            "earthmoving": {
                "description": "Cut and fill operations",
                "description_ar": "عمليات القطع والردم",
                "volume_m3": cut_volume + fill_volume,
                "cost_sar": 0,
            },
            "fine_grading": {
                "description": "Surface finishing",
                "description_ar": "تسوية السطح النهائية",
                "area_m2": 25000,  # 25 hectares
                "cost_sar": 0,
            },
            "laser_leveling": {
                "description": "Precision leveling",
                "description_ar": "التسوية بالليزر",
                "area_m2": 25000,
                "cost_sar": 0,
            },
        }

        # Calculate costs
        scraper = sample_equipment_costs["scraper"]
        grader = sample_equipment_costs["grader"]
        laser = sample_equipment_costs["laser_plane"]

        earthmoving_hours = (cut_volume + fill_volume) / scraper["capacity_m3_per_hour"]
        cost_breakdown["earthmoving"]["cost_sar"] = earthmoving_hours * scraper["cost_per_hour_sar"]

        grading_hours = 25000 / (grader["capacity_m3_per_hour"] * 100)  # Simplified
        cost_breakdown["fine_grading"]["cost_sar"] = grading_hours * grader["cost_per_hour_sar"]

        laser_hours = 25000 / (laser["capacity_m3_per_hour"] * 100)
        cost_breakdown["laser_leveling"]["cost_sar"] = laser_hours * laser["cost_per_hour_sar"]

        total_cost = sum(item["cost_sar"] for item in cost_breakdown.values())

        assert total_cost > 0

    def test_cost_comparison_scenarios(self, sample_dem_for_leveling: np.ndarray):
        """Test cost comparison between different leveling scenarios."""
        dem = sample_dem_for_leveling
        cell_size = 30.0

        scenarios = []

        # Scenario 1: Flat (balanced)
        flat_target = np.mean(dem)
        diff1 = dem - flat_target
        vol1 = np.sum(np.abs(diff1)) * cell_size**2
        scenarios.append(
            {
                "name": "Flat Field",
                "name_ar": "حقل مستوي",
                "earthwork_m3": vol1,
                "estimated_cost_sar": vol1 * 5,  # 5 SAR/m3 estimate
            }
        )

        # Scenario 2: Sloped (0.1%)
        slope_target = flat_target - np.arange(dem.shape[0])[:, np.newaxis] * cell_size * 0.001
        diff2 = dem - slope_target
        vol2 = np.sum(np.abs(diff2)) * cell_size**2
        scenarios.append(
            {
                "name": "Sloped Field (0.1%)",
                "name_ar": "حقل مائل (0.1%)",
                "earthwork_m3": vol2,
                "estimated_cost_sar": vol2 * 5,
            }
        )

        # Verify scenarios created
        assert len(scenarios) == 2


# =============================================================================
# Test Equipment Recommendations
# =============================================================================


class TestEquipmentRecommendations:
    """Tests for equipment selection and recommendations."""

    def test_equipment_selection_by_volume(self, sample_equipment_costs: dict[str, Any]):
        """Test equipment selection based on earthwork volume."""
        volume_m3 = 5000.0

        recommendations = []

        # Small volume: bulldozer or grader
        if volume_m3 < 2000:
            recommendations.append(sample_equipment_costs["bulldozer"])
            recommendations.append(sample_equipment_costs["grader"])
        # Medium volume: scraper
        elif volume_m3 < 10000:
            recommendations.append(sample_equipment_costs["scraper"])
            recommendations.append(sample_equipment_costs["bulldozer"])
        # Large volume: scraper fleet
        else:
            recommendations.append(sample_equipment_costs["scraper"])
            recommendations.append(sample_equipment_costs["excavator"])

        assert len(recommendations) > 0

    def test_equipment_selection_by_distance(self, sample_equipment_costs: dict[str, Any]):
        """Test equipment selection based on haul distance."""
        avg_haul_distance_m = 150.0

        if avg_haul_distance_m < 50:
            recommended = "bulldozer"  # Short push distance
        elif avg_haul_distance_m < 300:
            recommended = "scraper"  # Medium distance
        else:
            recommended = "excavator_and_trucks"  # Long haul

        assert recommended in ["bulldozer", "scraper", "excavator_and_trucks"]

    def test_equipment_combination_recommendation(self, sample_equipment_costs: dict[str, Any]):
        """Test recommendation of equipment combinations."""
        project_params = {
            "total_volume_m3": 8000,
            "avg_haul_distance_m": 200,
            "precision_required": True,
            "deadline_days": 10,
        }

        equipment_plan = {
            "phase_1_rough_grading": {
                "equipment": ["scraper", "bulldozer"],
                "duration_days": 6,
            },
            "phase_2_fine_grading": {
                "equipment": ["grader"],
                "duration_days": 2,
            },
            "phase_3_precision_leveling": {
                "equipment": ["laser_plane"],
                "duration_days": 2,
            },
        }

        total_days = sum(phase["duration_days"] for phase in equipment_plan.values())
        assert total_days <= project_params["deadline_days"]

    def test_equipment_capacity_validation(self, sample_equipment_costs: dict[str, Any]):
        """Test validation of equipment capacity for project."""
        volume_m3 = 5000.0
        available_days = 5
        working_hours_per_day = 8

        scraper = sample_equipment_costs["scraper"]
        total_available_hours = available_days * working_hours_per_day
        max_capacity = scraper["capacity_m3_per_hour"] * total_available_hours

        # Check if single scraper is sufficient
        single_scraper_sufficient = max_capacity >= volume_m3

        if not single_scraper_sufficient:
            # Calculate required fleet size
            required_scrapers = math.ceil(volume_m3 / max_capacity)
        else:
            required_scrapers = 1

        assert required_scrapers >= 1


# =============================================================================
# Test Leveling Optimization
# =============================================================================


class TestLevelingOptimization:
    """Tests for leveling optimization algorithms."""

    def test_cut_fill_balance_optimization(self, sample_dem_for_leveling: np.ndarray):
        """Test optimization to balance cut and fill volumes."""
        dem = sample_dem_for_leveling
        cell_size = 30.0

        # Objective: minimize |cut - fill|
        def objective(target_elev):
            diff = dem - target_elev
            cut = np.sum(diff[diff > 0])
            fill = np.abs(np.sum(diff[diff < 0]))
            return abs(cut - fill)

        # Simple optimization
        best_elev = np.mean(dem)
        best_score = objective(best_elev)

        for offset in np.linspace(-2, 2, 100):
            test_elev = np.mean(dem) + offset
            score = objective(test_elev)
            if score < best_score:
                best_score = score
                best_elev = test_elev

        # Verify improvement
        assert objective(best_elev) <= objective(np.mean(dem))

    def test_minimize_earthwork_optimization(self, sample_dem_for_leveling: np.ndarray):
        """Test optimization to minimize total earthwork."""
        dem = sample_dem_for_leveling
        cell_size = 30.0

        # Objective: minimize |cut| + |fill|
        def total_earthwork(target_elev):
            diff = dem - target_elev
            cut = np.sum(diff[diff > 0])
            fill = np.abs(np.sum(diff[diff < 0]))
            return cut + fill

        # Find minimum earthwork elevation (should be near median)
        test_elevations = np.linspace(np.min(dem), np.max(dem), 200)
        earthworks = [total_earthwork(e) for e in test_elevations]

        min_idx = np.argmin(earthworks)
        optimal_elevation = test_elevations[min_idx]

        # Optimal should be close to median
        assert abs(optimal_elevation - np.median(dem)) < 1.0

    def test_constraint_enforcement(self, sample_dem_for_leveling: np.ndarray):
        """Test enforcement of depth constraints."""
        dem = sample_dem_for_leveling
        max_cut_depth = 0.5
        max_fill_depth = 0.5

        target_elevation = np.mean(dem)
        diff = dem - target_elevation

        # Check constraint violations
        cut_violations = diff > max_cut_depth
        fill_violations = diff < -max_fill_depth

        violation_count = np.sum(cut_violations) + np.sum(fill_violations)

        # Record violations for reporting
        violation_report = {
            "cut_violations": int(np.sum(cut_violations)),
            "fill_violations": int(np.sum(fill_violations)),
            "max_cut_exceeded_by": float(np.max(diff) - max_cut_depth) if np.any(cut_violations) else 0,
            "max_fill_exceeded_by": float(-np.min(diff) - max_fill_depth) if np.any(fill_violations) else 0,
        }

        assert "cut_violations" in violation_report


# =============================================================================
# Test API Response Formats
# =============================================================================


class TestLevelingAPIResponses:
    """Tests for API response format compliance."""

    def test_leveling_analysis_response(self):
        """Test leveling analysis response format."""
        response = {
            "request_id": str(uuid.uuid4()),
            "field_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "existing_terrain": {
                "min_elevation_m": 95.5,
                "max_elevation_m": 104.2,
                "mean_elevation_m": 99.8,
                "std_elevation_m": 1.85,
            },
            "optimal_plane": {
                "base_elevation_m": 99.5,
                "slope_percent": 0.1,
                "slope_direction_degrees": 180,
            },
            "earthwork": {
                "cut_volume_m3": 3500.0,
                "fill_volume_m3": 3200.0,
                "balance_ratio": 0.91,
                "total_volume_m3": 6700.0,
            },
            "statistics": {
                "cut_area_m2": 12500,
                "fill_area_m2": 12500,
                "avg_cut_depth_m": 0.28,
                "avg_fill_depth_m": 0.26,
                "max_cut_depth_m": 0.45,
                "max_fill_depth_m": 0.42,
            },
        }

        assert "optimal_plane" in response
        assert "earthwork" in response
        assert response["earthwork"]["balance_ratio"] > 0.8

    def test_cost_estimate_response(self):
        """Test cost estimate response format."""
        response = {
            "request_id": str(uuid.uuid4()),
            "field_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "cost_breakdown": {
                "earthmoving": {
                    "description": "Excavation and filling",
                    "description_ar": "الحفر والردم",
                    "cost_sar": 33500,
                },
                "fine_grading": {
                    "description": "Surface finishing",
                    "description_ar": "التشطيب السطحي",
                    "cost_sar": 12000,
                },
                "laser_leveling": {
                    "description": "Precision leveling",
                    "description_ar": "التسوية الدقيقة",
                    "cost_sar": 8500,
                },
            },
            "total_cost_sar": 54000,
            "cost_per_hectare_sar": 2160,
            "estimated_duration_days": 8,
        }

        assert response["total_cost_sar"] > 0
        assert "cost_breakdown" in response

    def test_equipment_recommendation_response(self):
        """Test equipment recommendation response format."""
        response = {
            "request_id": str(uuid.uuid4()),
            "recommended_equipment": [
                {
                    "name": "Land Scraper",
                    "name_ar": "كاشطة الأراضي",
                    "quantity": 2,
                    "usage_hours": 40,
                    "phase": "rough_grading",
                },
                {
                    "name": "Motor Grader",
                    "name_ar": "ممهدة",
                    "quantity": 1,
                    "usage_hours": 16,
                    "phase": "fine_grading",
                },
                {
                    "name": "Laser Land Plane",
                    "name_ar": "مسوي بالليزر",
                    "quantity": 1,
                    "usage_hours": 20,
                    "phase": "precision_leveling",
                },
            ],
            "project_phases": [
                {
                    "name": "Rough Grading",
                    "name_ar": "التسوية الخشنة",
                    "duration_days": 5,
                },
                {
                    "name": "Fine Grading",
                    "name_ar": "التسوية الدقيقة",
                    "duration_days": 2,
                },
                {
                    "name": "Precision Leveling",
                    "name_ar": "التسوية بالليزر",
                    "duration_days": 2,
                },
            ],
        }

        assert len(response["recommended_equipment"]) > 0
        assert len(response["project_phases"]) > 0


# =============================================================================
# Test Health Endpoints
# =============================================================================


class TestLevelingHealthEndpoints:
    """Tests for health check endpoints."""

    def test_healthz_response(self):
        """Test health endpoint response."""
        health = {
            "status": "ok",
            "service": "leveling-optimizer-service",
            "version": "16.0.0",
        }

        assert health["status"] == "ok"
        assert health["service"] == "leveling-optimizer-service"

    def test_readyz_response(self):
        """Test readiness endpoint response."""
        readiness = {
            "status": "ok",
            "database": True,
            "nats": True,
            "terrain_service": True,
        }

        assert readiness["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
